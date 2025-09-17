"""
Test configuration and fixtures for the inspector vehicular backend
"""
import os
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from pymongo import MongoClient
from app.main import app
from app.config import Settings
from app.database import client, db

# Override settings for testing
class TestSettings(Settings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "vehicular_tfm_test"
    ENABLE_DEBUG_IMAGES: bool = False
    ENABLE_PDF_EXPORT: bool = False
    ENABLE_OCR: bool = False
    ENABLE_BG_CLASSIFIER: bool = False
    ENABLE_SEGMENTATION: bool = False
    ENABLE_TAMPER_DETECTION: bool = False
    ENABLE_COLOR_ANALYSIS: bool = False
    DAMAGE_MODEL_PATH: str = "tests/fixtures/mock_damage.pt"
    PARTS_MODEL_PATH: str = "tests/fixtures/mock_parts.pt"

@pytest.fixture(scope="session")
def test_settings():
    return TestSettings()

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    with patch('app.config.get_settings', return_value=TestSettings()):
        client = TestClient(app)
        yield client

@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    test_client = MongoClient("mongodb://localhost:27017")
    test_database = test_client["vehicular_tfm_test"]
    yield test_database
    # Cleanup after test
    test_client.drop_database("vehicular_tfm_test")
    test_client.close()

@pytest.fixture
def mock_yolo_model():
    """Mock YOLO model for testing"""
    mock_model = Mock()
    mock_model.predict.return_value = [Mock(
        boxes=Mock(
            data=[[100, 100, 200, 200, 0.9, 0]],  # x1, y1, x2, y2, conf, class
            conf=[0.9],
            cls=[0]
        ),
        names={0: 'test_class'}
    )]
    return mock_model

@pytest.fixture
def sample_image_bytes():
    """Sample image bytes for testing"""
    # Create a minimal valid image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

@pytest.fixture
def sample_vehicle_data():
    """Sample vehicle data for testing"""
    return {
        "plate": "ABC123",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "color": "white",
        "vin": "1HGBH41JXMN109186"
    }

@pytest.fixture
def sample_driver_data():
    """Sample driver data for testing"""
    return {
        "license_number": "DL123456789",
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john.doe@example.com"
    }

@pytest.fixture
def sample_inspection_data():
    """Sample inspection data for testing"""
    return {
        "vehicle_plate": "ABC123",
        "driver_license": "DL123456789",
        "inspection_type": "damage",
        "images": [],
        "notes": "Test inspection"
    }

@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""
    from io import BytesIO
    
    file_content = b"fake image content"
    return {
        "file": BytesIO(file_content),
        "filename": "test_image.jpg",
        "content_type": "image/jpeg"
    }
