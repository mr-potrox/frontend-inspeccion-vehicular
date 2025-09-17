import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    img: ({ children, ...props }: any) => <img {...props}>{children}</img>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock services
vi.mock('../services/inspectionService', () => ({
  getApiVersion: vi.fn().mockResolvedValue({ version: '1.0.0' }),
}));

// Mock ChatOrchestrator component
vi.mock('../components/chatflow/ChatOrchestrator', () => ({
  ChatOrchestrator: () => <div data-testid="chat-orchestrator">Chat Orchestrator</div>
}));

// Mock CoachChat component
vi.mock('../components/common/CoachChat/CoachChat', () => ({
  default: ({ messages }: { messages: string[] }) => (
    <div data-testid="coach-chat">
      {messages.map((msg, i) => <div key={i}>{msg}</div>)}
    </div>
  )
}));

// Mock LoadingSpinner
vi.mock('../components/common/LoadingSpinner', () => ({
  LoadingSpinner: ({ title, message }: { title: string; message: string }) => (
    <div data-testid="loading-spinner">{title}: {message}</div>
  )
}));

// Mock useInspectionStore
vi.mock('../hooks/useInspectionStore', () => ({
  InspectionProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useInspectionStore: () => ({
    state: {},
    setPhoto: vi.fn(),
    setStep: vi.fn(),
  })
}));

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock navigator.userAgent for mobile detection
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
      writable: true
    });
    
    // Mock window.innerWidth for mobile detection
    Object.defineProperty(window, 'innerWidth', {
      value: 375,
      writable: true
    });
  });

  it('shows mobile-only message on desktop', () => {
    // Set desktop width and user agent
    Object.defineProperty(window, 'innerWidth', {
      value: 1024,
      writable: true
    });
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      writable: true
    });
    
    render(<App />);
    
    expect(screen.getByText('Solo disponible en modo móvil')).toBeInTheDocument();
    expect(screen.getByText('Usa tu teléfono o reduce la ventana.')).toBeInTheDocument();
  });

  it('renders welcome screen on mobile', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('👋 Bienvenido a la inspección asistida.')).toBeInTheDocument();
      expect(screen.getByText('Validaremos identidad y vehículo antes de iniciar.')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Iniciar' })).toBeInTheDocument();
    });
  });

  it('shows chat orchestrator after clicking Iniciar', async () => {
    render(<App />);
    
    const iniciarButton = await screen.findByRole('button', { name: 'Iniciar' });
    fireEvent.click(iniciarButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('chat-orchestrator')).toBeInTheDocument();
    });
  });

  it('handles responsive resize events', async () => {
    render(<App />);
    
    // Initially on mobile
    expect(screen.getByRole('button', { name: 'Iniciar' })).toBeInTheDocument();
    
    // Simulate resize to desktop
    Object.defineProperty(window, 'innerWidth', {
      value: 1024,
      writable: true
    });
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      writable: true
    });
    
    fireEvent(window, new Event('resize'));
    
    await waitFor(() => {
      expect(screen.getByText('Solo disponible en modo móvil')).toBeInTheDocument();
    });
  });

  it('displays version mismatch warning when API version differs', async () => {
    const mockGetApiVersion = vi.mocked(await import('../services/inspectionService')).getApiVersion;
    mockGetApiVersion.mockResolvedValueOnce({ version: '2.0.0' });
    
    // Mock environment variable
    vi.stubEnv('VITE_EXPECTED_API_VERSION', '1.0.0');
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Versión API 2.0.0 ≠ esperada 1.0.0/)).toBeInTheDocument();
    });
    
    vi.unstubAllEnvs();
  });

  it('handles API version check failure gracefully', async () => {
    const mockGetApiVersion = vi.mocked(await import('../services/inspectionService')).getApiVersion;
    mockGetApiVersion.mockRejectedValueOnce(new Error('Network error'));
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('No se pudo validar la versión API.')).toBeInTheDocument();
    });
  });

  it('manages application state correctly', async () => {
    render(<App />);
    
    // Test initial state - should show welcome screen
    expect(screen.getByTestId('coach-chat')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Iniciar' })).toBeInTheDocument();
    
    // No error messages should be present initially
    expect(screen.queryByText(/Error/i)).not.toBeInTheDocument();
  });
});
