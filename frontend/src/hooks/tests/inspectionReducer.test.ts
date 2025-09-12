import { inspectionReducer, defaultState } from '@/hooks/useInspectionStore'
import type { AnalyzeImageResponse } from '@/types/inspection'

const baseAnalysis: AnalyzeImageResponse = {
  session_id: 's1',
  damage: [],
  parts_presence: {},
  missing_parts: [],
  color_detected: { color_name: null },
  color_match: true,
  exif_geo: null,
  fraud_flags: [],
  aborted: false,
  images_in_session: 1
}

describe('inspectionReducer', () => {
  it('SET_STEP cambia el paso', () => {
    const st = inspectionReducer(defaultState, { type: 'SET_STEP', step: 'front' })
    expect(st.currentStep).toBe('front')
  })

  it('SET_USER guarda datos usuario', () => {
    const st = inspectionReducer(defaultState, { type: 'SET_USER', info: { name: 'N', idNumber: '1', plate: 'ABC123' } })
    expect(st.userInfo?.plate).toBe('ABC123')
  })

  it('STORE_ANALYSIS agrega análisis', () => {
    const st = inspectionReducer(defaultState, { type: 'STORE_ANALYSIS', key: 'front', analysis: baseAnalysis })
    expect(st.analyses.front?.session_id).toBe('s1')
  })

  it('ABORT marca abortado y pasa a results', () => {
    const st = inspectionReducer(defaultState, { type: 'ABORT', reason: 'FAIL' })
    expect(st.aborted).toBe(true)
    expect(st.currentStep).toBe('results')
  })

  it('RESET genera nuevo sessionId', () => {
    const st = inspectionReducer(defaultState, { type: 'RESET' })
    expect(st.sessionId).not.toBe(defaultState.sessionId)
    expect(st.currentStep).toBe('user-info')
  })
})