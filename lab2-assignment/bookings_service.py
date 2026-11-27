
import datetime
import threading
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, Field, model_validator

OPEN_HOUR = 8    
CLOSE_HOUR = 20 

app = FastAPI(title="Campus Room Booking Service")


class Room(BaseModel):
    id: str = Field(min_length=2, max_length=10, pattern=r"^[A-Za-z0-9]+$",
                    examples=["B205"])
    building: str = Field(min_length=1, examples=["Science Building"])
    capacity: int = Field(ge=1, examples=[30])


class BookingData(BaseModel):
    room_id: str = Field(min_length=2, max_length=10, examples=["B205"])
    date: datetime.date = Field(examples=["2026-12-01"])
    start_hour: int = Field(ge=OPEN_HOUR, le=CLOSE_HOUR - 1, examples=[10])
    end_hour: int = Field(ge=OPEN_HOUR + 1, le=CLOSE_HOUR, examples=[12])
    purpose: str = Field(min_length=3, max_length=200, examples=["Study group"])

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self


class Booking(BookingData):
    id: str


BookingId = Annotated[str, Path(min_length=3, max_length=64,
                                pattern=r"^[A-Za-z0-9_-]+$")]
rooms: dict[str, Room] = {}
bookings: dict[str, Booking] = {}
lock = threading.Lock() 


def overlaps(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return start_a < end_b and start_b < end_a


@app.post("/rooms", status_code=201)
def create_room(room: Room) -> Room:
    with lock:
        if room.id in rooms:
            raise HTTPException(status_code=409, detail=f"Room {room.id} already exists")
        rooms[room.id] = room
    return room


@app.get("/rooms")
def list_rooms() -> list[Room]:
    return list(rooms.values())


@app.get("/rooms/{room_id}")
def get_room(room_id: str) -> Room:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return rooms[room_id]

@app.put("/bookings/{booking_id}", status_code=201)
def create_booking(booking_id: BookingId, data: BookingData,
                   response: Response) -> Booking:
   
    with lock:
        if data.room_id not in rooms:
            raise HTTPException(status_code=404, detail=f"Room {data.room_id} not found")

        existing = bookings.get(booking_id)
        if existing is not None:
            if existing.model_dump(exclude={"id"}) == data.model_dump():
                response.status_code = 200  
                return existing
            raise HTTPException(
                status_code=409,
                detail=f"Booking id {booking_id} is already used by a different booking")
         for other in bookings.values():
            if (other.room_id == data.room_id and other.date == data.date
                    and overlaps(data.start_hour, data.end_hour,
                                 other.start_hour, other.end_hour)):
                raise HTTPException(
                    status_code=409,
                    detail=(f"Overlaps booking {other.id} "
                            f"({other.start_hour}:00-{other.end_hour}:00)"))

        booking = Booking(id=booking_id, **data.model_dump())
        bookings[booking_id] = booking
    return booking


@app.get("/bookings")
def list_bookings(room_id: str | None = None,
                  date: datetime.date | None = None) -> list[Booking]:
    """All bookings, optionally filtered by ?room_id=...&date=YYYY-MM-DD."""
    result = [b for b in bookings.values()
              if (room_id is None or b.room_id == room_id)
              and (date is None or b.date == date)]
    return sorted(result, key=lambda b: (b.date, b.room_id, b.start_hour))


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str) -> Booking:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return bookings[booking_id]


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str) -> Response:
    with lock:
        if booking_id not in bookings:
            raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
        del bookings[booking_id]
    return Response(status_code=204)
