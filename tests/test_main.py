"""Test the main module of the application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMain:
    """Test the main module of the application."""

    def test_read_root(self) -> None:
        """Test the root route."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/html; charset=utf-8"

    def test_static_files(self) -> None:
        """Test the static files route."""
        response = client.get("/static/css/main.css")
        assert response.status_code == 200

    def test_home_route(self) -> None:
        """Test the home route with delta=0."""
        response = client.get("/?delta=0")
        assert response.status_code == 200
