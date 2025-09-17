import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Results from '../components/inspection/Results/Results';

// Mock de las dependencias
vi.mock('../hooks/useInspectionStore', () => ({
  useInspectionStore: vi.fn()
}));

vi.mock('../services/inspectionService', () => ({
  getReportPdf: vi.fn().mockResolvedValue(new Blob()),
}));

// Mock de los componentes hijos
vi.mock('../components/inspection/Results/components/PhotoAnalysis', () => ({
  default: () => <div data-testid="photo-analysis">Photo Analysis Component</div>
}));

vi.mock('../components/inspection/Results/components/DamageSummary', () => ({
  default: () => <div data-testid="damage-summary">Damage Summary Component</div>
}));

vi.mock('../components/inspection/Results/components/QualityIndicators', () => ({
  default: () => <div data-testid="quality-indicators">Quality Indicators Component</div>
}));

// Import the mocked hook after mock definition
import { useInspectionStore } from '../hooks/useInspectionStore';

const mockReset = vi.fn();

const mockProps = {
  onBack: vi.fn(),
  onReset: mockReset
};

const mockBaseState = {
  currentStep: 'results' as const,
  sessionId: 'test-session-123',
  finalizeResult: {
    inspection_id: 'test-123',
    session_id: 'test-session-123',
    status: 'completed' as const,
    damage_summary: {
      total_damages: 2,
      severity_distribution: { minor: 1, major: 1 }
    }
  },
  aborted: false,
  userInfo: {
    name: 'John Doe',
    idNumber: '12345678',
    plate: 'ABC123'
  },
  photos: {},
  previews: {
    front: 'mock-image-url.jpg',
    back: 'mock-image-url-back.jpg'
  },
  geoData: {
    front: { lat: 40.7128, lng: -74.0060 }
  },
  analyses: {
    front: {
      parts: [{ name: 'hood', confidence: 0.95 }],
      damage: [{ type: 'scratch', severity: 'minor' }],
      quality_status: 'ok'
    }
  },
  labels: {
    damage_labels: ['scratch', 'dent'],
    part_labels: ['hood', 'door', 'bumper']
  }
};

describe('Results Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useInspectionStore as any).mockReturnValue({
      state: mockBaseState,
      reset: mockReset
    });
  });

  it('renders inspection results correctly', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('ABC123')).toBeInTheDocument();
    expect(screen.getByTestId('damage-summary')).toBeInTheDocument();
  });

  it('displays user information', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('ABC123')).toBeInTheDocument();
  });

  it('shows damage summary', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByTestId('damage-summary')).toBeInTheDocument();
  });

  it('displays photo analysis results', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByTestId('photo-analysis')).toBeInTheDocument();
  });

  it('handles PDF download', () => {
    render(<Results {...mockProps} />);
    
    const downloadButton = screen.getByText(/Descargar PDF/i);
    expect(downloadButton).toBeInTheDocument();
    
    fireEvent.click(downloadButton);
  });

  it('handles back navigation', () => {
    render(<Results {...mockProps} />);
    
    const backButton = screen.getByText(/Atrás/i);
    fireEvent.click(backButton);
    
    expect(mockProps.onBack).toHaveBeenCalled();
  });

  it('shows new inspection option', () => {
    render(<Results {...mockProps} />);
    
    const newInspectionButton = screen.getByText(/Nueva Inspección/i);
    expect(newInspectionButton).toBeInTheDocument();
  });

  it('toggles damage visibility filters', () => {
    render(<Results {...mockProps} />);
    
    const damageSection = screen.getByTestId('damage-summary');
    expect(damageSection).toBeInTheDocument();
  });

  it('handles PDF disabled state', () => {
    (useInspectionStore as any).mockReturnValue({
      state: {
        ...mockBaseState,
        finalizeResult: null
      },
      reset: mockReset
    });

    render(<Results {...mockProps} />);
    
    const downloadButton = screen.queryByText(/Descargar PDF/i);
    expect(downloadButton).toBeNull();
  });

  it('displays aborted inspection message', () => {
    (useInspectionStore as any).mockReturnValue({
      state: {
        ...mockBaseState,
        aborted: true,
        abortReason: 'Quality too low'
      },
      reset: mockReset
    });

    render(<Results {...mockProps} />);
    
    expect(screen.getByText(/Quality too low/i)).toBeInTheDocument();
  });

  it('handles empty results gracefully', () => {
    (useInspectionStore as any).mockReturnValue({
      state: {
        ...mockBaseState,
        finalizeResult: null,
        analyses: {}
      },
      reset: mockReset
    });

    render(<Results {...mockProps} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('displays aborted inspection message', () => {
    (useInspectionStore as any).mockReturnValue({
      state: {
        ...mockBaseState,
        aborted: true,
        abortReason: 'Quality too low'
      },
      reset: mockReset
    });

    render(<Results {...mockProps} />);
    
    expect(screen.getByText(/Quality too low/i)).toBeInTheDocument();
  });

  it('handles empty results gracefully', () => {
    (useInspectionStore as any).mockReturnValue({
      state: {
        ...mockBaseState,
        finalizeResult: null,
        analyses: {}
      },
      reset: mockReset
    });

    render(<Results {...mockProps} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('displays quality indicators', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByTestId('quality-indicators')).toBeInTheDocument();
  });

  it('shows damage type filters', () => {
    render(<Results {...mockProps} />);
    
    expect(screen.getByTestId('damage-summary')).toBeInTheDocument();
  });

  it('handles start new inspection', () => {
    render(<Results {...mockProps} />);
    
    const newInspectionButton = screen.getByText(/Nueva Inspección/i);
    fireEvent.click(newInspectionButton);
    
    expect(mockProps.onReset).toHaveBeenCalled();
  });
});
