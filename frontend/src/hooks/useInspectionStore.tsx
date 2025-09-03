import React, { createContext, useContext, useMemo, useState } from 'react'
import { InspectionState, PhotoKey } from '@/types/inspection'

type InspectionContextType = {
  state: InspectionState
  setPhoto: (k: PhotoKey, f: File | null, geo?: { lat: number; lon: number }) => void
  setPreview: (k: PhotoKey, url?: string) => void
  setStep: (s: InspectionState['currentStep']) => void
  reset: () => void
  addNote: (t: string) => void
  setUserInfo: (info: { name: string; idNumber: string; plate: string }) => void
}

const defaultState: InspectionState = {
  currentStep: 'user-info',
  photos: {},
  previews: {},
  qualityResult: null,
  detectionResult: null,
  isProcessing: false,
  notes: [],
  error: null,
  userInfo: undefined,
  geoData: {}
}

// Cambia el valor inicial a undefined para forzar el error si no está envuelto
const InspectionContext = createContext<InspectionContextType | undefined>(undefined)

export function InspectionProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<InspectionState>(defaultState)

  const setPhoto = (k: PhotoKey, f: File | null, geo?: { lat: number; lon: number }) => {
    setState((s) => {
      const next = { ...s, photos: { ...s.photos }, previews: { ...s.previews }, geoData: { ...s.geoData } }
      if (f) {
        next.photos[k] = f
        next.previews[k] = URL.createObjectURL(f)
        if (geo) next.geoData[k] = geo
      } else {
        delete next.photos[k]
        if (next.previews[k]) { URL.revokeObjectURL(next.previews[k]!) }
        delete next.previews[k]
        delete next.geoData[k]
      }
      return next
    })
  }

  const setPreview = (k: PhotoKey, url?: string) => {
    setState((s) => ({ ...s, previews: { ...s.previews, [k]: url ?? undefined } }))
  }

  const setStep = (step: InspectionState['currentStep']) => setState((s) => ({ ...s, currentStep: step }))

  const addNote = (t: string) => setState((s) => ({ ...s, notes: [...s.notes, t] }))

  const reset = () => {
    Object.values(state.previews).forEach((u) => u && URL.revokeObjectURL(u))
    setState(defaultState)
  }

  const setUserInfo = (info: { name: string; idNumber: string; plate: string }) => {
    setState((s) => ({ ...s, userInfo: info }))
  }

  const value = useMemo(
    () => ({ state, setPhoto, setPreview, setStep, reset, addNote, setUserInfo }),
    [state]
  )

  return <InspectionContext.Provider value={value}>{children}</InspectionContext.Provider>
}

export function useInspectionStore() {
  const ctx = useContext(InspectionContext)
  if (!ctx) throw new Error('useInspectionStore must be used within an InspectionProvider')
  return ctx
}