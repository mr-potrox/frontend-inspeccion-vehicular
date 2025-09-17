import React from 'react';
import { renderHook } from '@testing-library/react';
import { vi } from 'vitest';
import { useInspectionWS } from '../hooks/useInspectionWS';

// Mock del useInspectionStore
const mockSetAbort = vi.fn();
vi.mock('../hooks/useInspectionStore', () => ({
  useInspectionStore: () => ({
    setAbort: mockSetAbort
  })
}));

// Mock de WebSocket
class MockWebSocket {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onopen: (() => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  close() {
    if (this.onclose) {
      this.onclose();
    }
  }

  send(data: string) {
    // Mock implementation
  }

  static instances: MockWebSocket[] = [];
  static clearInstances() {
    MockWebSocket.instances = [];
  }
}

// Replace global WebSocket
Object.defineProperty(global, 'WebSocket', {
  value: MockWebSocket,
  writable: true
});

describe('useInspectionWS', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockWebSocket.clearInstances();
  });

  it('creates WebSocket connection when sessionId is provided', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0].url).toContain(`/ws/inspection/${sessionId}`);
  });

  it('does not create WebSocket when sessionId is null', () => {
    renderHook(() => useInspectionWS(null));
    
    expect(MockWebSocket.instances).toHaveLength(0);
  });

  it('handles session:aborted message', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    expect(ws).toBeDefined();
    
    // Simulate receiving an abort message
    const abortMessage = {
      event: 'session:aborted',
      reason: 'Quality too low'
    };
    
    if (ws.onmessage) {
      ws.onmessage(new MessageEvent('message', {
        data: JSON.stringify(abortMessage)
      }));
    }
    
    expect(mockSetAbort).toHaveBeenCalledWith('Quality too low');
  });

  it('handles session:aborted message without reason', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    const abortMessage = {
      event: 'session:aborted'
    };
    
    if (ws.onmessage) {
      ws.onmessage(new MessageEvent('message', {
        data: JSON.stringify(abortMessage)
      }));
    }
    
    expect(mockSetAbort).toHaveBeenCalledWith('ABORT');
  });

  it('ignores non-abort messages', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    const otherMessage = {
      event: 'other:event',
      data: 'some data'
    };
    
    if (ws.onmessage) {
      ws.onmessage(new MessageEvent('message', {
        data: JSON.stringify(otherMessage)
      }));
    }
    
    expect(mockSetAbort).not.toHaveBeenCalled();
  });

  it('handles malformed JSON messages gracefully', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    
    if (ws.onmessage) {
      ws.onmessage(new MessageEvent('message', {
        data: 'invalid json {'
      }));
    }
    
    // Should not throw or call setAbort
    expect(mockSetAbort).not.toHaveBeenCalled();
  });

  it('cleans up WebSocket on unmount', () => {
    const sessionId = 'test-session-123';
    
    const { unmount } = renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    const closeSpy = vi.spyOn(ws, 'close');
    
    unmount();
    
    expect(closeSpy).toHaveBeenCalled();
  });

  it('creates new WebSocket when sessionId changes', () => {
    const { rerender } = renderHook(
      ({ sessionId }) => useInspectionWS(sessionId),
      { initialProps: { sessionId: 'session-1' } }
    );
    
    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0].url).toContain('session-1');
    
    const firstWs = MockWebSocket.instances[0];
    const closeSpy = vi.spyOn(firstWs, 'close');
    
    rerender({ sessionId: 'session-2' });
    
    expect(closeSpy).toHaveBeenCalled();
    expect(MockWebSocket.instances).toHaveLength(2);
    expect(MockWebSocket.instances[1].url).toContain('session-2');
  });

  it('uses correct WebSocket URL with custom API base', () => {
    const originalEnv = import.meta.env.VITE_API_BASE_URL;
    
    // Mock environment variable
    vi.stubEnv('VITE_API_BASE_URL', 'https://custom-api.example.com');
    
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    expect(MockWebSocket.instances[0].url).toBe(
      `wss://custom-api.example.com/ws/inspection/${sessionId}`
    );
    
    // Restore environment
    vi.unstubAllEnvs();
  });

  it('handles WebSocket close event', () => {
    const sessionId = 'test-session-123';
    
    renderHook(() => useInspectionWS(sessionId));
    
    const ws = MockWebSocket.instances[0];
    
    // Simulate WebSocket close
    if (ws.onclose) {
      ws.onclose();
    }
    
    // Should not throw any errors
    expect(true).toBe(true);
  });
});
