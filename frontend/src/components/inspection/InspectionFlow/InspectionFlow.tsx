import React from 'react'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import Landing from '@/components/landing/Landing'
import ImageStep from '@/components/inspection/ImageStep/ImageStep'
import QualityCheck from '@/components/inspection/QualityCheck/QualityCheck'
import DamageDetection from '@/components/inspection/DamageDetection/DamageDetection'
import Results from '@/components/inspection/Results/Results'

const photoSteps = [
  { key: 'front', label: 'Frente', helper: 'Toma frontal completa a ~2m, que se vean ambas luces.' },
  { key: 'rear', label: 'Trasera', helper: 'Parte trasera completa, placa visible si aplica.' },
  { key: 'left', label: 'Lateral izquierdo', helper: 'Desde 45°, que se vea la puerta y la llanta.' },
  { key: 'right', label: 'Lateral derecho', helper: 'Misma toma del otro lado, cuidando iluminación.' },
  { key: 'dashboard', label: 'Tablero/Odómetro', helper: 'Captura el odómetro y testigos encendidos.' },
  { key: 'vin', label: 'VIN/Motor', helper: 'Número VIN o foto con cofre abierto (sin riesgo).' }
]

export default function InspectionFlow() {
  const { state, setStep } = useInspectionStore()

  const steps = [...photoSteps.map((p) => p.label), 'Revisión de calidad', 'Detección de daños', 'Resultados']
  const activeIndex = (() => {
    if (state.currentStep === 'landing') return 0
    const idx = photoSteps.findIndex((p) => p.key === state.currentStep)
    if (idx >= 0) return idx
    if (state.currentStep === 'quality-check') return photoSteps.length
    if (state.currentStep === 'damage-detection') return photoSteps.length + 1
    if (state.currentStep === 'results') return photoSteps.length + 2
    return 0
  })()

  const goNextFromPhoto = (current: number) => {
    if (current < photoSteps.length - 1) setStep(photoSteps[current + 1].key as any)
    else setStep('quality-check')
  }

  const goBackFromPhoto = (current: number) => {
    if (current > 0) setStep(photoSteps[current - 1].key as any)
    else setStep('landing')
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {state.currentStep === 'landing' && <Landing />}

      {photoSteps.map((p, i) => state.currentStep === p.key && (
        <ImageStep key={p.key} photoKey={p.key as any} title={`Paso ${i + 1}: ${p.label}`} helper={p.helper} onNext={() => goNextFromPhoto(i)} onBack={() => goBackFromPhoto(i)} />
      ))}

      {state.currentStep === 'quality-check' && <QualityCheck onNext={() => setStep('damage-detection')} onBack={() => setStep(photoSteps[photoSteps.length - 1].key as any)} />}

      {state.currentStep === 'damage-detection' && <DamageDetection onNext={() => setStep('results')} onBack={() => setStep('quality-check')} />}

      {state.currentStep === 'results' && <Results onBack={() => setStep('damage-detection')} />}
    </div>
  )
}