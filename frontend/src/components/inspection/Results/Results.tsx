import React from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { PhotoKey } from '@/types/inspection'

const LABELS: Record<PhotoKey, string> = {
  front: 'Frontal',
  rear: 'Trasera',
  left: 'Lateral izquierdo',
  right: 'Lateral derecho',
  dashboard: 'Tablero / Odómetro',
  vin: 'VIN / Motor'
}

export default function Results({ onBack }: { onBack: () => void }) {
  const { state, reset } = useInspectionStore()
  const items = (Object.keys(state.previews) as PhotoKey[]).map((k) => ({ key: k, label: LABELS[k], url: state.previews[k]! }))

  return (
    <div className="space-y-6">
      <CoachChat messages={["✅ Inspección completada", 'Puedes descargar el informe cuando integremos la función.']} />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {items.map((it) => (
          <div key={it.key} className="border rounded-xl p-3 bg-white">
            <img src={it.url} alt={it.label} className="rounded-lg mb-2 max-h-56 object-contain w-full" />
            <div className="text-sm text-gray-700">{it.label}</div>
          </div>
        ))}
      </div>

      {state.notes.length > 0 && (
        <div className="border rounded-xl p-4 bg-blue-50">
          <div className="font-medium mb-2">Notas del usuario</div>
          <ul className="list-disc ml-5 text-sm text-gray-700">{state.notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      )}

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>Volver</Button>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => alert('Próximamente: exportar PDF')}>Exportar PDF</Button>
          <Button onClick={reset}>Nueva inspección</Button>
        </div>
      </div>
    </div>
  )
}