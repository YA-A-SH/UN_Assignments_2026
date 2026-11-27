# Lab Assignment 2: Campus Room Booking Service


A REST service (FastAPI + Pydantic) for booking university rooms. The rule that
matters: two bookings of the same room on the same day never overlap. A booking
from 10 to 12 and another from 12 to 13 do **not** overlap.

## Files

| File | Purpose |
|------|---------|
| `bookings_service.py` | The FastAPI service |
| `test_bookings.py` | httpx client that shows every success and error case |
| `README.md` | API table, client output, explanation of the retry design |

## How to run

From the `lab2-assignment` folder, with the virtual environment active:

```
uvicorn bookings_service:app --reload --port 8000
```

In a second terminal (restart the service before each run, the data is kept in memory):

```
python test_bookings.py http://localhost:8000
```

Interactive documentation: http://localhost:8000/docs

## 1. API design

Resources: **rooms** (`/rooms/{room_id}`) and **bookings** (`/bookings/{booking_id}`).
A booking has the fields `room_id`, `date` (YYYY-MM-DD), `start_hour` (8 to 19),
`end_hour` (9 to 20, greater than `start_hour`) and `purpose`.

| # | Method | URI | Request body | Success | Error codes |
|---|--------|-----|--------------|---------|-------------|
| 1 | POST | `/rooms` | `{"id": "B205", "building": "Science Building", "capacity": 30}` | 201 | 409 room id already exists; 422 invalid data |
| 2 | GET | `/rooms` | none | 200 | none |
| 3 | GET | `/rooms/{room_id}` | none | 200 | 404 unknown room |
| 4 | PUT | `/bookings/{booking_id}` | `{"room_id": "B205", "date": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study group"}` | 201 created; 200 same request repeated (retry) | 404 unknown room; 409 overlaps an existing booking; 409 booking id already used with different data; 422 invalid data or invalid id |
| 5 | GET | `/bookings` (optional `?room_id=B205&date=2026-12-01`) | none | 200 | 422 invalid date in the query |
| 6 | GET | `/bookings/{booking_id}` | none | 200 | 404 unknown booking |
| 7 | DELETE | `/bookings/{booking_id}` | none | 204 | 404 unknown booking |

Design notes:

- The booking id is chosen by the **client** and sent in the URI, so a booking is
  created with `PUT` and not with `POST` (see step 4).
- Bookings are not edited in place. To change a booking, delete it and create a new one.
- Status codes: 422 is produced by Pydantic (and FastAPI) for invalid data,
  404 for an unknown room or booking, 409 for a conflict with the current state.

## 2. Implementation

- **Validation (422):** `Field(ge=..., le=...)` limits the hours to 8-20, `min_length`
  is used for text fields, and a `model_validator` rejects `end_hour <= start_hour`.
  The service code never checks these rules itself; Pydantic rejects the request
  before the function runs.
- **Overlap check (409):** two bookings of the same room and the same date overlap when
  `new.start < old.end and old.start < new.end`. With this formula 10-12 and 12-13
  do not overlap (`12 < 12` is false).
- **Unknown room or booking (404):** checked with a dictionary lookup.
- **Lock:** a `threading.Lock` makes "check the overlap, then store the booking" one
  atomic step, so two simultaneous requests cannot both take the same slot.

## 3. Output of `test_bookings.py`

> PASTE HERE the real output of `python test_bookings.py http://localhost:8000`
> (run it against a freshly started service), inside a code block.

## 4. Making booking creation safe to retry

**The problem.** The app sends a booking, the service creates it, but the reply is
lost on the way back. The app does not know whether the booking exists, so it sends
the same request again. If creation were a `POST /bookings` where the server invents
a new id for every request, the second request would create a **second booking**
(or fail with a confusing 409 against the first copy).

**The design.** The client chooses the booking id (for example a UUID it generates
once for this booking) and sends `PUT /bookings/{booking_id}`. The service handles
the request like this:

| Situation | Result |
|-----------|--------|
| The id is new and the slot is free | 201, the booking is created |
| The id already exists with exactly the same data (a retry) | 200, the existing booking is returned, nothing new is created |
| The id already exists with different data | 409, the id is already used by another booking |
| The id is new but the slot overlaps another booking | 409 overlap |

The overlap check is done only for new ids. A retried request is recognized by its
id first, so it never conflicts with the booking it created itself.

**Why it works.** `PUT` is idempotent: sending the same request once or ten times
leaves the server in the same state. The id in the URI is the identity of the
booking, so the same request always points at the same booking. The status code may
differ (201 the first time, 200 on the retry) but the state of the server is the same.

**Proof.** Section 5 of the client output sends `PUT /bookings/bk-retry` twice with the
same data. The first call returns 201, the second returns 200, and a `GET /bookings`
for that room and date shows exactly one booking.
