import React from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'

export default function DamageDetection({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { addNote } = useInspectionStore()
  return (
    <div className="space-y-6">
      <CoachChat messages={["🔎 Analizando imágenes (placeholder)", 'Aquí verás las marcas de rayones y golpes cuando integremos la IA.']} />
      <textarea className="w-full min-h-[120px] border rounded-xl p-3" placeholder="Deja una nota sobre daños que veas" onBlur={(e) => e.target.value && addNote(e.target.value)} />
      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  )
}