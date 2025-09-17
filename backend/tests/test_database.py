"""
Tests for database operations and connections
"""
import pytest
from unittest.mock import patch, Mock
from app.database import client, db, vehicles_col, drivers_col, inspections_col, sessions_col

class TestDatabaseConnection:
    """Test database connectivity and collections"""
    
    def test_database_client_connection(self):
        """Test MongoDB client connection"""
        assert client is not None
        # Test server info (requires MongoDB running)
        try:
            server_info = client.server_info()
            assert 'version' in server_info
        except Exception:
            # If MongoDB is not running, skip this test
            pytest.skip("MongoDB server not available")
    
    def test_database_selection(self):
        """Test database selection"""
        assert db is not None
        assert db.name == "vehicular_tfm" or db.name == "vehicular_tfm_test"
    
    def test_collections_exist(self):
        """Test that all required collections are defined"""
        assert vehicles_col is not None
        assert drivers_col is not None
        assert inspections_col is not None
        assert sessions_col is not None

class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    def test_vehicle_crud_operations(self, test_db, sample_vehicle_data):
        """Test vehicle CRUD operations"""
        vehicles = test_db["vehicles"]
        
        # Create
        result = vehicles.insert_one(sample_vehicle_data)
        assert result.inserted_id is not None
        
        # Read
        vehicle = vehicles.find_one({"plate": "ABC123"})
        assert vehicle is not None
        assert vehicle["brand"] == "Toyota"
        
        # Update
        vehicles.update_one(
            {"plate": "ABC123"}, 
            {"$set": {"year": 2021}}
        )
        updated_vehicle = vehicles.find_one({"plate": "ABC123"})
        assert updated_vehicle["year"] == 2021
        
        # Delete
        vehicles.delete_one({"plate": "ABC123"})
        deleted_vehicle = vehicles.find_one({"plate": "ABC123"})
        assert deleted_vehicle is None
    
    def test_driver_crud_operations(self, test_db, sample_driver_data):
        """Test driver CRUD operations"""
        drivers = test_db["drivers"]
        
        # Create
        result = drivers.insert_one(sample_driver_data)
        assert result.inserted_id is not None
        
        # Read
        driver = drivers.find_one({"license_number": "DL123456789"})
        assert driver is not None
        assert driver["name"] == "John Doe"
        
        # Update
        drivers.update_one(
            {"license_number": "DL123456789"}, 
            {"$set": {"phone": "+9876543210"}}
        )
        updated_driver = drivers.find_one({"license_number": "DL123456789"})
        assert updated_driver["phone"] == "+9876543210"
        
        # Delete
        drivers.delete_one({"license_number": "DL123456789"})
        deleted_driver = drivers.find_one({"license_number": "DL123456789"})
        assert deleted_driver is None
    
    def test_inspection_crud_operations(self, test_db, sample_inspection_data):
        """Test inspection CRUD operations"""
        inspections = test_db["inspections"]
        
        # Create
        result = inspections.insert_one(sample_inspection_data)
        assert result.inserted_id is not None
        
        # Read
        inspection = inspections.find_one({"vehicle_plate": "ABC123"})
        assert inspection is not None
        assert inspection["inspection_type"] == "damage"
        
        # Update
        inspections.update_one(
            {"vehicle_plate": "ABC123"}, 
            {"$set": {"notes": "Updated test inspection"}}
        )
        updated_inspection = inspections.find_one({"vehicle_plate": "ABC123"})
        assert updated_inspection["notes"] == "Updated test inspection"
        
        # Delete
        inspections.delete_one({"vehicle_plate": "ABC123"})
        deleted_inspection = inspections.find_one({"vehicle_plate": "ABC123"})
        assert deleted_inspection is None

class TestDatabaseIndexes:
    """Test database indexes and performance"""
    
    def test_vehicle_indexes(self, test_db):
        """Test vehicle collection indexes"""
        vehicles = test_db["vehicles"]
        
        # Create index
        vehicles.create_index("plate", unique=True)
        
        # Check index exists
        indexes = list(vehicles.list_indexes())
        plate_index_exists = any(
            "plate" in idx.get("key", {}) for idx in indexes
        )
        assert plate_index_exists
    
    def test_inspection_indexes(self, test_db):
        """Test inspection collection indexes"""
        inspections = test_db["inspections"]
        
        # Create compound index
        inspections.create_index([
            ("vehicle_plate", 1),
            ("created_at", -1)
        ])
        
        # Check index exists
        indexes = list(inspections.list_indexes())
        compound_index_exists = any(
            "vehicle_plate" in idx.get("key", {}) and "created_at" in idx.get("key", {})
            for idx in indexes
        )
        assert compound_index_exists

class TestDatabaseValidation:
    """Test data validation and constraints"""
    
    def test_vehicle_duplicate_plate_handling(self, test_db):
        """Test handling of duplicate vehicle plates"""
        vehicles = test_db["vehicles"]
        vehicles.create_index("plate", unique=True)
        
        vehicle_data = {"plate": "DUPLICATE123", "brand": "Honda"}
        
        # First insert should succeed
        result1 = vehicles.insert_one(vehicle_data.copy())
        assert result1.inserted_id is not None
        
        # Second insert should fail
        from pymongo.errors import DuplicateKeyError
        with pytest.raises(DuplicateKeyError):
            vehicles.insert_one(vehicle_data.copy())
    
    def test_inspection_data_validation(self, test_db):
        """Test inspection data validation"""
        inspections = test_db["inspections"]
        
        # Valid data
        valid_data = {
            "vehicle_plate": "ABC123",
            "driver_license": "DL123456789",
            "inspection_type": "damage",
            "images": [],
            "created_at": "2025-09-16T10:00:00Z"
        }
        
        result = inspections.insert_one(valid_data)
        assert result.inserted_id is not None
        
        # Verify data integrity
        saved_inspection = inspections.find_one({"_id": result.inserted_id})
        assert saved_inspection["vehicle_plate"] == "ABC123"
        assert saved_inspection["inspection_type"] == "damage"
