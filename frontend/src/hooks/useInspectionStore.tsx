import React, { createContext, useContext, useMemo, useReducer } from 'react'
import { InspectionState, PhotoKey, AnalyzeImageResponse, FinalizeResponse, QualityThresholds } from '@/types/inspection'

export type Action =
  | { type: 'SET_PHOTO'; key: PhotoKey; file: File | null; geo?: { lat: number; lon: number } }
  | { type: 'SET_STEP'; step: string }
  | { type: 'SET_USER'; info: { name: string; idNumber: string; plate: string } }
  | { type: 'ADD_NOTE'; note: string }
  | { type: 'STORE_ANALYSIS'; key: PhotoKey; analysis: AnalyzeImageResponse }
  | { type: 'ABORT'; reason: string }
  | { type: 'STORE_FINAL'; result: FinalizeResponse }
  | { type: 'SET_THRESHOLDS'; data: QualityThresholds }
  | { type: 'SET_IDENTITY'; data: { valid: boolean; name: string; document: string } }
  | { type: 'SET_HISTORY'; data: any }
  | { type: 'RESET' }

export const newSessionId = () =>
  (crypto?.randomUUID ? crypto.randomUUID() : 'sess_' + Math.random().toString(36).slice(2))

export const defaultState: InspectionState = {
  currentStep: 'WELCOME',
  sessionId: newSessionId(),
  photos: {},
  previews: {},
  analyses: {},
  notes: [],
  aborted: false,
  error: null,
  finalizeResult: null,
  userInfo: undefined,
  geoData: {},
  quality: undefined,
  identity: null,
  vehicleHistory: null
}

export function inspectionReducer(state: InspectionState, action: Action): InspectionState {
  switch (action.type) {
    case 'SET_PHOTO': {
      const previews = { ...state.previews }
      const photos = { ...state.photos }
      const geoData = { ...(state.geoData || {}) }
      if (action.file) {
        photos[action.key] = action.file
        if (previews[action.key]) URL.revokeObjectURL(previews[action.key]!)
        previews[action.key] = URL.createObjectURL(action.file)
        if (action.geo) geoData[action.key] = action.geo
      } else {
        if (previews[action.key]) URL.revokeObjectURL(previews[action.key]!)
        delete photos[action.key]; delete previews[action.key]; delete geoData[action.key]
      }
      return { ...state, photos, previews, geoData }
    }
    case 'SET_STEP':
      return { ...state, currentStep: action.step }
    case 'SET_USER':
      return { ...state, userInfo: action.info }
    case 'ADD_NOTE':
      return { ...state, notes: [...state.notes, action.note] }
    case 'STORE_ANALYSIS':
      return { ...state, analyses: { ...state.analyses, [action.key]: action.analysis } }
    case 'ABORT':
      return { ...state, aborted: true, abortReason: action.reason, currentStep: 'RESULTS' }
    case 'STORE_FINAL':
      return { ...state, finalizeResult: action.result }
    case 'SET_THRESHOLDS':
      return { ...state, quality: action.data }
    case 'SET_IDENTITY':
      return { ...state, identity: action.data }
    case 'SET_HISTORY':
      return { ...state, vehicleHistory: action.data }
    case 'RESET': {
      Object.values(state.previews).forEach(u => u && URL.revokeObjectURL(u))
      return { ...defaultState, sessionId: newSessionId() }
    }
    default:
      return state
  }
}

function reducer(s: InspectionState, a: Action) { return inspectionReducer(s, a) }

type Ctx = {
  state: InspectionState
  setPhoto: (k: PhotoKey, f: File | null, geo?: { lat: number; lon: number }) => void
  setStep: (s: string) => void
  setUserInfo: (info: { name: string; idNumber: string; plate: string }) => void
  addNote: (t: string) => void
  storeAnalysis: (k: PhotoKey, a: AnalyzeImageResponse) => void
  setAbort: (reason: string) => void
  storeFinalize: (r: FinalizeResponse) => void
  setQuality: (q: QualityThresholds) => void
  setIdentity: (d: { valid: boolean; name: string; document: string }) => void
  setHistory: (d: any) => void
  reset: () => void
}

const InspectionContext = createContext<Ctx | undefined>(undefined)

export function InspectionProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, defaultState)
  const api: Ctx = useMemo(() => ({
    state,
    setPhoto: (k, f, geo) => dispatch({ type: 'SET_PHOTO', key: k, file: f, geo }),
    setStep: (s) => dispatch({ type: 'SET_STEP', step: s }),
    setUserInfo: (info) => dispatch({ type: 'SET_USER', info }),
    addNote: (t) => dispatch({ type: 'ADD_NOTE', note: t }),
    storeAnalysis: (k, a) => dispatch({ type: 'STORE_ANALYSIS', key: k, analysis: a }),
    setAbort: (r) => dispatch({ type: 'ABORT', reason: r }),
    storeFinalize: (r) => dispatch({ type: 'STORE_FINAL', result: r }),
    setQuality: (q) => dispatch({ type: 'SET_THRESHOLDS', data: q }),
    setIdentity: (d) => dispatch({ type: 'SET_IDENTITY', data: d }),
    setHistory: (d) => dispatch({ type: 'SET_HISTORY', data: d }),
    reset: () => dispatch({ type: 'RESET' })
  }), [state])
  return <InspectionContext.Provider value={api}>{children}</InspectionContext.Provider>
}

export function useInspectionStore() {
  const ctx = useContext(InspectionContext)
  if (!ctx) throw new Error('useInspectionStore must be used within an InspectionProvider')
  return ctx
}