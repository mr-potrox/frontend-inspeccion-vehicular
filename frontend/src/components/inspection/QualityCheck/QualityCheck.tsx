import React from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { PhotoKey } from '@/types/inspection'

const REQUIRED: { key: PhotoKey; label: string }[] = [
  { key: 'front', label: 'Frontal' },
  { key: 'rear', label: 'Trasera' },
  { key: 'left', label: 'Lateral izquierdo' },
  { key: 'right', label: 'Lateral derecho' },
  { key: 'dashboard', label: 'Tablero / Odómetro' },
  { key: 'vin', label: 'VIN / Motor' }
]

export default function QualityCheck({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { state } = useInspectionStore()
  const missing = REQUIRED.filter((r) => !state.photos[r.key])
  const ready = missing.length === 0

  return (
    <div className="space-y-6">
      <CoachChat messages={["✅ Validemos las tomas", ready ? 'Perfecto, tienes todas las fotos' : 'Faltan algunas fotos. Puedes volver a tomarlas.']} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {REQUIRED.map((r) => {
          const ok = Boolean(state.photos[r.key])
          return (
            <div key={r.key} className={`p-3 rounded-xl border flex items-center justify-between ${ok ? 'border-green-300 bg-green-50' : 'border-amber-300 bg-amber-50'}`}>
              <span className="text-sm">{r.label}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${ok ? 'bg-green-600 text-white' : 'bg-amber-600 text-white'}`}>{ok ? 'OK' : 'Falta'}</span>
            </div>
          )
        })}
      </div>

      {!ready && <div className="text-sm text-amber-700">Faltan: {missing.map((m) => m.label).join(', ')}.</div>}

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <Button onClick={onNext} disabled={!ready}>Continuar</Button>
      </div>
    </div>
  )
}