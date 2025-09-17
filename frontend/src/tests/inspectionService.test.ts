import { vi } from 'vitest';
import { 
  analyzeImage, 
  finalizeInspection, 
  getApiVersion, 
  getHealth, 
  verifyVehicle,
  verifyIdentity,
  getVehicleHistory,
  getReportPdf
} from '../services/inspectionService';

// Mock fetch global
global.fetch = vi.fn();

describe('Inspection Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Clear sessionStorage mock
    Object.defineProperty(window, 'sessionStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn()
      },
      writable: true
    });
  });

  describe('analyzeImage', () => {
    it('sends image analysis request with correct parameters', async () => {
      const mockResponse = {
        success: true,
        parts: [{ name: 'hood', confidence: 0.95 }],
        damage: [{ type: 'scratch', severity: 'minor' }],
        quality_status: 'ok'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const params = {
        file,
        sessionId: 'test-session',
        plate: 'ABC123',
        lat: 40.7128,
        lon: -74.0060,
        debug: false,
        photoKey: 'front'
      };

      const result = await analyzeImage(params);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/inspection/analyze'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles analysis errors gracefully', async () => {
      // Mock fetch to throw error directly
      const originalFetch = global.fetch;
      global.fetch = vi.fn().mockImplementation(() => 
        Promise.reject(new Error('Network error'))
      );

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const params = {
        file,
        sessionId: 'test-session',
        plate: 'ABC123',
        photoKey: 'front'
      };

      await expect(analyzeImage(params)).rejects.toThrow('Network error');
      
      // Restore original fetch
      global.fetch = originalFetch;
    });
  });

  describe('finalizeInspection', () => {
    it('finalizes inspection successfully', async () => {
      const mockResponse = {
        success: true,
        inspection_id: 'insp-123',
        report_url: 'https://example.com/report/123'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await finalizeInspection('test-session', 'ABC123', 0.5, 0.7);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/inspection/finalize'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getApiVersion', () => {
    it('retrieves API version information', async () => {
      const mockVersion = {
        version: '1.0.0',
        build: '123',
        commit: 'abc123'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockVersion
      });

      const result = await getApiVersion();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/model/info'),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      );
      expect(result).toEqual(mockVersion);
    });
  });

  describe('getHealth', () => {
    it('retrieves health status', async () => {
      const mockHealth = {
        status: 'healthy',
        model_version: '1.0.0',
        models: {
          damage: { name: 'damage_model', path: '/models/damage', default_conf: 0.5 },
          parts: { name: 'parts_model', path: '/models/parts', default_conf: 0.5 }
        }
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth
      });

      const result = await getHealth();

      expect(result).toEqual(mockHealth);
    });
  });

  describe('verifyVehicle', () => {
    it('verifies vehicle successfully', async () => {
      const mockVehicle = {
        found: true,
        data: {
          plate: 'ABC123',
          brand: 'Toyota',
          model: 'Corolla',
          year: '2020'
        }
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicle
      });

      const result = await verifyVehicle('ABC123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/inspection/verify?plate=ABC123'),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      );
      expect(result).toEqual(mockVehicle);
    });

    it('uses cached vehicle data when available', async () => {
      const cachedData = {
        found: true,
        data: { plate: 'ABC123', brand: 'Toyota' }
      };
      
      const cachedItem = {
        t: Date.now() - 5000, // 5 seconds ago, within TTL
        v: cachedData
      };

      (window.sessionStorage.getItem as any).mockReturnValueOnce(JSON.stringify(cachedItem));

      const result = await verifyVehicle('ABC123');

      expect(result).toEqual(cachedData);
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('verifyIdentity', () => {
    it('verifies identity successfully', async () => {
      const mockIdentity = {
        valid: true,
        matched_driver: { name: 'John Doe', id: '123' }
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockIdentity
      });

      const payload = {
        name: 'John Doe',
        document: '12345678'
      };

      const result = await verifyIdentity(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/identity/verify'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
      );
      expect(result).toEqual(mockIdentity);
    });
  });

  describe('getVehicleHistory', () => {
    it('retrieves vehicle history', async () => {
      const mockHistory = {
        plate: 'ABC123',
        infractions: 2,
        previous_owners: 1,
        tech_ok: true,
        notes: ['Maintenance up to date']
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistory
      });

      const result = await getVehicleHistory('ABC123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/vehicle/history?plate=ABC123'),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      );
      expect(result).toEqual(mockHistory);
    });
  });

  describe('getReportPdf', () => {
    it('retrieves PDF report', async () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob
      });

      const result = await getReportPdf('insp-123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/inspection/report/insp-123/pdf'),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      );
      expect(result).toEqual(mockBlob);
    });
  });

  describe('Error handling', () => {
    it('handles HTTP errors', async () => {
      // Mock fetch to return HTTP error response
      const originalFetch = global.fetch;
      global.fetch = vi.fn().mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error'
        } as Response)
      );

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const params = {
        file,
        sessionId: 'test-session',
        plate: 'ABC123',
        photoKey: 'front'
      };

      await expect(analyzeImage(params)).rejects.toThrow('HTTP 500');
      
      // Restore original fetch
      global.fetch = originalFetch;
    });

    it('handles network timeouts', async () => {
      (global.fetch as any).mockImplementationOnce(() => 
        new Promise((_, reject) => {
          setTimeout(() => reject(new Error('AbortError')), 100);
        })
      );

      await expect(getApiVersion()).rejects.toThrow();
    });
  });
});
