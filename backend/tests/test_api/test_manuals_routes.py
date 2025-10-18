"""
Tests for manuals API routes
"""
import pytest
import io
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestManualsAPI:
    """Test manual management API endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_list_manuals_empty(self, test_client):
        """Test listing manuals when none uploaded"""
        response = test_client.get("/api/manuals/")
        assert response.status_code == 200
        data = response.json()
        assert "manuals" in data
        assert "total_count" in data
        assert isinstance(data["manuals"], list)

    def test_process_manual_invalid_file_type(self, test_client):
        """Test uploading non-PDF file returns error"""
        # Create a fake text file
        file_content = b"This is not a PDF"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        response = test_client.post("/api/manuals/process", files=files)
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_process_manual_with_valid_pdf(self, test_client, temp_pdf_file):
        """Test processing a valid PDF file"""
        with open(temp_pdf_file, 'rb') as f:
            files = {"file": ("Moog-Minimoog.pdf", f, "application/pdf")}
            response = test_client.post("/api/manuals/process", files=files)

        # Should return 200 with pending manual data
        assert response.status_code == 200
        data = response.json()
        assert "original_filename" in data
        assert "metadata" in data
        assert data["original_filename"] == "Moog-Minimoog.pdf"

    def test_save_manual_not_found(self, test_client):
        """Test saving non-existent pending manual returns error"""
        payload = {
            "filename": "nonexistent.pdf",
            "display_name": "Test Manual",
            "manufacturer": "Test",
            "model": "T-100",
            "instrument_type": "synthesizer"
        }

        response = test_client.post("/api/manuals/save", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_manual_not_found(self, test_client):
        """Test deleting non-existent manual"""
        response = test_client.delete("/api/manuals/nonexistent.pdf")
        # Should still return 200 but success=false
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False


@pytest.mark.integration
class TestStatsAPI:
    """Test statistics API endpoints"""

    def test_get_stats(self, test_client):
        """Test getting database statistics"""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_manuals" in data
        assert "total_chunks" in data
        assert "manufacturers" in data
        assert "instrument_types" in data
        assert isinstance(data["manufacturers"], list)

    def test_get_manufacturers_filter(self, test_client):
        """Test getting manufacturers filter"""
        response = test_client.get("/api/filters/manufacturers")
        assert response.status_code == 200
        data = response.json()
        assert "manufacturers" in data
        assert isinstance(data["manufacturers"], list)

    def test_get_instrument_types_filter(self, test_client):
        """Test getting instrument types filter"""
        response = test_client.get("/api/filters/instrument-types")
        assert response.status_code == 200
        data = response.json()
        assert "instrument_types" in data
        assert isinstance(data["instrument_types"], list)
