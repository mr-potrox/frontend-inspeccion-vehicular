import React, { useState, useEffect } from 'react'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import Button from '@/components/common/Button/Button'
import ImageStep from '@/components/inspection/ImageStep/ImageStep'
import DamageDetection from '@/components/inspection/DamageDetection/DamageDetection'
import Results from '@/components/inspection/Results/Results'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import {
  verifyIdentity,
  verifyVehicle,
  getVehicleHistory,
  getHealth,
  finalizeInspection
} from '@/services/inspectionService'
import { PhotoKey } from '@/types/inspection'

type Flow =
  | 'WELCOME'
  | 'ASK_ID'
  | 'VERIFYING_ID'
  | 'ASK_PLATE'
  | 'VERIFYING_VEHICLE'
  | 'SHOW_VEHICLE'
  | 'PHOTO'
  | 'DAMAGE'
  | 'FINALIZING'
  | 'RESULTS'

const ORDER: PhotoKey[] = ['front', 'rear', 'left', 'right', 'dashboard', 'vin']

export function ChatOrchestrator() {
  const {
    state, setUserInfo, setQuality,
    setIdentity, setHistory, storeFinalize, setAbort
  } = useInspectionStore()
  const [flow, setFlow] = useState<Flow>('WELCOME')
  const [idx, setIdx] = useState(0)

  const [name, setName] = useState('')
  const [documentId, setDocumentId] = useState('')
  const [plate, setPlate] = useState('')
  const [vehicleData, setVehicleData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Carga thresholds al inicio (si no están)
  useEffect(() => {
    (async () => {
      if (!state.quality) {
        try {
          const h = await getHealth()
          if (h.quality_thresholds) setQuality(h.quality_thresholds)
        } catch {
          // silencioso
        }
      }
    })()
  }, [state.quality, setQuality])

  const canSubmitIdentity = name.trim().length >= 3 && documentId.trim().length >= 5
  const plateRegex = /^[A-Z0-9]{5,7}$/i
  const canSubmitPlate = plateRegex.test(plate.trim())

  const handleVerifyIdentity = async () => {
    setError(null); setLoading(true); setFlow('VERIFYING_ID')
    try {
      const resp = await verifyIdentity({ name: name.trim(), document: documentId.trim() })
      if (!resp.valid) {
        setError('Identidad no válida.')
        setFlow('ASK_ID')
      } else {
        setIdentity({ valid: true, name: name.trim(), document: documentId.trim() })
        setFlow('ASK_PLATE')
      }
    } catch {
      setError('Error validando identidad')
      setFlow('ASK_ID')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyVehicle = async () => {
    setError(null); setLoading(true); setFlow('VERIFYING_VEHICLE')
    try {
      const veh = await verifyVehicle(plate.toUpperCase().trim())
      if (!veh.found || !veh.data) {
        setError('Vehículo no encontrado')
        setFlow('ASK_PLATE')
        return
      }
      // Historia
      try {
        const hist = await getVehicleHistory(veh.data.plate)
        setHistory(hist)
      } catch {
        // ignore
      }
      setVehicleData(veh.data)
      setUserInfo({
        name: name.trim(),
        idNumber: documentId.trim(),
        plate: veh.data.plate
      })
      if (veh.data.id && veh.data.id !== documentId.trim()) {
        setError('Documento no coincide con propietario.')
        setFlow('ASK_PLATE')
        return
      }
      setFlow('SHOW_VEHICLE')
    } catch {
      setError('Error consultando vehículo')
      setFlow('ASK_PLATE')
    } finally {
      setLoading(false)
    }
  }

  const goPhotos = () => { setIdx(0); setFlow('PHOTO') }
  const nextPhoto = () => {
    if (idx < ORDER.length - 1) setIdx(i => i + 1)
    else setFlow('DAMAGE')
  }
  const backPhoto = () => {
    if (idx === 0) setFlow('SHOW_VEHICLE')
    else setIdx(i => i - 1)
  }

  const finalize = async () => {
    if (!state.userInfo?.plate) return
    setFlow('FINALIZING')
    try {
      const res = await finalizeInspection(state.sessionId, state.userInfo.plate)
      storeFinalize(res)
      if (res.aborted) setAbort(res.abort_reason || 'ABORT')
      setFlow('RESULTS')
    } catch (e: any) {
      setError(e.message || 'Error finalizando')
      setFlow('DAMAGE')
    }
  }

  const messages = (() => {
    switch (flow) {
      case 'WELCOME': return ['👋 Hola, empecemos tu inspección.', 'Validaremos identidad y vehículo.']
      case 'ASK_ID': return ['Ingresa tu nombre y documento.']
      case 'VERIFYING_ID': return ['Verificando identidad...']
      case 'ASK_PLATE': return ['Ahora ingresa la placa del vehículo.']
      case 'VERIFYING_VEHICLE': return ['Consultando datos del vehículo...']
      case 'SHOW_VEHICLE': return ['Verifica los datos recuperados y continúa.']
      case 'PHOTO': return ['Capturaremos las fotos requeridas.']
      case 'DAMAGE': return ['Observaciones finales antes de generar el reporte.']
      case 'FINALIZING': return ['Generando reporte final...']
      case 'RESULTS': return ['Inspección completada.']
      default: return []
    }
  })()

  if (flow === 'WELCOME') {
    return (
      <div className="space-y-6 max-w-md mx-auto">
        <CoachChat messages={messages} />
        <div className="flex justify-end">
          <Button onClick={() => setFlow('ASK_ID')}>Comenzar</Button>
        </div>
      </div>
    )
  }

  if (flow === 'ASK_ID' || flow === 'VERIFYING_ID') {
    return (
      <div className="space-y-6 max-w-md mx-auto">
        <CoachChat messages={messages} />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <div className="border rounded-xl p-4 space-y-4 bg-white">
          <label className="block text-sm">
            Nombre:
            <input
              className="mt-1 w-full border rounded p-2 text-sm"
              value={name}
              onChange={e => setName(e.target.value)}
              disabled={flow === 'VERIFYING_ID'}
            />
          </label>
          <label className="block text-sm">
            Documento:
            <input
              className="mt-1 w-full border rounded p-2 text-sm"
              value={documentId}
              onChange={e => setDocumentId(e.target.value)}
              disabled={flow === 'VERIFYING_ID'}
            />
          </label>
          <div className="flex justify-end">
            <Button
              disabled={!canSubmitIdentity || flow === 'VERIFYING_ID'}
              onClick={handleVerifyIdentity}
            >
              {flow === 'VERIFYING_ID' ? 'Verificando...' : 'Validar'}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (flow === 'ASK_PLATE' || flow === 'VERIFYING_VEHICLE') {
    return (
      <div className="space-y-6 max-w-md mx-auto">
        <CoachChat messages={messages} />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <div className="border rounded-xl p-4 space-y-4 bg-white">
          <label className="block text-sm">
            Placa:
            <input
              className="mt-1 w-full border rounded p-2 text-sm uppercase"
              value={plate}
              onChange={e => setPlate(e.target.value.toUpperCase())}
              disabled={flow === 'VERIFYING_VEHICLE'}
              maxLength={7}
            />
          </label>
          <div className="flex justify-between">
            <Button variant="ghost" onClick={() => setFlow('ASK_ID')} disabled={flow === 'VERIFYING_VEHICLE'}>Atrás</Button>
            <Button
              disabled={!canSubmitPlate || flow === 'VERIFYING_VEHICLE'}
              onClick={handleVerifyVehicle}
            >
              {flow === 'VERIFYING_VEHICLE' ? 'Consultando...' : 'Validar placa'}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (flow === 'SHOW_VEHICLE') {
    return (
      <div className="space-y-6 max-w-md mx-auto">
        <CoachChat messages={messages} />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <div className="border rounded-xl p-4 bg-white text-sm space-y-1">
          <div><strong>Placa:</strong> {vehicleData?.plate}</div>
          <div><strong>Propietario:</strong> {vehicleData?.owner}</div>
          <div><strong>Marca:</strong> {vehicleData?.brand}</div>
          <div><strong>Modelo:</strong> {vehicleData?.model}</div>
          <div><strong>Año:</strong> {vehicleData?.year}</div>
          {state.vehicleHistory && (
            <>
              <div className="mt-2"><strong>Infracciones:</strong> {state.vehicleHistory.infractions}</div>
              <div><strong>Dueños previos:</strong> {state.vehicleHistory.previous_owners}</div>
              <div><strong>Técnica OK:</strong> {state.vehicleHistory.tech_ok ? 'Sí' : 'No'}</div>
            </>
          )}
        </div>
        <div className="flex justify-between">
          <Button variant="ghost" onClick={() => setFlow('ASK_PLATE')}>Atrás</Button>
          <Button onClick={goPhotos}>Continuar a fotos</Button>
        </div>
      </div>
    )
  }

  if (flow === 'PHOTO') {
    const key = ORDER[idx]
    const helperMap: Record<PhotoKey, string> = {
      front: 'Frontal completa a ~2m',
      rear: 'Parte trasera',
      left: 'Lado izquierdo 45°',
      right: 'Lado derecho 45°',
      dashboard: 'Tablero con odómetro',
      vin: 'VIN / motor legible'
    }
    return (
      <ImageStep
        photoKey={key}
        title={`Foto ${idx + 1} / ${ORDER.length}`}
        helper={helperMap[key]}
        onNext={nextPhoto}
        onBack={backPhoto}
      />
    )
  }

  if (flow === 'DAMAGE') {
    return (
      <DamageDetection
        onNext={finalize}
        onBack={() => setFlow('PHOTO')}
      />
    )
  }

  if (flow === 'FINALIZING') {
    return (
      <div className="space-y-6 max-w-md mx-auto">
        <CoachChat messages={messages} />
        <div className="text-sm text-gray-500">Generando...</div>
      </div>
    )
  }

  return (
    <Results onBack={() => setFlow('DAMAGE')} />
  )
}