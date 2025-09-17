import { vi } from 'vitest';
import { inspectionReducer, defaultState } from '../useInspectionStore';

describe('Inspection Reducer', () => {
  it('handles SET_USER action', () => {
    const userInfo = {
      name: 'John Doe',
      idNumber: '12345678',
      plate: 'ABC123'
    };
    
    const action = { type: 'SET_USER' as const, info: userInfo };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.userInfo).toEqual(userInfo);
  });

  it('handles SET_PHOTO action', () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const geo = { lat: 40.7128, lon: -74.0060 };
    
    const action = { 
      type: 'SET_PHOTO' as const, 
      key: 'front' as any,
      file,
      geo
    };
    
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.photos.front).toBe(file);
    expect(newState.geoData.front).toEqual(geo);
    expect(newState.previews.front).toMatch(/^blob:/);
  });

  it('handles STORE_ANALYSIS action', () => {
    const analysis = {
      parts: [{ name: 'hood', confidence: 0.95 }],
      damage: [{ type: 'scratch', severity: 'minor' }],
      quality_status: 'ok'
    } as any;
    
    const action = { 
      type: 'STORE_ANALYSIS' as const, 
      key: 'front' as any,
      analysis
    };
    
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.analyses.front).toEqual(analysis);
  });

  it('handles STORE_FINAL action', () => {
    const finalResults = {
      inspection_id: 'insp-123',
      overall_damage: 'minor'
    } as any;
    
    const action = { type: 'STORE_FINAL' as const, result: finalResults };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.finalizeResult).toEqual(finalResults);
  });

  it('handles SET_STEP action', () => {
    const action = { type: 'SET_STEP' as const, step: 'RESULTS' };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.currentStep).toBe('RESULTS');
  });

  it('handles ABORT action', () => {
    const action = { type: 'ABORT' as const, reason: 'Quality too low' };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.aborted).toBe(true);
    expect(newState.abortReason).toBe('Quality too low');
    expect(newState.currentStep).toBe('RESULTS');
  });

  it('handles ADD_NOTE action', () => {
    const action = { type: 'ADD_NOTE' as const, note: 'Test note' };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.notes).toContain('Test note');
    expect(newState.notes).toHaveLength(1);
  });

  it('handles SET_THRESHOLDS action', () => {
    const thresholds = {
      blur_threshold: 0.5,
      very_blur_threshold: 0.3
    } as any;
    
    const action = { type: 'SET_THRESHOLDS' as const, data: thresholds };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.quality).toEqual(thresholds);
  });

  it('handles SET_IDENTITY action', () => {
    const identity = { valid: true, name: 'John Doe', document: '12345' };
    const action = { type: 'SET_IDENTITY' as const, data: identity };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.identity).toEqual(identity);
  });

  it('handles SET_HISTORY action', () => {
    const history = { infractions: 2, tech_ok: true };
    const action = { type: 'SET_HISTORY' as const, data: history };
    const newState = inspectionReducer(defaultState, action);
    
    expect(newState.vehicleHistory).toEqual(history);
  });

  it('handles RESET action', () => {
    const modifiedState = {
      ...defaultState,
      currentStep: 'RESULTS',
      userInfo: { name: 'John', idNumber: '123', plate: 'ABC123' }
    };
    
    const action = { type: 'RESET' as const };
    const newState = inspectionReducer(modifiedState, action);
    
    expect(newState.currentStep).toBe('WELCOME');
    expect(newState.userInfo).toBeUndefined();
    expect(newState.sessionId).toBeDefined();
    expect(newState.sessionId).not.toBe(modifiedState.sessionId);
  });

  it('returns current state for unknown action', () => {
    const unknownAction = { type: 'UNKNOWN_ACTION' as any };
    const newState = inspectionReducer(defaultState, unknownAction);
    
    expect(newState).toBe(defaultState);
  });

  describe('State immutability', () => {
    it('does not mutate original state', () => {
      const originalState = { ...defaultState };
      const action = { type: 'SET_STEP' as const, step: 'RESULTS' };
      
      inspectionReducer(defaultState, action);
      
      expect(defaultState.currentStep).toBe(originalState.currentStep);
    });

    it('creates new state object for SET_PHOTO', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const action = { 
        type: 'SET_PHOTO' as const, 
        key: 'front' as any,
        file
      };
      
      const newState = inspectionReducer(defaultState, action);
      
      expect(newState).not.toBe(defaultState);
      expect(newState.photos).not.toBe(defaultState.photos);
      expect(newState.previews).not.toBe(defaultState.previews);
    });
  });

  describe('Photo management', () => {
    it('removes photo when file is null', () => {
      const stateWithPhoto = {
        ...defaultState,
        photos: { front: new File(['test'], 'test.jpg') },
        previews: { front: 'blob:test-url' }
      };
      
      const action = { 
        type: 'SET_PHOTO' as const, 
        key: 'front' as any,
        file: null
      };
      
      const newState = inspectionReducer(stateWithPhoto, action);
      
      expect(newState.photos.front).toBeUndefined();
      expect(newState.previews.front).toBeUndefined();
    });

    it('handles multiple photos', () => {
      const frontFile = new File(['front'], 'front.jpg', { type: 'image/jpeg' });
      const rearFile = new File(['rear'], 'rear.jpg', { type: 'image/jpeg' });
      
      let state = defaultState;
      
      state = inspectionReducer(state, { 
        type: 'SET_PHOTO', 
        key: 'front', 
        file: frontFile 
      });
      
      state = inspectionReducer(state, { 
        type: 'SET_PHOTO', 
        key: 'rear', 
        file: rearFile 
      });
      
      expect(state.photos.front).toBe(frontFile);
      expect(state.photos.rear).toBe(rearFile);
      expect(state.previews.front).toMatch(/^blob:/);
      expect(state.previews.rear).toMatch(/^blob:/);
    });
  });
});
