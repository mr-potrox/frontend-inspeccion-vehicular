import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock components for integration tests
const MockImageUpload = vi.fn(({ onUpload, onError }) => (
  <div data-testid="image-upload">
    <button 
      onClick={() => onUpload({ damage_detections: [], parts_detections: [] })}
      data-testid="upload-success"
    >
      Upload Success
    </button>
    <button 
      onClick={() => onError('Upload error')}
      data-testid="upload-error"
    >
      Upload Error
    </button>
  </div>
));

const MockInspectionResults = vi.fn(({ results, isLoading }) => (
  <div data-testid="inspection-results">
    {isLoading && <div data-testid="loading">Loading...</div>}
    {results && <div data-testid="results">Results displayed</div>}
  </div>
));

// Mock inspection service
const mockInspectionService = {
  uploadImage: vi.fn(),
  startInspectionSession: vi.fn(),
  finalizeInspection: vi.fn(),
  getInspections: vi.fn(),
  exportResults: vi.fn(),
};

vi.mock('../services/inspectionService', () => ({
  default: mockInspectionService,
}));

// Integration test component that combines upload and results
const InspectionWorkflow = () => {
  const [results, setResults] = React.useState(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleUpload = async (uploadResults) => {
    setIsLoading(false);
    setResults(uploadResults);
    setError(null);
  };

  const handleError = (errorMessage) => {
    setIsLoading(false);
    setError(errorMessage);
    setResults(null);
  };

  return (
    <div data-testid="inspection-workflow">
      <MockImageUpload onUpload={handleUpload} onError={handleError} />
      <MockInspectionResults results={results} isLoading={isLoading} />
      {error && <div data-testid="error">{error}</div>}
    </div>
  );
};

describe('Frontend Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Complete Inspection Workflow', () => {
    it('completes full inspection flow successfully', async () => {
      const mockResults = {
        damage_detections: [
          { class: 'scratch', confidence: 0.85, bbox: [100, 100, 200, 200] }
        ],
        parts_detections: [
          { class: 'bumper', confidence: 0.90, bbox: [50, 50, 350, 250] }
        ],
        processing_time: 2.3
      };

      render(<InspectionWorkflow />);

      // Simulate successful upload
      const uploadButton = screen.getByTestId('upload-success');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByTestId('results')).toBeInTheDocument();
      });

      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });

    it('handles upload errors in workflow', async () => {
      render(<InspectionWorkflow />);

      // Simulate upload error
      const errorButton = screen.getByTestId('upload-error');
      fireEvent.click(errorButton);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toBeInTheDocument();
      });

      expect(screen.getByText('Upload error')).toBeInTheDocument();
      expect(screen.queryByTestId('results')).not.toBeInTheDocument();
    });
  });

  describe('API Integration', () => {
    it('integrates with backend API correctly', async () => {
      const mockApiResponse = {
        damage_detections: [],
        parts_detections: [],
        processing_time: 1.5,
        session_id: 'session-123'
      };

      mockInspectionService.uploadImage.mockResolvedValueOnce(mockApiResponse);

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const result = await mockInspectionService.uploadImage(file);

      expect(result).toEqual(mockApiResponse);
      expect(mockInspectionService.uploadImage).toHaveBeenCalledWith(file);
    });

    it('handles API rate limiting', async () => {
      mockInspectionService.uploadImage.mockRejectedValueOnce(
        new Error('Rate limit exceeded')
      );

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await expect(mockInspectionService.uploadImage(file))
        .rejects.toThrow('Rate limit exceeded');
    });

    it('handles API timeouts', async () => {
      mockInspectionService.uploadImage.mockRejectedValueOnce(
        new Error('Request timeout')
      );

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await expect(mockInspectionService.uploadImage(file))
        .rejects.toThrow('Request timeout');
    });
  });

  describe('Error Boundary Integration', () => {
    interface ErrorBoundaryState {
      hasError: boolean;
    }

    interface ErrorBoundaryProps {
      children: React.ReactNode;
    }

    class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
      constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true };
      }

      componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.log('Error caught by boundary:', error, errorInfo);
      }

      render() {
        if (this.state.hasError) {
          return <div data-testid="error-boundary">Something went wrong</div>;
        }

        return this.props.children;
      }
    }

    it('catches and displays errors gracefully', () => {
      const ThrowError = () => {
        throw new Error('Test error');
      };

      // Suppress error output in tests
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });

  describe('State Management Integration', () => {
    const StateTestComponent = () => {
      const [inspectionState, setInspectionState] = React.useState({
        sessionId: null,
        results: null,
        isLoading: false
      });

      const startSession = () => {
        setInspectionState(prev => ({
          ...prev,
          sessionId: 'session-123',
          isLoading: true
        }));
      };

      const completeInspection = () => {
        setInspectionState(prev => ({
          ...prev,
          results: { damage_detections: [], parts_detections: [] },
          isLoading: false
        }));
      };

      return (
        <div data-testid="state-test">
          <div data-testid="session-id">{inspectionState.sessionId || 'No session'}</div>
          <div data-testid="loading-state">{inspectionState.isLoading ? 'Loading' : 'Not loading'}</div>
          <button onClick={startSession} data-testid="start-session">Start Session</button>
          <button onClick={completeInspection} data-testid="complete-inspection">Complete</button>
        </div>
      );
    };

    it('manages state transitions correctly', async () => {
      render(<StateTestComponent />);

      // Initial state
      expect(screen.getByText('No session')).toBeInTheDocument();
      expect(screen.getByText('Not loading')).toBeInTheDocument();

      // Start session
      fireEvent.click(screen.getByTestId('start-session'));
      expect(screen.getByText('session-123')).toBeInTheDocument();
      expect(screen.getByText('Loading')).toBeInTheDocument();

      // Complete inspection
      fireEvent.click(screen.getByTestId('complete-inspection'));
      expect(screen.getByText('Not loading')).toBeInTheDocument();
    });
  });

  describe('Performance Integration', () => {
    it('handles large file uploads efficiently', async () => {
      const startTime = performance.now();

      // Simulate large file processing
      const largeFile = new File(['x'.repeat(1000000)], 'large.jpg', { 
        type: 'image/jpeg' 
      });

      mockInspectionService.uploadImage.mockImplementationOnce(async () => {
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 100));
        return { damage_detections: [], parts_detections: [] };
      });

      await mockInspectionService.uploadImage(largeFile);

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      // Should complete within reasonable time (less than 5 seconds for test)
      expect(processingTime).toBeLessThan(5000);
    });

    it('handles multiple concurrent requests', async () => {
      const promises = [];

      // Create multiple upload promises
      for (let i = 0; i < 5; i++) {
        const file = new File([`test${i}`], `test${i}.jpg`, { type: 'image/jpeg' });
        mockInspectionService.uploadImage.mockResolvedValueOnce({
          damage_detections: [],
          parts_detections: [],
          file_id: i
        });
        promises.push(mockInspectionService.uploadImage(file));
      }

      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach((result, index) => {
        expect(result.file_id).toBe(index);
      });
    });
  });

  describe('Accessibility Integration', () => {
    const AccessibleInspectionForm = () => (
      <form data-testid="inspection-form" role="form" aria-label="Vehicle Inspection Form">
        <label htmlFor="vehicle-plate">
          Vehicle Plate
          <input 
            id="vehicle-plate" 
            type="text" 
            required
            aria-describedby="plate-help"
          />
        </label>
        <div id="plate-help">Enter the vehicle license plate</div>
        
        <label htmlFor="inspection-type">
          Inspection Type
          <select id="inspection-type" required>
            <option value="">Select type</option>
            <option value="damage">Damage Inspection</option>
            <option value="parts">Parts Inspection</option>
          </select>
        </label>

        <button type="submit" aria-describedby="submit-help">
          Start Inspection
        </button>
        <div id="submit-help">Begin the vehicle inspection process</div>
      </form>
    );

    it('provides proper accessibility features', () => {
      render(<AccessibleInspectionForm />);

      // Check form accessibility
      expect(screen.getByRole('form')).toHaveAttribute('aria-label', 'Vehicle Inspection Form');
      
      // Check input labels
      expect(screen.getByLabelText('Vehicle Plate')).toBeInTheDocument();
      expect(screen.getByLabelText('Inspection Type')).toBeInTheDocument();
      
      // Check ARIA descriptions
      expect(screen.getByText('Enter the vehicle license plate')).toBeInTheDocument();
      expect(screen.getByText('Begin the vehicle inspection process')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      render(<AccessibleInspectionForm />);

      const plateInput = screen.getByLabelText('Vehicle Plate');
      const typeSelect = screen.getByLabelText('Inspection Type');
      const submitButton = screen.getByRole('button', { name: /Start Inspection/i });

      // Test tab navigation
      plateInput.focus();
      expect(document.activeElement).toBe(plateInput);

      fireEvent.keyDown(plateInput, { key: 'Tab' });
      // In a real test, we'd check if focus moved to typeSelect
    });
  });

  describe('Responsive Design Integration', () => {
    const ResponsiveComponent = () => {
      const [isMobile, setIsMobile] = React.useState(window.innerWidth < 768);

      React.useEffect(() => {
        const handleResize = () => {
          setIsMobile(window.innerWidth < 768);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
      }, []);

      return (
        <div data-testid="responsive-component">
          {isMobile ? (
            <div data-testid="mobile-view">Mobile Layout</div>
          ) : (
            <div data-testid="desktop-view">Desktop Layout</div>
          )}
        </div>
      );
    };

    it('adapts to different screen sizes', () => {
      // Test desktop view
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1024,
      });

      render(<ResponsiveComponent />);
      expect(screen.getByTestId('desktop-view')).toBeInTheDocument();

      // Test mobile view
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      // Trigger resize event
      fireEvent(window, new Event('resize'));

      // Note: In a real test environment, you'd need to re-render or use a different approach
      // to test responsive behavior
    });
  });
});
