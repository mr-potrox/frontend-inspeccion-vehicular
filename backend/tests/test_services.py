"""
Tests for business logic services
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from datetime import datetime
from app.services.inspection_service import InspectionService
from app.services.pipeline import PipelineService
from app.services.rules_engine import RulesEngine

class TestInspectionService:
    """Test inspection service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.inspection_service = InspectionService()
    
    def test_create_inspection_session(self):
        """Test creating a new inspection session"""
        with patch('app.services.inspection_service.sessions_col') as mock_col:
            mock_col.insert_one.return_value = Mock(inserted_id="session_123")
            
            session_id = self.inspection_service.create_session("ABC123", "damage")
            
            assert session_id == "session_123"
            mock_col.insert_one.assert_called_once()
    
    def test_add_image_to_session(self):
        """Test adding image to inspection session"""
        with patch('app.services.inspection_service.sessions_col') as mock_col:
            mock_col.update_one.return_value = Mock(modified_count=1)
            
            image_data = {"filename": "test.jpg", "results": []}
            result = self.inspection_service.add_image("session_123", image_data)
            
            assert result is True
            mock_col.update_one.assert_called_once()
    
    def test_finalize_inspection(self):
        """Test finalizing inspection session"""
        session_data = {
            "_id": "session_123",
            "vehicle_plate": "ABC123",
            "images": [{"filename": "test.jpg", "results": []}],
            "created_at": datetime.now()
        }
        
        with patch('app.services.inspection_service.sessions_col') as mock_sessions, \
             patch('app.services.inspection_service.inspections_col') as mock_inspections:
            
            mock_sessions.find_one.return_value = session_data
            mock_inspections.insert_one.return_value = Mock(inserted_id="inspection_123")
            mock_sessions.delete_one.return_value = Mock(deleted_count=1)
            
            inspection_id = self.inspection_service.finalize_session("session_123")
            
            assert inspection_id == "inspection_123"
            mock_inspections.insert_one.assert_called_once()
            mock_sessions.delete_one.assert_called_once()
    
    def test_get_session_status(self):
        """Test getting inspection session status"""
        session_data = {
            "_id": "session_123",
            "vehicle_plate": "ABC123",
            "status": "active",
            "images": []
        }
        
        with patch('app.services.inspection_service.sessions_col') as mock_col:
            mock_col.find_one.return_value = session_data
            
            status = self.inspection_service.get_session_status("session_123")
            
            assert status["status"] == "active"
            assert status["vehicle_plate"] == "ABC123"

class TestPipelineService:
    """Test pipeline service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.pipeline_service = PipelineService()
    
    @patch('app.services.pipeline.get_damage_model')
    @patch('app.services.pipeline.get_parts_model')
    def test_process_image_complete_flow(self, mock_parts_model, mock_damage_model):
        """Test complete image processing pipeline"""
        # Mock models
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
        
        mock_damage_model.return_value.predict.return_value = [mock_damage_result]
        mock_parts_model.return_value.predict.return_value = [mock_parts_result]
        
        # Test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = self.pipeline_service.process_image(image, "test.jpg")
        
        assert "damage_detections" in result
        assert "parts_detections" in result
        assert len(result["damage_detections"]) == 1
        assert len(result["parts_detections"]) == 1
        assert result["damage_detections"][0]["class"] == "scratch"
        assert result["parts_detections"][0]["class"] == "bumper"
    
    def test_process_image_with_preprocessing(self):
        """Test image processing with preprocessing enabled"""
        with patch('app.services.pipeline.enhance_image') as mock_enhance:
            mock_enhance.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            with patch('app.services.pipeline.get_damage_model') as mock_damage, \
                 patch('app.services.pipeline.get_parts_model') as mock_parts:
                
                mock_damage.return_value.predict.return_value = [Mock(
                    boxes=Mock(data=[], conf=[], cls=[]), names={}
                )]
                mock_parts.return_value.predict.return_value = [Mock(
                    boxes=Mock(data=[], conf=[], cls=[]), names={}
                )]
                
                image = np.zeros((480, 640, 3), dtype=np.uint8)
                result = self.pipeline_service.process_image(image, "test.jpg")
                
                mock_enhance.assert_called_once()
    
    def test_batch_processing(self):
        """Test batch image processing"""
        images = [
            (np.zeros((480, 640, 3), dtype=np.uint8), "image1.jpg"),
            (np.zeros((480, 640, 3), dtype=np.uint8), "image2.jpg"),
            (np.zeros((480, 640, 3), dtype=np.uint8), "image3.jpg")
        ]
        
        with patch.object(self.pipeline_service, 'process_image') as mock_process:
            mock_process.return_value = {"damage_detections": [], "parts_detections": []}
            
            results = self.pipeline_service.process_batch(images)
            
            assert len(results) == 3
            assert mock_process.call_count == 3

class TestRulesEngine:
    """Test rules engine functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rules_engine = RulesEngine()
    
    def test_evaluate_damage_severity(self):
        """Test damage severity evaluation"""
        damage_detections = [
            {"class": "scratch", "confidence": 0.9, "bbox": [100, 100, 200, 200]},
            {"class": "dent", "confidence": 0.8, "bbox": [300, 300, 400, 400]}
        ]
        
        severity = self.rules_engine.evaluate_damage_severity(damage_detections)
        
        assert severity in ["low", "medium", "high"]
    
    def test_check_completeness_score(self):
        """Test vehicle completeness scoring"""
        parts_detections = [
            {"class": "bumper", "confidence": 0.9},
            {"class": "headlight", "confidence": 0.8},
            {"class": "door", "confidence": 0.7}
        ]
        
        expected_parts = ["bumper", "headlight", "door", "mirror", "wheel"]
        
        score = self.rules_engine.calculate_completeness_score(
            parts_detections, expected_parts
        )
        
        assert 0.0 <= score <= 1.0
        assert score == 0.6  # 3 out of 5 parts detected
    
    def test_fraud_detection_rules(self):
        """Test fraud detection rules"""
        inspection_data = {
            "vehicle_plate": "ABC123",
            "damage_detections": [
                {"class": "scratch", "confidence": 0.9, "severity": "high"}
            ],
            "parts_detections": [
                {"class": "bumper", "confidence": 0.8}
            ],
            "metadata": {
                "location": "outdoor",
                "lighting": "good",
                "image_quality": "high"
            }
        }
        
        fraud_flags = self.rules_engine.check_fraud_indicators(inspection_data)
        
        assert isinstance(fraud_flags, list)
        # Should not flag as fraud for normal inspection
        assert len(fraud_flags) == 0
    
    def test_quality_validation_rules(self):
        """Test quality validation rules"""
        image_metadata = {
            "resolution": (1920, 1080),
            "brightness": 128,
            "contrast": 64,
            "blur_score": 0.1,
            "file_size": 2048000  # 2MB
        }
        
        quality_score = self.rules_engine.validate_image_quality(image_metadata)
        
        assert 0.0 <= quality_score <= 1.0
    
    def test_business_rules_validation(self):
        """Test business rules validation"""
        inspection_request = {
            "vehicle_plate": "ABC123",
            "inspection_type": "damage",
            "driver_license": "DL123456789",
            "timestamp": datetime.now().isoformat()
        }
        
        validation_result = self.rules_engine.validate_inspection_request(
            inspection_request
        )
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0

class TestImageProcessingServices:
    """Test image processing related services"""
    
    def test_image_enhancement_service(self):
        """Test image enhancement functionality"""
        from app.services.image_preprocess import enhance_image
        
        # Create test image
        original_image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        enhanced_image = enhance_image(original_image)
        
        assert enhanced_image.shape == original_image.shape
        assert enhanced_image.dtype == np.uint8
    
    def test_segmentation_service(self):
        """Test vehicle segmentation service"""
        from app.services.segmentation import segment_vehicle
        
        with patch('app.services.segmentation.cv2') as mock_cv2:
            mock_cv2.imread.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            image = np.zeros((480, 640, 3), dtype=np.uint8)
            mask = segment_vehicle(image)
            
            assert mask is not None
    
    def test_color_analysis_service(self):
        """Test color analysis service"""
        from app.services.color_exif import analyze_vehicle_color
        
        # Create test image with dominant blue color
        blue_image = np.full((480, 640, 3), [0, 0, 255], dtype=np.uint8)
        
        color_info = analyze_vehicle_color(blue_image)
        
        assert "dominant_color" in color_info
        assert "color_name" in color_info
        assert "confidence" in color_info

class TestUtilityServices:
    """Test utility services"""
    
    def test_pdf_export_service(self):
        """Test PDF export functionality"""
        from app.services.pdf_export import generate_inspection_report
        
        inspection_data = {
            "vehicle_plate": "ABC123",
            "timestamp": datetime.now(),
            "damage_detections": [],
            "parts_detections": [],
            "summary": "Test inspection"
        }
        
        with patch('app.services.pdf_export.canvas') as mock_canvas:
            mock_canvas.Canvas.return_value = Mock()
            
            pdf_path = generate_inspection_report(inspection_data)
            
            assert pdf_path is not None
            assert pdf_path.endswith('.pdf')
    
    def test_markdown_builder_service(self):
        """Test markdown report builder"""
        from app.services.markdown_builder import build_inspection_report
        
        inspection_data = {
            "vehicle_plate": "ABC123",
            "timestamp": datetime.now(),
            "damage_detections": [
                {"class": "scratch", "confidence": 0.9}
            ],
            "parts_detections": [
                {"class": "bumper", "confidence": 0.8}
            ]
        }
        
        markdown_content = build_inspection_report(inspection_data)
        
        assert isinstance(markdown_content, str)
        assert "ABC123" in markdown_content
        assert "scratch" in markdown_content
        assert "bumper" in markdown_content

class TestErrorHandlingInServices:
    """Test error handling in services"""
    
    def test_service_with_model_unavailable(self):
        """Test service behavior when models are unavailable"""
        with patch('app.services.pipeline.get_damage_model', return_value=None):
            pipeline = PipelineService()
            image = np.zeros((480, 640, 3), dtype=np.uint8)
            
            result = pipeline.process_image(image, "test.jpg")
            
            assert "error" in result
            assert "damage model not available" in result["error"]
    
    def test_service_with_invalid_image(self):
        """Test service behavior with invalid image"""
        pipeline = PipelineService()
        
        # Test with None image
        result = pipeline.process_image(None, "test.jpg")
        assert "error" in result
        
        # Test with invalid shape
        invalid_image = np.zeros((10,), dtype=np.uint8)
        result = pipeline.process_image(invalid_image, "test.jpg")
        assert "error" in result
    
    def test_database_service_error_handling(self):
        """Test database service error handling"""
        with patch('app.services.inspection_service.sessions_col') as mock_col:
            mock_col.insert_one.side_effect = Exception("Database error")
            
            service = InspectionService()
            
            with pytest.raises(Exception):
                service.create_session("ABC123", "damage")
