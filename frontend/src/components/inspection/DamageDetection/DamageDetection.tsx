import React, { useState, useEffect, useRef } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { finalizeInspection } from '@/services/inspectionService'

export default function DamageDetection({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { state, addNote, storeFinalize, setStep } = useInspectionStore()
  const [noteDraft, setNoteDraft] = useState('')
  const debounceRef = useRef<number | null>(null)
  const [confDamage, setConfDamage] = useState<number | undefined>()
  const [confParts, setConfParts] = useState<number | undefined>()
  const [finalizing, setFinalizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!state.userInfo?.plate) return
    setError(null)
    setFinalizing(true)
    try {
      const r = await finalizeInspection(state.sessionId, state.userInfo.plate, confDamage, confParts)
      storeFinalize(r)
      setStep('results')
    } catch (e: any) {
      setError(e.message || 'Error al finalizar')
    } finally {
      setFinalizing(false)
    }
  }

  useEffect(() => {
    const saved = sessionStorage.getItem(`noteDraft_${state.sessionId}`)
    if (saved) setNoteDraft(saved)
  }, [state.sessionId])

  const schedulePersist = (val: string) => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current)
    debounceRef.current = window.setTimeout(() => {
      sessionStorage.setItem(`noteDraft_${state.sessionId}`, val)
      if (val.trim().length) addNote(val.trim())
    }, 600)
  }

  return (
    <div className="space-y-6 max-w-md mx-auto">
      <CoachChat messages={[
        '🛠️ Observaciones finales.',
        'Si ves un daño no detectado escribe una nota. Luego generaremos el reporte.'
      ]} />

      <div className="grid grid-cols-2 gap-4 text-xs">
        <label className="flex flex-col gap-1">
          Conf Daños
          <input
            type="range"
            min={0.1}
            max={0.9}
            step={0.05}
            value={confDamage ?? 0.35}
            onChange={e => setConfDamage(parseFloat(e.target.value))}
          />
          <span className="text-[10px] text-gray-500">
            {(confDamage ?? 0.35).toFixed(2)}
          </span>
        </label>
        <label className="flex flex-col gap-1">
          Conf Partes
            <input
              type="range"
              min={0.1}
              max={0.9}
              step={0.05}
              value={confParts ?? 0.35}
              onChange={e => setConfParts(parseFloat(e.target.value))}
            />
            <span className="text-[10px] text-gray-500">
              {(confParts ?? 0.35).toFixed(2)}
            </span>
        </label>
      </div>

      <textarea
        className="w-full border rounded p-2 text-sm dark:bg-neutral-800 dark:text-neutral-100"
        placeholder="Notas (auto-guardado)..."
        value={noteDraft}
        onChange={e => { setNoteDraft(e.target.value); schedulePersist(e.target.value) }}
      />

      {error && <div className="text-xs text-red-600">{error}</div>}

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} disabled={finalizing}>Atrás</Button>
        <Button onClick={handleGenerate} disabled={finalizing}>
          {finalizing ? 'Generando...' : 'Generar reporte'}
        </Button>
      </div>
    </div>
  )
}