import React, { useRef, useState, useCallback } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { PhotoKey } from '@/types/inspection'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { analyzeImage } from '@/services/inspectionService'
import { optimizeImage } from '@/utils/imageOptimize'


export default function ImageStep({
  photoKey, title, helper, onNext, onBack
}: { photoKey: PhotoKey; title: string; helper: string; onNext: () => void; onBack?: () => void }) {
  const { state, setPhoto, storeAnalysis, setAbort } = useInspectionStore()
  const DEBUG_IMAGES = import.meta.env.VITE_DEBUG_IMAGES === '1'
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [geoError, setGeoError] = useState<string | null>(null)
  const [geoData, setGeoData] = useState<{ lat: number; lon: number } | null>(null)
  const [qualityStatus, setQualityStatus] = useState<string | null>(null)
  const [override, setOverride] = useState(false)
  const preview = state.previews[photoKey]
  const plate = state.userInfo?.plate || ''
  const analysis = state.analyses[photoKey]

  const runBackendAnalyze = async (file: File, coords: { lat?: number; lon?: number }) => {
    if (!plate) { setError('Placa no definida.'); return }
    try {
      const resp = await analyzeImage({
        file,
        sessionId: state.sessionId,
        plate,
        lat: coords.lat,
        lon: coords.lon,
        debug: DEBUG_IMAGES,
        photoKey
      })
      storeAnalysis(photoKey, resp)
      if (resp.aborted) {
        setAbort(resp.abort_reason || 'ABORT')
        return
      }
      const qs = resp.quality_status || 'ok'
      setQualityStatus(qs)
      if ((qs === 'blur' || qs === 'very_blur') && !override) {
        // No avanzamos automáticamente
        return
      }
      onNext()
    } catch (e: any) {
      setError(e.message || 'Error backend')
    }
  }

  const handleFileWithGeo = async (file: File) => {
    setIsProcessing(true); setError(null); setGeoError(null); setQualityStatus(null); setOverride(false)
    let working = file
    try { working = await optimizeImage(file, 1400, 0.85) } catch {}
    if (!working.type.startsWith('image/')) { setError('Archivo debe ser imagen'); setIsProcessing(false); return }
    if (working.size > 8 * 1024 * 1024) { setError('Imagen > 8MB'); setIsProcessing(false); return }

    const proceed = (coords: { lat?: number; lon?: number }) => {
      setPhoto(photoKey, working, coords.lat != null && coords.lon != null ? { lat: coords.lat, lon: coords.lon } : undefined)
      runBackendAnalyze(working, coords).finally(() => setIsProcessing(false))
    }

    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const c = { lat: pos.coords.latitude, lon: pos.coords.longitude }
            setGeoData(c); proceed(c)
        },
        () => { setGeoError('Sin geolocalización'); proceed({}) },
        { enableHighAccuracy: true, timeout: 5000 }
      )
    } else {
      setGeoError('Geo no soportada'); proceed({})
    }
  }

  const onDrop = useCallback((accepted: File[]) => { if (accepted[0]) handleFileWithGeo(accepted[0]) }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1
  })

  const retake = () => {
    setPhoto(photoKey, null)
    setQualityStatus(null)
    setOverride(false)
  }

  const proceedAnyway = () => {
    setOverride(true)
    onNext()
  }

  const qualityMessage = (() => {
    if (!qualityStatus) return null
    switch (qualityStatus) {
      case 'very_blur':
        return 'Muy borrosa. Debe recapturarse.'
      case 'blur':
        return 'Baja nitidez. Se sugiere recapturar.'
      case 'warn':
        return 'Nitidez aceptable pero podría mejorarse.'
      default:
        return 'Calidad OK.'
    }
  })()

  return (
    <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.35 }} className="space-y-6">
      <CoachChat messages={[`📸 ${title}`, helper, 'Procura iluminación uniforme.']} />

      {qualityStatus && (qualityStatus === 'blur' || qualityStatus === 'very_blur') && !override && (
        <div className={`border rounded-xl p-4 text-xs space-y-2 ${
          qualityStatus === 'very_blur' ? 'bg-red-50 border-red-400 text-red-700' : 'bg-amber-50 border-amber-400 text-amber-700'
        }`}>
          <div>{qualityMessage}</div>
          <ul className="list-disc ml-4">
            <li>Evita movimiento.</li>
            <li>Mejor luz frontal.</li>
            <li>Limpia la lente.</li>
          </ul>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={retake}>Repetir foto</Button>
            {qualityStatus === 'blur' && (
              <Button variant="primary" onClick={proceedAnyway}>Continuar igualmente</Button>
            )}
          </div>
        </div>
      )}

      <div {...getRootProps()} className={`border-2 border-dashed rounded-2xl p-6 bg-gray-50 flex flex-col items-center gap-4 cursor-pointer ${isDragActive ? 'border-primary-500' : ''}`}>
        <input {...getInputProps()} />
        {preview
          ? <motion.img src={preview} alt={photoKey} className="max-h-80 rounded-xl object-contain shadow"
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} />
          : <div className="text-gray-500 text-sm">{isDragActive ? 'Suelta la imagen...' : 'Arrastra o haz clic para subir / tomar foto.'}</div>}
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={e => { if (e.target.files?.[0]) handleFileWithGeo(e.target.files[0]) }}
          />
          <Button onClick={() => inputRef.current?.click()} disabled={isProcessing}>
            {isProcessing ? 'Procesando...' : preview ? 'Reemplazar' : 'Seleccionar/Tomar'}
          </Button>
          {preview && (
            <Button variant="secondary" onClick={retake} disabled={isProcessing}>
              Quitar
            </Button>
          )}
        </div>
        {qualityStatus && (
          <div className="text-xs font-medium">
            Estado calidad: {qualityStatus}
          </div>
        )}
        {analysis?.scratch?.count != null && analysis.scratch.count > 0 && (
          <div className="text-[11px] text-blue-600">
            Scratch candidatos: {analysis.scratch.count}
          </div>
        )}
        {isProcessing && <div className="text-sm text-primary">Analizando...</div>}
        {error && <div className="text-red-600 text-sm">{error}</div>}
        {geoError && <div className="text-yellow-600 text-xs">{geoError}</div>}
        {geoData && <div className="text-green-700 text-xs">Geo: {geoData.lat.toFixed(5)}, {geoData.lon.toFixed(5)}</div>}
      </div>
      <div className="flex justify-between">
        {onBack && <Button variant="back" onClick={onBack} disabled={isProcessing}>Atrás</Button>}
        <Button onClick={onNext} disabled={!preview || isProcessing || ((qualityStatus === 'blur' || qualityStatus === 'very_blur') && !override)}>
          Siguiente
        </Button>
      </div>
    </motion.div>
  )
}