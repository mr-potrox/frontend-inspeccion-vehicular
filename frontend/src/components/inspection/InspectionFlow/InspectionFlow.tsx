import React, { Suspense, lazy } from 'react'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { UserForm } from '../UserForm'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { usePrefetch } from '@/hooks/usePrefetch'

const LazyImageStep = lazy(() => import('@/components/inspection/ImageStep/ImageStep'))
const LazyDamageDetection = lazy(() => import('@/components/inspection/DamageDetection/DamageDetection'))
const LazyResults = lazy(() => import('@/components/inspection/Results/Results'))


const photoSteps = [
  { key: 'front', label: 'Frente', helper: 'Toma frontal completa a ~2m.' },
  { key: 'rear', label: 'Trasera', helper: 'Parte trasera completa.' },
  { key: 'left', label: 'Lateral izquierdo', helper: 'Ángulo 45° lado izquierdo.' },
  { key: 'right', label: 'Lateral derecho', helper: 'Ángulo 45° lado derecho.' },
  { key: 'dashboard', label: 'Tablero/Odómetro', helper: 'Odómetro visible.' },
  { key: 'vin', label: 'VIN/Motor', helper: 'Foto VIN o motor.' }
]

export default function InspectionFlow() {
  const { state, setStep } = useInspectionStore()
  const hasAllPhotos = ['front','rear','left','right','dashboard','vin'].every(k => state.photos[k as any])
  usePrefetch(hasAllPhotos, () => import('@/components/inspection/DamageDetection/DamageDetection'))
  usePrefetch(state.currentStep === 'damage-detection', () => import('@/components/inspection/Results/Results'))

  const goNextFromPhoto = (idx: number) => {
    if (idx < photoSteps.length - 1) setStep(photoSteps[idx + 1].key as any)
    else setStep('damage-detection')
  }
  const goBackFromPhoto = (idx: number) => {
    if (idx > 0) setStep(photoSteps[idx - 1].key as any)
    else setStep('user-info')
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <Suspense fallback={<LoadingSpinner title="Cargando paso" message="Preparando componente..." />}>
        {state.currentStep === 'user-info' && <UserForm />}
        {photoSteps.map((p, i) =>
          state.currentStep === p.key && (
            <LazyImageStep
              key={p.key}
              photoKey={p.key as any}
              title={`Paso ${i + 1}: ${p.label}`}
              helper={p.helper}
              onNext={() => goNextFromPhoto(i)}
              onBack={() => goBackFromPhoto(i)}
            />
          )
        )}
        {state.currentStep === 'damage-detection' && (
          <LazyDamageDetection
            onNext={() => setStep('results')}
            onBack={() => setStep(photoSteps[photoSteps.length - 1].key as any)}
          />
        )}
        {state.currentStep === 'results' && (
          <LazyResults onBack={() => setStep('damage-detection')} />
        )}
      </Suspense>
    </div>
  )
}