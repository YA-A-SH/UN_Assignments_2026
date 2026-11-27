
import sys

import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
results = [] 
def show(label, response, expected):
      ok = response.status_code == expected
    results.append(ok)
    body = response.text if response.content else "(no body)"
    if len(body) > 110:
        body = body[:107] + "..."
    verdict = "OK" if ok else "MISMATCH"
    print(f"{label:<48} -> {response.status_code} (expected {expected}) {verdict}")
    print(f"      {body}")


def booking(room_id="B205", date="2026-12-01", start=10, end=12, purpose="Study group"):
    return {"room_id": room_id, "date": date, "start_hour": start,
            "end_hour": end, "purpose": purpose}


def run(c):
    print("== 1. Rooms ==")
    show("POST /rooms (B205)", c.post("/rooms", json={
        "id": "B205", "building": "Science Building", "capacity": 30}), 201)
    show("POST /rooms (B207)", c.post("/rooms", json={
        "id": "B207", "building": "Science Building", "capacity": 12}), 201)
    show("POST /rooms (B205 again)", c.post("/rooms", json={
        "id": "B205", "building": "Science Building", "capacity": 30}), 409)
    show("POST /rooms (invalid: capacity 0, empty building)", c.post("/rooms", json={
        "id": "X1", "building": "", "capacity": 0}), 422)
    show("GET /rooms", c.get("/rooms"), 200)
    show("GET /rooms/B205", c.get("/rooms/B205"), 200)
    show("GET /rooms/Z999 (unknown room)", c.get("/rooms/Z999"), 404)

    print("\n== 2. Bookings: success cases ==")
    show("PUT /bookings/bk-001 (B205, 10-12)",
         c.put("/bookings/bk-001", json=booking()), 201)
    show("PUT /bookings/bk-002 (B205, 12-13, adjacent)",
         c.put("/bookings/bk-002", json=booking(start=12, end=13)), 201)
    show("PUT /bookings/bk-003 (B207, 10-12, other room)",
         c.put("/bookings/bk-003", json=booking(room_id="B207")), 201)
    show("PUT /bookings/bk-004 (B205, other day)",
         c.put("/bookings/bk-004", json=booking(date="2026-12-02")), 201)
    show("GET /bookings/bk-001", c.get("/bookings/bk-001"), 200)
    show("GET /bookings?room_id=B205&date=2026-12-01",
         c.get("/bookings", params={"room_id": "B205", "date": "2026-12-01"}), 200)

    print("\n== 3. Bookings: error cases ==")
    show("PUT /bookings/bk-005 (B205, 11-13, overlap)",
         c.put("/bookings/bk-005", json=booking(start=11, end=13)), 409)
    show("PUT /bookings/bk-006 (B205, 10-11, inside bk-001)",
         c.put("/bookings/bk-006", json=booking(start=10, end=11)), 409)
    show("PUT /bookings/bk-001 (same id, different data)",
         c.put("/bookings/bk-001", json=booking(start=14, end=16)), 409)
    show("PUT /bookings/bk-007 (unknown room Z999)",
         c.put("/bookings/bk-007", json=booking(room_id="Z999")), 404)
    show("GET /bookings/bk-999 (unknown booking)", c.get("/bookings/bk-999"), 404)
    show("DELETE /bookings/bk-999 (unknown booking)", c.delete("/bookings/bk-999"), 404)
    show("PUT /bookings/bk-008 (end before start)",
         c.put("/bookings/bk-008", json=booking(start=12, end=10)), 422)
    show("PUT /bookings/bk-009 (start hour 7, before 8:00)",
         c.put("/bookings/bk-009", json=booking(start=7, end=9)), 422)
    show("PUT /bookings/bk-010 (end hour 21, after 20:00)",
         c.put("/bookings/bk-010", json=booking(start=19, end=21)), 422)
    bad = booking()
    del bad["purpose"]
    show("PUT /bookings/bk-011 (purpose missing)", c.put("/bookings/bk-011", json=bad), 422)
    show("PUT /bookings/bk-012 (date 2026-13-45)",
         c.put("/bookings/bk-012", json=booking(date="2026-13-45")), 422)
    show("PUT /bookings/ab (booking id too short)",
         c.put("/bookings/ab", json=booking()), 422)

    print("\n== 4. Delete frees the time slot ==")
    show("DELETE /bookings/bk-004", c.delete("/bookings/bk-004"), 204)
    show("GET /bookings/bk-004 (after delete)", c.get("/bookings/bk-004"), 404)
    show("PUT /bookings/bk-013 (B205, 2026-12-02, 10-12)",
         c.put("/bookings/bk-013", json=booking(date="2026-12-02")), 201)

    print("\n== 5. Retry safety: the same PUT sent twice ==")
    retry = booking(room_id="B207", date="2026-12-03", start=13, end=15,
                    purpose="Retry demo")
    show("PUT /bookings/bk-retry (attempt 1)", c.put("/bookings/bk-retry", json=retry), 201)
    show("PUT /bookings/bk-retry (attempt 2, same data)",
         c.put("/bookings/bk-retry", json=retry), 200)
    found = c.get("/bookings", params={"room_id": "B207", "date": "2026-12-03"}).json()
    ok = len(found) == 1
    results.append(ok)
    print(f"Bookings of B207 on 2026-12-03 after two PUTs: {len(found)} "
          f"(expected 1) {'OK' if ok else 'MISMATCH'}")


try:
    with httpx.Client(base_url=base, timeout=5.0) as client:
        run(client)
except httpx.ConnectError:
    print(f"Cannot reach the service at {base}. Start it first with:")
    print("    uvicorn bookings_service:app --port 8000")
    sys.exit(1)

print(f"\n{sum(results)} of {len(results)} checks gave the expected result.")
sys.exit(0 if all(results) else 1)
