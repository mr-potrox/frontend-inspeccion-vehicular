"""
Pytest configuration file
"""
import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Pytest configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_models: mark test as requiring ML models"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['integration', 'slow'] for marker in item.iter_markers()):
            item.add_marker('unit')
        
        # Add markers based on test file names
        if 'integration' in item.fspath.basename:
            item.add_marker('integration')
        
        if 'test_yolo' in item.fspath.basename or 'test_services' in item.fspath.basename:
            item.add_marker('requires_models')
        
        if 'test_database' in item.fspath.basename:
            item.add_marker('requires_db')
