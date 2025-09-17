"""
Integration tests for the complete system workflow
"""
import pytest
from unittest.mock import Mock, patch
import numpy as np
from fastapi.testclient import TestClient
from io import BytesIO
import json

class TestCompleteInspectionWorkflow:
    """Test complete inspection workflow from start to finish"""
    
    def test_end_to_end_damage_inspection(self, test_client, sample_vehicle_data, sample_driver_data, sample_image_bytes):
        """Test complete damage inspection workflow"""
        # Step 1: Create vehicle
        with patch('app.main.vehicles_col') as mock_vehicles:
            mock_vehicles.find_one.return_value = None
            mock_vehicles.insert_one.return_value = Mock(inserted_id="vehicle_id")
            
            vehicle_response = test_client.post("/vehicles/", json=sample_vehicle_data)
            assert vehicle_response.status_code == 201
        
        # Step 2: Create driver
        with patch('app.main.drivers_col') as mock_drivers:
            mock_drivers.find_one.return_value = None
            mock_drivers.insert_one.return_value = Mock(inserted_id="driver_id")
            
            driver_response = test_client.post("/drivers/", json=sample_driver_data)
            assert driver_response.status_code == 201
        
        # Step 3: Start inspection session
        with patch('app.main.sessions_col') as mock_sessions:
            mock_sessions.insert_one.return_value = Mock(inserted_id="session_123")
            
            session_data = {
                "vehicle_plate": sample_vehicle_data["plate"],
                "driver_license": sample_driver_data["license_number"],
                "inspection_type": "damage"
            }
            
            session_response = test_client.post("/inspect/start/", json=session_data)
            assert session_response.status_code == 201
            session_id = session_response.json()["session_id"]
        
        # Step 4: Upload and process images
        with patch('app.main.get_damage_model') as mock_damage, \
             patch('app.main.get_parts_model') as mock_parts:
            
            # Mock model predictions
            mock_damage_result = Mock()
            mock_damage_result.boxes.data = [[100, 100, 200, 200, 0.9, 0]]
            mock_damage_result.boxes.conf = [0.9]
            mock_damage_result.boxes.cls = [0]
            mock_damage_result.names = {0: "scratch"}
            
            mock_parts_result = Mock()
            mock_parts_result.boxes.data = [[50, 50, 150, 150, 0.8, 1]]
            mock_parts_result.boxes.conf = [0.8]
            mock_parts_result.boxes.cls = [1]
            mock_parts_result.names = {1: "bumper"}
            
            mock_damage.return_value.predict.return_value = [mock_damage_result]
            mock_parts.return_value.predict.return_value = [mock_parts_result]
            
            files = {"file": ("damage1.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            upload_response = test_client.post(
                f"/inspect/upload/?session_id={session_id}", 
                files=files
            )
            
            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            assert len(upload_data["damage_detections"]) == 1
            assert upload_data["damage_detections"][0]["class"] == "scratch"
        
        # Step 5: Finalize inspection
        with patch('app.main.sessions_col') as mock_sessions, \
             patch('app.main.inspections_col') as mock_inspections:
            
            session_data_full = {
                "_id": session_id,
                "vehicle_plate": sample_vehicle_data["plate"],
                "images": [{"filename": "damage1.jpg", "results": upload_data}]
            }
            
            mock_sessions.find_one.return_value = session_data_full
            mock_inspections.insert_one.return_value = Mock(inserted_id="inspection_123")
            mock_sessions.delete_one.return_value = Mock(deleted_count=1)
            
            finalize_response = test_client.post(f"/inspect/finalize/{session_id}")
            
            assert finalize_response.status_code == 200
            final_data = finalize_response.json()
            assert "inspection_id" in final_data
    
    def test_multi_image_inspection_workflow(self, test_client, sample_image_bytes):
        """Test inspection workflow with multiple images"""
        session_id = "session_multi"
        
        with patch('app.main.get_damage_model') as mock_damage, \
             patch('app.main.get_parts_model') as mock_parts:
            
            # Mock consistent results
            mock_result = Mock()
            mock_result.boxes.data = []
            mock_result.boxes.conf = []
            mock_result.boxes.cls = []
            mock_result.names = {}
            
            mock_damage.return_value.predict.return_value = [mock_result]
            mock_parts.return_value.predict.return_value = [mock_result]
            
            # Upload multiple images
            image_names = ["front.jpg", "rear.jpg", "side.jpg"]
            
            for image_name in image_names:
                files = {"file": (image_name, BytesIO(sample_image_bytes), "image/jpeg")}
                response = test_client.post(
                    f"/inspect/upload/?session_id={session_id}", 
                    files=files
                )
                assert response.status_code == 200

class TestWebSocketInspectionFlow:
    """Test WebSocket-based inspection flow"""
    
    def test_real_time_inspection_updates(self, test_client):
        """Test real-time inspection updates via WebSocket"""
        with test_client.websocket_connect("/ws/inspect") as websocket:
            # Start inspection
            websocket.send_json({
                "type": "start_inspection",
                "vehicle_plate": "ABC123",
                "inspection_type": "damage"
            })
            
            # Receive confirmation
            response = websocket.receive_json()
            assert response["type"] == "inspection_started"
            session_id = response["session_id"]
            
            # Send image processing request
            websocket.send_json({
                "type": "process_image",
                "session_id": session_id,
                "image_name": "test.jpg"
            })
            
            # Receive processing result
            result = websocket.receive_json()
            assert result["type"] == "image_processed"
            assert result["session_id"] == session_id
    
    def test_websocket_error_handling(self, test_client):
        """Test WebSocket error handling"""
        with test_client.websocket_connect("/ws/inspect") as websocket:
            # Send invalid message
            websocket.send_json({
                "type": "invalid_command",
                "data": "test"
            })
            
            # Should receive error response
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "invalid command" in response["message"].lower()

class TestDataConsistencyAndIntegrity:
    """Test data consistency and integrity across the system"""
    
    def test_vehicle_inspection_data_consistency(self, test_client, test_db):
        """Test data consistency between vehicle and inspection records"""
        # Create vehicle
        vehicle_data = {
            "plate": "CONSISTENCY123",
            "brand": "Honda",
            "model": "Civic",
            "year": 2020
        }
        
        vehicles_col = test_db["vehicles"]
        vehicle_result = vehicles_col.insert_one(vehicle_data)
        
        # Create inspection for the vehicle
        inspection_data = {
            "vehicle_plate": "CONSISTENCY123",
            "inspection_type": "damage",
            "results": {"damage_count": 2, "severity": "medium"},
            "timestamp": "2025-09-16T10:00:00Z"
        }
        
        inspections_col = test_db["inspections"]
        inspection_result = inspections_col.insert_one(inspection_data)
        
        # Verify consistency
        saved_vehicle = vehicles_col.find_one({"_id": vehicle_result.inserted_id})
        saved_inspection = inspections_col.find_one({"_id": inspection_result.inserted_id})
        
        assert saved_vehicle["plate"] == saved_inspection["vehicle_plate"]
    
    def test_session_cleanup_integrity(self, test_client, test_db):
        """Test session cleanup maintains data integrity"""
        sessions_col = test_db["sessions"]
        inspections_col = test_db["inspections"]
        
        # Create test session
        session_data = {
            "vehicle_plate": "CLEANUP123",
            "status": "active",
            "images": [{"filename": "test.jpg", "results": {}}]
        }
        
        session_result = sessions_col.insert_one(session_data)
        session_id = str(session_result.inserted_id)
        
        # Finalize session (should move to inspections and clean session)
        with patch('app.main.sessions_col', sessions_col), \
             patch('app.main.inspections_col', inspections_col):
            
            response = test_client.post(f"/inspect/finalize/{session_id}")
            
            # Session should be cleaned
            remaining_session = sessions_col.find_one({"_id": session_result.inserted_id})
            assert remaining_session is None
            
            # Inspection should be created
            created_inspection = inspections_col.find_one({"vehicle_plate": "CLEANUP123"})
            assert created_inspection is not None

class TestPerformanceAndScalability:
    """Test system performance and scalability"""
    
    def test_concurrent_inspections(self, test_client):
        """Test handling of concurrent inspection sessions"""
        import threading
        import time
        
        results = []
        
        def create_inspection(plate_suffix):
            try:
                with patch('app.main.sessions_col') as mock_sessions:
                    mock_sessions.insert_one.return_value = Mock(inserted_id=f"session_{plate_suffix}")
                    
                    session_data = {
                        "vehicle_plate": f"CONCURRENT{plate_suffix}",
                        "driver_license": f"DL{plate_suffix}",
                        "inspection_type": "damage"
                    }
                    
                    response = test_client.post("/inspect/start/", json=session_data)
                    results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        # Create multiple concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_inspection, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(result == 201 for result in results)
    
    def test_large_image_batch_processing(self, test_client, sample_image_bytes):
        """Test processing of large image batches"""
        session_id = "batch_session"
        
        with patch('app.main.get_damage_model') as mock_damage, \
             patch('app.main.get_parts_model') as mock_parts:
            
            # Mock fast processing
            mock_result = Mock()
            mock_result.boxes.data = []
            mock_result.boxes.conf = []
            mock_result.boxes.cls = []
            mock_result.names = {}
            
            mock_damage.return_value.predict.return_value = [mock_result]
            mock_parts.return_value.predict.return_value = [mock_result]
            
            # Process multiple images quickly
            start_time = time.time()
            
            for i in range(10):  # Process 10 images
                files = {"file": (f"batch_{i}.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
                response = test_client.post(
                    f"/inspect/upload/?session_id={session_id}", 
                    files=files
                )
                assert response.status_code == 200
            
            processing_time = time.time() - start_time
            
            # Should process reasonably quickly (less than 10 seconds for 10 images)
            assert processing_time < 10.0

class TestSecurityAndValidation:
    """Test security features and input validation"""
    
    def test_file_upload_security(self, test_client):
        """Test file upload security measures"""
        # Test malicious file upload
        malicious_content = b"<?php system($_GET['cmd']); ?>"
        files = {"file": ("malicious.php", BytesIO(malicious_content), "application/x-php")}
        
        response = test_client.post("/inspect/upload/", files=files)
        
        # Should reject non-image files
        assert response.status_code == 400
    
    def test_sql_injection_prevention(self, test_client):
        """Test SQL injection prevention (for MongoDB)"""
        # Attempt injection in plate parameter
        malicious_plate = "'; DROP TABLE vehicles; --"
        
        response = test_client.get(f"/vehicles/{malicious_plate}")
        
        # Should handle safely (not find vehicle, not crash)
        assert response.status_code in [404, 400]
    
    def test_input_sanitization(self, test_client):
        """Test input sanitization"""
        # Test with special characters and potential XSS
        malicious_data = {
            "plate": "<script>alert('xss')</script>",
            "brand": "'; DELETE FROM vehicles WHERE 1=1; --",
            "model": "../../etc/passwd",
            "year": "UNION SELECT * FROM users"
        }
        
        response = test_client.post("/vehicles/", json=malicious_data)
        
        # Should either sanitize or reject
        if response.status_code == 201:
            # If accepted, should be sanitized
            data = response.json()
            assert "<script>" not in data["plate"]
        else:
            # Or should be rejected with 400/422
            assert response.status_code in [400, 422]
    
    def test_rate_limiting_per_ip(self, test_client):
        """Test rate limiting per IP address"""
        # Simulate rapid requests from same IP
        responses = []
        
        for i in range(35):  # Exceed rate limit
            response = test_client.get("/health")
            responses.append(response.status_code)
        
        # Some requests should be rate limited
        rate_limited_count = sum(1 for status in responses if status == 429)
        assert rate_limited_count > 0

class TestErrorRecoveryAndResilience:
    """Test system error recovery and resilience"""
    
    def test_database_connection_recovery(self, test_client):
        """Test recovery from database connection issues"""
        with patch('app.main.vehicles_col') as mock_col:
            # Simulate database connection failure then recovery
            mock_col.find_one.side_effect = [
                Exception("Connection failed"),  # First call fails
                {"plate": "ABC123", "brand": "Honda"}  # Second call succeeds
            ]
            
            # First request should fail
            response1 = test_client.get("/vehicles/ABC123")
            assert response1.status_code == 500
            
            # Second request should succeed (simulating recovery)
            response2 = test_client.get("/vehicles/ABC123")
            assert response2.status_code == 200
    
    def test_model_failure_graceful_degradation(self, test_client, sample_image_bytes):
        """Test graceful degradation when models fail"""
        with patch('app.main.get_damage_model') as mock_damage, \
             patch('app.main.get_parts_model') as mock_parts:
            
            # Simulate model failure
            mock_damage.return_value.predict.side_effect = Exception("Model crashed")
            mock_parts.return_value = None  # Model not available
            
            files = {"file": ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg")}
            response = test_client.post("/inspect/upload/", files=files)
            
            # Should handle gracefully
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.json()
                # Should indicate model unavailable
                assert "error" in data or "unavailable" in str(data).lower()
    
    def test_partial_system_failure_handling(self, test_client):
        """Test handling when part of system fails"""
        # Simulate OCR service failure but core inspection works
        with patch('app.services.ocr.extract_text') as mock_ocr:
            mock_ocr.side_effect = Exception("OCR service down")
            
            session_data = {
                "vehicle_plate": "PARTIAL123",
                "inspection_type": "damage"
            }
            
            response = test_client.post("/inspect/start/", json=session_data)
            
            # Core inspection should still work
            assert response.status_code == 201
