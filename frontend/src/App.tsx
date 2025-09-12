// filepath: [App.tsx](http://_vscodecontentref_/6)
import React, { useState, useEffect, Suspense } from 'react'
import { InspectionProvider } from '@/hooks/useInspectionStore'
import { ChatOrchestrator } from '@/components/chatflow/ChatOrchestrator'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import Button from '@/components/common/Button/Button'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { getApiVersion } from '@/services/inspectionService'

export default function App() {
  const [isMobile, setIsMobile] = useState(() =>
    window.innerWidth <= 600 && /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  )
  const [versionMismatch, setVersionMismatch] = useState<string | null>(null)
  const [started, setStarted] = useState(false)

  useEffect(() => {
    const handleResize = () =>
      setIsMobile(window.innerWidth <= 600 && /Android|iPhone|iPad|iPod/i.test(navigator.userAgent))
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    (async () => {
      try {
        const api = await getApiVersion()
        const expected = import.meta.env.VITE_EXPECTED_API_VERSION
        if (expected && api.version && api.version !== expected) {
          setVersionMismatch(`Versión API ${api.version} ≠ esperada ${expected}`)
        }
      } catch {
        setVersionMismatch('No se pudo validar la versión API.')
      }
    })()
  }, [])

  if (!isMobile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-neutral-900 dark:text-neutral-100">
        <div className="bg-white dark:bg-neutral-800 p-8 rounded-xl shadow text-center max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-4">Solo disponible en modo móvil</h2>
          <p>Usa tu teléfono o reduce la ventana.</p>
        </div>
      </div>
    )
  }

  return (
    <InspectionProvider>
      {versionMismatch && (
        <div className="fixed top-2 left-1/2 -translate-x-1/2 z-50 bg-amber-500 text-white text-xs px-3 py-1 rounded shadow">
          {versionMismatch}
        </div>
      )}
      <div className="min-h-screen bg-gray-50 dark:bg-neutral-900 flex items-center justify-center p-6">
        {!started ? (
          <div className="text-center max-w-lg">
            <img src="/logo.png" alt="Logo" className="mx-auto w-24 h-24 mb-6" />
            <CoachChat
              messages={[
                '👋 Bienvenido a la inspección asistida.',
                'Validaremos identidad y vehículo antes de iniciar.',
                'Pulsa Iniciar para comenzar.'
              ]}
            />
            <div className="mt-6">
              <Button variant="primary" onClick={() => setStarted(true)}>Iniciar</Button>
            </div>
          </div>
        ) : (
          <div className="w-full">
            <Suspense fallback={<LoadingSpinner title="Cargando" message="Preparando interfaz..." />}>
              <ChatOrchestrator />
            </Suspense>
          </div>
        )}
      </div>
    </InspectionProvider>
  )
}