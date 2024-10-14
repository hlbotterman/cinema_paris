"""Test the routes of the application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRoutes:
    """Test the routes of the application."""

    def test_home_route_default(self) -> None:
        """Testt the home route."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_route_with_delta(self) -> None:
        """Test the home route with a delta."""
        response = client.get("/?delta=2")
        assert response.status_code == 200
