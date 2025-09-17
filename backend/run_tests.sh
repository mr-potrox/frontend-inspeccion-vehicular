#!/bin/bash

# Backend Test Runner Script
# Ejecuta todas las pruebas del backend con diferentes configuraciones

set -e

echo "🧪 Inspector Vehicular - Backend Test Runner"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not detected. Activating..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please create one first."
        exit 1
    fi
fi

# Install test dependencies
print_status "Installing test dependencies..."
pip install -r requirements-test.txt

# Create necessary directories
mkdir -p htmlcov
mkdir -p test-reports

# Function to run specific test categories
run_unit_tests() {
    print_status "Running unit tests..."
    pytest tests/ -m "unit and not requires_models and not requires_db" \
        --junitxml=test-reports/unit-tests.xml \
        -v
}

run_integration_tests() {
    print_status "Running integration tests..."
    pytest tests/ -m "integration" \
        --junitxml=test-reports/integration-tests.xml \
        -v
}

run_database_tests() {
    print_status "Running database tests..."
    # Check if MongoDB is running
    if ! pgrep -x "mongod" > /dev/null; then
        print_warning "MongoDB not running. Starting local instance..."
        # Try to start MongoDB (adjust command as needed)
        mongod --fork --logpath /tmp/mongodb-test.log --dbpath /tmp/mongodb-test-data || {
            print_warning "Could not start MongoDB. Skipping database tests."
            return 1
        }
    fi
    
    pytest tests/ -m "requires_db" \
        --junitxml=test-reports/database-tests.xml \
        -v
}

run_model_tests() {
    print_status "Running model tests (mocked)..."
    pytest tests/ -m "requires_models" \
        --junitxml=test-reports/model-tests.xml \
        -v
}

run_all_tests() {
    print_status "Running all tests with coverage..."
    pytest tests/ \
        --cov=app \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml:test-reports/coverage.xml \
        --junitxml=test-reports/all-tests.xml \
        -v
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "database")
        run_database_tests
        ;;
    "models")
        run_model_tests
        ;;
    "all")
        print_status "Running complete test suite..."
        echo ""
        
        print_status "1/4 - Unit Tests"
        run_unit_tests || print_warning "Some unit tests failed"
        echo ""
        
        print_status "2/4 - Integration Tests"
        run_integration_tests || print_warning "Some integration tests failed"
        echo ""
        
        print_status "3/4 - Database Tests"
        run_database_tests || print_warning "Some database tests failed"
        echo ""
        
        print_status "4/4 - Model Tests"
        run_model_tests || print_warning "Some model tests failed"
        echo ""
        
        print_status "Running complete coverage analysis..."
        run_all_tests
        ;;
    "coverage")
        run_all_tests
        ;;
    "quick")
        print_status "Running quick test suite (unit tests only)..."
        run_unit_tests
        ;;
    *)
        echo "Usage: $0 {unit|integration|database|models|all|coverage|quick}"
        echo ""
        echo "Test categories:"
        echo "  unit        - Unit tests (fast, no external dependencies)"
        echo "  integration - Integration tests (API endpoints, workflows)"
        echo "  database    - Database tests (requires MongoDB)"
        echo "  models      - Model tests (mocked ML models)"
        echo "  all         - All tests with coverage report"
        echo "  coverage    - Full coverage analysis"
        echo "  quick       - Quick unit tests only"
        exit 1
        ;;
esac

# Test results summary
echo ""
echo "=============================================="
print_success "Test execution completed!"
echo ""
print_status "Test reports generated in: test-reports/"
print_status "Coverage report generated in: htmlcov/"
echo ""
print_status "To view coverage report:"
print_status "  open htmlcov/index.html"
echo ""
print_status "To run specific tests:"
print_status "  pytest tests/test_specific.py::TestClass::test_method -v"
echo ""
print_status "To run with specific markers:"
print_status "  pytest tests/ -m 'unit and not slow' -v"
