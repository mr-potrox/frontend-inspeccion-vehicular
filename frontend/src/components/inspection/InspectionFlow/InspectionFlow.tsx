import React from 'react'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import Landing from '@/components/landing/Landing'
import ImageStep from '@/components/inspection/ImageStep/ImageStep'
import QualityCheck from '@/components/inspection/QualityCheck/QualityCheck'
import DamageDetection from '@/components/inspection/DamageDetection/DamageDetection'
import Results from '@/components/inspection/Results/Results'
import { ImageUpload } from '@/components/inspection/ImageUpload/ImageUpload'
import CoachChat from '@/components/common/CoachChat/CoachChat'

const photoSteps = [
  { key: 'front', label: 'Frente', helper: 'Toma frontal completa a ~2m, que se vean ambas luces.' },
  { key: 'rear', label: 'Trasera', helper: 'Parte trasera completa, placa visible si aplica.' },
  { key: 'left', label: 'Lateral izquierdo', helper: 'Desde 45°, que se vea la puerta y la llanta.' },
  { key: 'right', label: 'Lateral derecho', helper: 'Misma toma del otro lado, cuidando iluminación.' },
  { key: 'dashboard', label: 'Tablero/Odómetro', helper: 'Captura el odómetro y testigos encendidos.' },
  { key: 'vin', label: 'VIN/Motor', helper: 'Número VIN o foto con cofre abierto (sin riesgo).' }
]

const coachMessages: Record<string, string[]> = {
  'user-info': [
    "👤 Por favor ingresa tus datos personales para comenzar la inspección.",
    "Completa el formulario y haz clic en continuar."
  ],
  'landing': [
    "👋 ¡Bienvenido! Haz clic en iniciar para comenzar tu inspección."
  ],
  'quality-check': [
    "🔎 Estamos revisando la calidad de tus imágenes. Un momento por favor..."
  ],
  'damage-detection': [
    "🛠️ Indica si observas algún daño adicional en tu vehículo."
  ],
  'results': [
    "✅ ¡Inspección finalizada! Aquí tienes el resultado."
  ],
  ...Object.fromEntries(photoSteps.map((p, i) => [
    p.key,
    [
      `📸 Paso ${i + 1}: ${p.label}`,
      p.helper
    ]
  ]))
}

export default function InspectionFlow() {
  const { state, setStep } = useInspectionStore()

  const goNextFromPhoto = (current: number) => {
    if (current < photoSteps.length - 1) setStep(photoSteps[current + 1].key as any)
    else setStep('quality-check')
  }

  const goBackFromPhoto = (current: number) => {
    if (current > 0) setStep(photoSteps[current - 1].key as any)
    else setStep('user-info')
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <CoachChat messages={coachMessages[state.currentStep] || ["¡Bienvenido!"]} />

      {state.currentStep === 'user-info' && <ImageUpload />}
      {state.currentStep === 'landing' && <Landing />}

      {photoSteps.map((p, i) => state.currentStep === p.key && (
        <ImageStep
          key={p.key}
          photoKey={p.key as any}
          title={`Paso ${i + 1}: ${p.label}`}
          helper={p.helper}
          onNext={() => goNextFromPhoto(i)}
          onBack={() => goBackFromPhoto(i)}
        />
      ))}

      {state.currentStep === 'quality-check' && (
        <QualityCheck
          onNext={() => setStep('damage-detection')}
          onBack={() => setStep(photoSteps[photoSteps.length - 1].key as any)}
        />
      )}

      {state.currentStep === 'damage-detection' && (
        <DamageDetection
          onNext={() => setStep('results')}
          onBack={() => setStep('quality-check')}
        />
      )}

      {state.currentStep === 'results' && (
        <Results onBack={() => setStep('damage-detection')} />
      )}
    </div>
  )
}