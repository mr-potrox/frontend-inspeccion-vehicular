import React, { createContext, useContext, useMemo, useState } from 'react'
import { InspectionState, PhotoKey } from '@/types/inspection'

type Ctx = {
  state: InspectionState
  setPhoto: (k: PhotoKey, f: File | null) => void
  setPreview: (k: PhotoKey, url?: string) => void
  setStep: (s: InspectionState['currentStep']) => void
  reset: () => void
  addNote: (t: string) => void
}

const defaultState: InspectionState = {
  currentStep: 'landing',
  photos: {},
  previews: {},
  qualityResult: null,
  detectionResult: null,
  isProcessing: false,
  notes: [],
  error: null
}

const Ctx = createContext<Ctx | null>(null)

export function InspectionProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<InspectionState>(defaultState)

  const setPhoto = (k: PhotoKey, f: File | null) => {
    setState((s) => {
      const next = { ...s, photos: { ...s.photos }, previews: { ...s.previews } }
      if (f) {
        next.photos[k] = f
        next.previews[k] = URL.createObjectURL(f)
      } else {
        delete next.photos[k]
        if (next.previews[k]) { URL.revokeObjectURL(next.previews[k]!) }
        delete next.previews[k]
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

  const value = useMemo(() => ({ state, setPhoto, setPreview, setStep, reset, addNote }), [state])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useInspectionStore() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useInspectionStore must be used inside InspectionProvider')
  return ctx
}
