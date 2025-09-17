#!/bin/bash

# Frontend Test Runner Script
# Ejecuta todas las pruebas del frontend con diferentes configuraciones

set -e

echo "🧪 Inspector Vehicular - Frontend Test Runner"
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

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    print_error "No package.json found. Are you in the frontend directory?"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

# Create necessary directories
mkdir -p coverage
mkdir -p test-reports

# Function to run specific test categories
run_unit_tests() {
    print_status "Running unit tests..."
    npm run test -- --reporter=verbose --coverage=false
}

run_integration_tests() {
    print_status "Running integration tests..."
    npm run test -- --run --reporter=verbose src/tests/integration.test.tsx
}

run_component_tests() {
    print_status "Running component tests..."
    npm run test -- --run --reporter=verbose src/tests/*Component*.test.tsx src/tests/*Upload*.test.tsx src/tests/*Results*.test.tsx
}

run_service_tests() {
    print_status "Running service tests..."
    npm run test -- --run --reporter=verbose src/tests/*Service*.test.ts src/tests/*Hook*.test.tsx
}

run_coverage_tests() {
    print_status "Running tests with coverage..."
    npm run test -- --run --coverage --reporter=verbose
}

run_watch_tests() {
    print_status "Running tests in watch mode..."
    npm run test:watch
}

run_build_test() {
    print_status "Testing build process..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Build successful"
        
        # Check if critical files exist in dist
        if [ -f "dist/index.html" ] && [ -f "dist/assets/index*.js" ]; then
            print_success "All build artifacts present"
        else
            print_warning "Some build artifacts missing"
        fi
    else
        print_error "Build failed"
        return 1
    fi
}

run_lint_tests() {
    print_status "Running linting tests..."
    npm run lint
    
    if [ $? -eq 0 ]; then
        print_success "Linting passed"
    else
        print_warning "Linting issues found"
    fi
}

run_type_check() {
    print_status "Running TypeScript type checking..."
    npx tsc --noEmit
    
    if [ $? -eq 0 ]; then
        print_success "Type checking passed"
    else
        print_error "Type checking failed"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "components")
        run_component_tests
        ;;
    "services")
        run_service_tests
        ;;
    "coverage")
        run_coverage_tests
        ;;
    "watch")
        run_watch_tests
        ;;
    "build")
        run_build_test
        ;;
    "lint")
        run_lint_tests
        ;;
    "types")
        run_type_check
        ;;
    "all")
        print_status "Running complete frontend test suite..."
        echo ""
        
        print_status "1/7 - Type Checking"
        run_type_check || print_warning "Type checking failed"
        echo ""
        
        print_status "2/7 - Linting"
        run_lint_tests || print_warning "Linting issues found"
        echo ""
        
        print_status "3/7 - Unit Tests"
        run_unit_tests || print_warning "Some unit tests failed"
        echo ""
        
        print_status "4/7 - Component Tests"
        run_component_tests || print_warning "Some component tests failed"
        echo ""
        
        print_status "5/7 - Service Tests"
        run_service_tests || print_warning "Some service tests failed"
        echo ""
        
        print_status "6/7 - Integration Tests"
        run_integration_tests || print_warning "Some integration tests failed"
        echo ""
        
        print_status "7/7 - Build Test"
        run_build_test || print_warning "Build test failed"
        echo ""
        
        print_status "Running final coverage analysis..."
        run_coverage_tests
        ;;
    "quick")
        print_status "Running quick test suite..."
        run_type_check && run_unit_tests
        ;;
    "ci")
        print_status "Running CI test suite..."
        run_type_check &&
        run_lint_tests &&
        run_coverage_tests &&
        run_build_test
        ;;
    *)
        echo "Usage: $0 {unit|integration|components|services|coverage|watch|build|lint|types|all|quick|ci}"
        echo ""
        echo "Test categories:"
        echo "  unit         - Unit tests only"
        echo "  integration  - Integration tests"
        echo "  components   - Component tests (Upload, Results, etc.)"
        echo "  services     - Service and hook tests"
        echo "  coverage     - All tests with coverage report"
        echo "  watch        - Run tests in watch mode"
        echo "  build        - Test build process"
        echo "  lint         - Run ESLint"
        echo "  types        - TypeScript type checking"
        echo "  all          - Complete test suite"
        echo "  quick        - Quick tests (types + unit)"
        echo "  ci           - CI pipeline tests"
        exit 1
        ;;
esac

# Test results summary
echo ""
echo "=============================================="
print_success "Frontend test execution completed!"
echo ""

if [ -d "coverage" ] && [ "$(ls -A coverage)" ]; then
    print_status "Coverage report generated in: coverage/"
    print_status "To view coverage report:"
    print_status "  open coverage/index.html"
fi

echo ""
print_status "Available npm scripts:"
print_status "  npm run test          - Run all tests"
print_status "  npm run test:watch    - Run tests in watch mode"
print_status "  npm run test:coverage - Run tests with coverage"
print_status "  npm run lint          - Run ESLint"
print_status "  npm run build         - Build for production"
echo ""
print_status "To run specific test files:"
print_status "  npm run test -- src/tests/specific.test.tsx"
echo ""
print_status "To run tests matching pattern:"
print_status "  npm run test -- --grep 'pattern'"
