import pytest
from fastapi.testclient import TestClient

from app.database import bookings, hotels, users
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    users.clear()
    hotels.clear()
    bookings.clear()
    yield
    users.clear()
    hotels.clear()
    bookings.clear()


def _register(login="testuser", password="pass1234", first_name="Ivan", last_name="Petrov"):
    return client.post("/api/auth/register", json={
        "login": login, "password": password,
        "first_name": first_name, "last_name": last_name,
        "email": f"{login}@example.com",
    })


def _login(login="testuser", password="pass1234"):
    resp = client.post("/api/auth/login", json={"login": login, "password": password})
    return resp.json()["access_token"]


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


# ---- Auth tests ----

class TestAuth:
    def test_register_success(self):
        resp = _register()
        assert resp.status_code == 201
        data = resp.json()
        assert data["login"] == "testuser"
        assert data["first_name"] == "Ivan"

    def test_register_duplicate_login(self):
        _register()
        resp = _register()
        assert resp.status_code == 409

    def test_login_success(self):
        _register()
        resp = client.post("/api/auth/login", json={"login": "testuser", "password": "pass1234"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self):
        _register()
        resp = client.post("/api/auth/login", json={"login": "testuser", "password": "wrong"})
        assert resp.status_code == 401


# ---- User tests ----

class TestUsers:
    def test_search_by_login(self):
        _register()
        token = _login()
        resp = client.get("/api/users/search?login=testuser", headers=_auth_header(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_by_name(self):
        _register()
        token = _login()
        resp = client.get("/api/users/search?name=Ivan", headers=_auth_header(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_no_params(self):
        _register()
        token = _login()
        resp = client.get("/api/users/search", headers=_auth_header(token))
        assert resp.status_code == 400

    def test_search_unauthorized(self):
        resp = client.get("/api/users/search?login=test")
        assert resp.status_code in (401, 403)


# ---- Hotel tests ----

class TestHotels:
    def test_create_hotel(self):
        _register()
        token = _login()
        resp = client.post("/api/hotels", json={
            "name": "Grand Hotel", "city": "Moscow",
            "address": "Tverskaya 1", "stars": 5,
            "rooms_total": 100, "price_per_night": 5000.0,
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["name"] == "Grand Hotel"

    def test_list_hotels(self):
        _register()
        token = _login()
        client.post("/api/hotels", json={
            "name": "Hotel A", "city": "Moscow",
            "address": "A st", "stars": 3,
            "rooms_total": 50, "price_per_night": 3000.0,
        }, headers=_auth_header(token))
        resp = client.get("/api/hotels")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_by_city(self):
        _register()
        token = _login()
        client.post("/api/hotels", json={
            "name": "H1", "city": "Moscow",
            "address": "A1", "stars": 3,
            "rooms_total": 10, "price_per_night": 2000.0,
        }, headers=_auth_header(token))
        client.post("/api/hotels", json={
            "name": "H2", "city": "Saint Petersburg",
            "address": "A2", "stars": 4,
            "rooms_total": 20, "price_per_night": 4000.0,
        }, headers=_auth_header(token))
        resp = client.get("/api/hotels/search?city=moscow")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_hotel_not_found(self):
        resp = client.get("/api/hotels/nonexistent")
        assert resp.status_code == 404

    def test_create_hotel_unauthorized(self):
        resp = client.post("/api/hotels", json={
            "name": "H", "city": "C", "address": "A",
            "stars": 3, "rooms_total": 10, "price_per_night": 1000.0,
        })
        assert resp.status_code in (401, 403)


# ---- Booking tests ----

class TestBookings:
    def _setup(self):
        _register()
        token = _login()
        resp = client.post("/api/hotels", json={
            "name": "Test Hotel", "city": "Moscow",
            "address": "Test st 1", "stars": 4,
            "rooms_total": 50, "price_per_night": 3000.0,
        }, headers=_auth_header(token))
        hotel_id = resp.json()["id"]
        return token, hotel_id

    def test_create_booking(self):
        token, hotel_id = self._setup()
        resp = client.post("/api/bookings", json={
            "hotel_id": hotel_id,
            "check_in": "2026-06-01",
            "check_out": "2026-06-05",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_price"] == 12000.0
        assert data["status"] == "confirmed"

    def test_create_booking_invalid_dates(self):
        token, hotel_id = self._setup()
        resp = client.post("/api/bookings", json={
            "hotel_id": hotel_id,
            "check_in": "2026-06-05",
            "check_out": "2026-06-01",
        }, headers=_auth_header(token))
        assert resp.status_code == 400

    def test_get_my_bookings(self):
        token, hotel_id = self._setup()
        client.post("/api/bookings", json={
            "hotel_id": hotel_id,
            "check_in": "2026-06-01",
            "check_out": "2026-06-03",
        }, headers=_auth_header(token))
        resp = client.get("/api/bookings/my", headers=_auth_header(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_cancel_booking(self):
        token, hotel_id = self._setup()
        resp = client.post("/api/bookings", json={
            "hotel_id": hotel_id,
            "check_in": "2026-07-01",
            "check_out": "2026-07-03",
        }, headers=_auth_header(token))
        booking_id = resp.json()["id"]
        resp = client.delete(f"/api/bookings/{booking_id}", headers=_auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["detail"] == "Booking cancelled"

    def test_cancel_already_cancelled(self):
        token, hotel_id = self._setup()
        resp = client.post("/api/bookings", json={
            "hotel_id": hotel_id,
            "check_in": "2026-08-01",
            "check_out": "2026-08-03",
        }, headers=_auth_header(token))
        booking_id = resp.json()["id"]
        client.delete(f"/api/bookings/{booking_id}", headers=_auth_header(token))
        resp = client.delete(f"/api/bookings/{booking_id}", headers=_auth_header(token))
        assert resp.status_code == 400

    def test_booking_not_found(self):
        _register()
        token = _login()
        resp = client.get("/api/bookings/nonexistent", headers=_auth_header(token))
        assert resp.status_code == 404

    def test_booking_unauthorized(self):
        resp = client.post("/api/bookings", json={
            "hotel_id": "x", "check_in": "2026-06-01", "check_out": "2026-06-03",
        })
        assert resp.status_code in (401, 403)
