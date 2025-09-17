"""
Tests for FastAPI endpoints and API functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import json
from io import BytesIO

class TestHealthEndpoints:
    """Test health check and status endpoints"""
    
    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_api_info(self, test_client):
        """Test API info endpoint"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_title" in data
        assert "version" in data

class TestVehicleEndpoints:
    """Test vehicle-related endpoints"""
    
    def test_create_vehicle_success(self, test_client, sample_vehicle_data):
        """Test successful vehicle creation"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.insert_one.return_value = Mock(inserted_id="test_id")
            mock_col.find_one.return_value = None  # No existing vehicle
            
            response = test_client.post("/vehicles/", json=sample_vehicle_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["plate"] == sample_vehicle_data["plate"]
    
    def test_create_vehicle_duplicate_plate(self, test_client, sample_vehicle_data):
        """Test vehicle creation with duplicate plate"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.return_value = sample_vehicle_data  # Existing vehicle
            
            response = test_client.post("/vehicles/", json=sample_vehicle_data)
            
            assert response.status_code == 400
            data = response.json()
            assert "already exists" in data["detail"]
    
    def test_get_vehicle_success(self, test_client, sample_vehicle_data):
        """Test successful vehicle retrieval"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.return_value = sample_vehicle_data
            
            response = test_client.get(f"/vehicles/{sample_vehicle_data['plate']}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["plate"] == sample_vehicle_data["plate"]
    
    def test_get_vehicle_not_found(self, test_client):
        """Test vehicle retrieval when not found"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.return_value = None
            
            response = test_client.get("/vehicles/NONEXISTENT")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"]
    
    def test_update_vehicle_success(self, test_client, sample_vehicle_data):
        """Test successful vehicle update"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.return_value = sample_vehicle_data
            mock_col.update_one.return_value = Mock(modified_count=1)
            
            update_data = {"year": 2022, "color": "blue"}
            response = test_client.put(
                f"/vehicles/{sample_vehicle_data['plate']}", 
                json=update_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["year"] == 2022
    
    def test_delete_vehicle_success(self, test_client, sample_vehicle_data):
        """Test successful vehicle deletion"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.return_value = sample_vehicle_data
            mock_col.delete_one.return_value = Mock(deleted_count=1)
            
            response = test_client.delete(f"/vehicles/{sample_vehicle_data['plate']}")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]

class TestDriverEndpoints:
    """Test driver-related endpoints"""
    
    def test_create_driver_success(self, test_client, sample_driver_data):
        """Test successful driver creation"""
        with patch('app.main.drivers_col') as mock_col:
            mock_col.insert_one.return_value = Mock(inserted_id="test_id")
            mock_col.find_one.return_value = None  # No existing driver
            
            response = test_client.post("/drivers/", json=sample_driver_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["license_number"] == sample_driver_data["license_number"]
    
    def test_get_driver_success(self, test_client, sample_driver_data):
        """Test successful driver retrieval"""
        with patch('app.main.drivers_col') as mock_col:
            mock_col.find_one.return_value = sample_driver_data
            
            response = test_client.get(f"/drivers/{sample_driver_data['license_number']}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == sample_driver_data["name"]

class TestInspectionEndpoints:
    """Test inspection-related endpoints"""
    
    def test_create_inspection_success(self, test_client, sample_inspection_data):
        """Test successful inspection creation"""
        with patch('app.main.inspections_col') as mock_col:
            mock_col.insert_one.return_value = Mock(inserted_id="test_id")
            
            response = test_client.post("/inspections/", json=sample_inspection_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["vehicle_plate"] == sample_inspection_data["vehicle_plate"]
    
    def test_get_inspections_by_vehicle(self, test_client, sample_inspection_data):
        """Test getting inspections by vehicle plate"""
        with patch('app.main.inspections_col') as mock_col:
            mock_col.find.return_value = [sample_inspection_data]
            
            response = test_client.get(f"/inspections/vehicle/{sample_inspection_data['vehicle_plate']}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["vehicle_plate"] == sample_inspection_data["vehicle_plate"]

class TestImageUploadEndpoints:
    """Test image upload and processing endpoints"""
    
    def test_upload_image_success(self, test_client, sample_image_bytes):
        """Test successful image upload"""
        with patch('app.main.get_damage_model') as mock_damage, \
             patch('app.main.get_parts_model') as mock_parts:
            
            # Mock models
            mock_damage.return_value = Mock(predict=Mock(return_value=[
                Mock(boxes=Mock(data=[], conf=[], cls=[]), names={})
            ]))
            mock_parts.return_value = Mock(predict=Mock(return_value=[
                Mock(boxes=Mock(data=[], conf=[], cls=[]), names={})
            ]))
            
            files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            
            response = test_client.post("/inspect/upload/", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "damage_detections" in data
            assert "parts_detections" in data
    
    def test_upload_invalid_file_type(self, test_client):
        """Test upload with invalid file type"""
        files = {"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
        
        response = test_client.post("/inspect/upload/", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid file type" in data["detail"]
    
    def test_upload_large_file(self, test_client):
        """Test upload with file too large"""
        # Create a large fake image (over 8MB)
        large_content = b"0" * (9 * 1024 * 1024)  # 9MB
        files = {"file": ("large.jpg", BytesIO(large_content), "image/jpeg")}
        
        response = test_client.post("/inspect/upload/", files=files)
        
        assert response.status_code == 413
        data = response.json()
        assert "too large" in data["detail"]

class TestWebSocketEndpoints:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self, test_client):
        """Test WebSocket connection establishment"""
        with test_client.websocket_connect("/ws/inspect") as websocket:
            # Send test message
            websocket.send_json({"type": "ping"})
            
            # Receive response
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    def test_websocket_inspection_flow(self, test_client):
        """Test complete inspection flow via WebSocket"""
        with test_client.websocket_connect("/ws/inspect") as websocket:
            # Start inspection
            websocket.send_json({
                "type": "start_inspection",
                "vehicle_plate": "ABC123"
            })
            
            # Should receive confirmation
            data = websocket.receive_json()
            assert data["type"] == "inspection_started"
            assert data["vehicle_plate"] == "ABC123"

class TestAdminEndpoints:
    """Test administrative endpoints"""
    
    def test_get_system_stats(self, test_client):
        """Test system statistics endpoint"""
        with patch('app.main.vehicles_col') as mock_vehicles, \
             patch('app.main.inspections_col') as mock_inspections:
            
            mock_vehicles.count_documents.return_value = 10
            mock_inspections.count_documents.return_value = 25
            
            response = test_client.get("/admin/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_vehicles"] == 10
            assert data["total_inspections"] == 25
    
    def test_cleanup_old_data(self, test_client):
        """Test cleanup of old data"""
        with patch('app.main.sessions_col') as mock_sessions:
            mock_sessions.delete_many.return_value = Mock(deleted_count=5)
            
            response = test_client.post("/admin/cleanup")
            
            assert response.status_code == 200
            data = response.json()
            assert data["cleaned_sessions"] == 5

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_payload(self, test_client):
        """Test handling of invalid JSON payload"""
        response = test_client.post(
            "/vehicles/", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, test_client):
        """Test handling of missing required fields"""
        incomplete_data = {"brand": "Toyota"}  # Missing plate
        
        response = test_client.post("/vehicles/", json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "field required" in str(data["detail"])
    
    def test_database_connection_error(self, test_client):
        """Test handling of database connection errors"""
        with patch('app.main.vehicles_col') as mock_col:
            mock_col.find_one.side_effect = Exception("Database connection failed")
            
            response = test_client.get("/vehicles/ABC123")
            
            assert response.status_code == 500
    
    def test_model_prediction_error(self, test_client, sample_image_bytes):
        """Test handling of model prediction errors"""
        with patch('app.main.get_damage_model') as mock_damage:
            mock_damage.return_value.predict.side_effect = Exception("Model error")
            
            files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            
            response = test_client.post("/inspect/upload/", files=files)
            
            assert response.status_code == 500

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_exceeded(self, test_client):
        """Test rate limiting when limit is exceeded"""
        # Make multiple rapid requests
        for i in range(35):  # Exceed 30/minute limit
            response = test_client.get("/health")
            
            if i < 30:
                assert response.status_code == 200
            else:
                # Should be rate limited
                assert response.status_code == 429

class TestCORSHeaders:
    """Test CORS headers and cross-origin requests"""
    
    def test_cors_headers_present(self, test_client):
        """Test CORS headers are present in responses"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        # Check for CORS headers (if configured)
        # This depends on your CORS configuration
    
    def test_preflight_request(self, test_client):
        """Test preflight OPTIONS request handling"""
        response = test_client.options("/vehicles/")
        
        # Should handle OPTIONS request properly
        assert response.status_code in [200, 204]
