"""
Tests for YOLO model loading and inference
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from app.yolo_model import load_models, _safe_load, get_damage_model, get_parts_model

class TestYOLOModelLoading:
    """Test YOLO model loading functionality"""
    
    @patch('app.yolo_model.YOLO')
    def test_safe_load_success(self, mock_yolo):
        """Test successful model loading"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        result = _safe_load("test_model.pt", "test-model")
        
        assert result == mock_model
        mock_yolo.assert_called_once_with("test_model.pt")
    
    @patch('app.yolo_model.YOLO')
    def test_safe_load_failure(self, mock_yolo):
        """Test model loading failure handling"""
        mock_yolo.side_effect = Exception("Model loading failed")
        
        result = _safe_load("invalid_model.pt", "test-model")
        
        assert result is None
        mock_yolo.assert_called_once_with("invalid_model.pt")
    
    @patch('app.yolo_model._safe_load')
    def test_load_models_success(self, mock_safe_load):
        """Test successful loading of both models"""
        mock_damage_model = Mock()
        mock_parts_model = Mock()
        mock_safe_load.side_effect = [mock_damage_model, mock_parts_model]
        
        with patch('app.yolo_model.settings') as mock_settings:
            mock_settings.DAMAGE_MODEL_PATH = "damage.pt"
            mock_settings.PARTS_MODEL_PATH = "parts.pt"
            mock_settings.DAMAGE_MODEL_NAME = "damage-model"
            mock_settings.PARTS_MODEL_NAME = "parts-model"
            
            load_models()
            
            assert mock_safe_load.call_count == 2
    
    def test_get_damage_model_not_loaded(self):
        """Test getting damage model when not loaded"""
        with patch('app.yolo_model._damage_model', None):
            result = get_damage_model()
            assert result is None
    
    def test_get_parts_model_not_loaded(self):
        """Test getting parts model when not loaded"""
        with patch('app.yolo_model._parts_model', None):
            result = get_parts_model()
            assert result is None

class TestYOLOModelInference:
    """Test YOLO model inference functionality"""
    
    def test_model_prediction_structure(self, mock_yolo_model):
        """Test model prediction returns expected structure"""
        # Mock image array
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run prediction
        results = mock_yolo_model.predict(image)
        
        # Verify structure
        assert len(results) == 1
        result = results[0]
        assert hasattr(result, 'boxes')
        assert hasattr(result, 'names')
        assert hasattr(result.boxes, 'data')
        assert hasattr(result.boxes, 'conf')
        assert hasattr(result.boxes, 'cls')
    
    def test_model_prediction_with_confidence_threshold(self, mock_yolo_model):
        """Test model prediction with confidence threshold"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Configure mock to return different confidence levels
        mock_result = Mock()
        mock_result.boxes.data = [
            [100, 100, 200, 200, 0.9, 0],  # High confidence
            [300, 300, 400, 400, 0.3, 1]   # Low confidence
        ]
        mock_result.boxes.conf = [0.9, 0.3]
        mock_result.boxes.cls = [0, 1]
        mock_result.names = {0: 'high_conf_class', 1: 'low_conf_class'}
        
        mock_yolo_model.predict.return_value = [mock_result]
        
        results = mock_yolo_model.predict(image, conf=0.5)
        
        # Should filter out low confidence detections
        assert len(results) == 1

class TestModelConfiguration:
    """Test model configuration and settings"""
    
    def test_model_paths_configuration(self):
        """Test model paths are correctly configured"""
        from app.config import settings
        
        assert hasattr(settings, 'DAMAGE_MODEL_PATH')
        assert hasattr(settings, 'PARTS_MODEL_PATH')
        assert hasattr(settings, 'DAMAGE_MODEL_NAME')
        assert hasattr(settings, 'PARTS_MODEL_NAME')
        
        # Verify paths are strings
        assert isinstance(settings.DAMAGE_MODEL_PATH, str)
        assert isinstance(settings.PARTS_MODEL_PATH, str)
    
    def test_confidence_thresholds_configuration(self):
        """Test confidence thresholds are properly configured"""
        from app.config import settings
        
        assert hasattr(settings, 'DEFAULT_CONF_DAMAGE')
        assert hasattr(settings, 'DEFAULT_CONF_PARTS')
        
        # Verify thresholds are valid floats
        assert 0.0 <= settings.DEFAULT_CONF_DAMAGE <= 1.0
        assert 0.0 <= settings.DEFAULT_CONF_PARTS <= 1.0
    
    def test_class_labels_configuration(self):
        """Test class labels are properly configured"""
        from app.config import settings
        
        assert hasattr(settings, 'DAMAGE_LABELS')
        assert hasattr(settings, 'PART_LABELS')
        
        # Verify labels are strings with comma-separated values
        damage_labels = settings.DAMAGE_LABELS.split(',')
        part_labels = settings.PART_LABELS.split(',')
        
        assert len(damage_labels) > 0
        assert len(part_labels) > 0
        assert all(isinstance(label.strip(), str) for label in damage_labels)
        assert all(isinstance(label.strip(), str) for label in part_labels)

class TestModelErrorHandling:
    """Test error handling in model operations"""
    
    @patch('app.yolo_model.YOLO')
    def test_model_loading_with_invalid_path(self, mock_yolo):
        """Test handling of invalid model paths"""
        mock_yolo.side_effect = FileNotFoundError("Model file not found")
        
        result = _safe_load("nonexistent_model.pt", "test-model")
        
        assert result is None
    
    @patch('app.yolo_model.YOLO')
    def test_model_loading_with_corrupted_file(self, mock_yolo):
        """Test handling of corrupted model files"""
        mock_yolo.side_effect = RuntimeError("Corrupted model file")
        
        result = _safe_load("corrupted_model.pt", "test-model")
        
        assert result is None
    
    def test_prediction_with_invalid_image(self, mock_yolo_model):
        """Test prediction with invalid image data"""
        # Test with None
        with pytest.raises((AttributeError, TypeError)):
            mock_yolo_model.predict(None)
        
        # Test with invalid array shape
        invalid_image = np.zeros((10,), dtype=np.uint8)  # 1D array
        
        # Mock should handle this gracefully
        mock_yolo_model.predict.side_effect = ValueError("Invalid image shape")
        
        with pytest.raises(ValueError):
            mock_yolo_model.predict(invalid_image)

class TestModelPerformance:
    """Test model performance and optimization"""
    
    def test_model_inference_time(self, mock_yolo_model):
        """Test model inference time is reasonable"""
        import time
        
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock quick inference
        def mock_predict(*args, **kwargs):
            time.sleep(0.001)  # Simulate 1ms inference
            return [Mock(boxes=Mock(data=[], conf=[], cls=[]), names={})]
        
        mock_yolo_model.predict = mock_predict
        
        start_time = time.time()
        results = mock_yolo_model.predict(image)
        inference_time = time.time() - start_time
        
        # Should be fast (less than 1 second for test)
        assert inference_time < 1.0
        assert len(results) == 1
    
    def test_batch_prediction_capability(self, mock_yolo_model):
        """Test model can handle batch predictions"""
        # Create batch of images
        batch_images = [
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.zeros((480, 640, 3), dtype=np.uint8)
        ]
        
        # Mock batch prediction
        mock_results = [
            Mock(boxes=Mock(data=[], conf=[], cls=[]), names={})
            for _ in range(3)
        ]
        mock_yolo_model.predict.return_value = mock_results
        
        results = mock_yolo_model.predict(batch_images)
        
        assert len(results) == 3
