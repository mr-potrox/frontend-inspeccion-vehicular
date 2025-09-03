import React, { useRef, useState, useCallback } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { PhotoKey } from '@/types/inspection'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'

export default function ImageStep({
  photoKey,
  title,
  helper,
  onNext,
  onBack
}: {
  photoKey: PhotoKey
  title: string
  helper: string
  onNext: () => void
  onBack?: () => void
}) {
  const { state, setPhoto } = useInspectionStore()
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [geoError, setGeoError] = useState<string | null>(null)
  const [geoData, setGeoData] = useState<{ lat: number; lon: number } | null>(null)
  const preview = state.previews[photoKey]

  // Drag and drop handler
  const handleFileWithGeo = async (file: File) => {
    setIsProcessing(true)
    setError(null)
    setGeoError(null)

    if (!file.type.startsWith('image/')) {
      setError('El archivo debe ser una imagen.')
      setIsProcessing(false)
      return
    }
    if (file.size > 8 * 1024 * 1024) {
      setError('La imagen supera 8MB. Reduce su tamaño.')
      setIsProcessing(false)
      return
    }

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude }
          setGeoData(coords)
          setPhoto(photoKey, file, coords)
          setIsProcessing(false)
        },
        (err) => {
          let message = ''
          switch (err.code) {
            case 1: message = 'Permiso de ubicación denegado'; break
            case 2: message = 'Posición no disponible'; break
            case 3: message = 'Timeout al obtener ubicación'; break
            default: message = 'Error desconocido'
          }
          setGeoError(message)
          setPhoto(photoKey, file)
          setIsProcessing(false)
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      )
    } else {
      setGeoError('Geolocalización no soportada')
      setPhoto(photoKey, file)
      setIsProcessing(false)
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles[0]) handleFileWithGeo(acceptedFiles[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1
  })

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <CoachChat messages={[
        `📸 ${title}`,
        helper,
        'Consejo: mantén 2m de distancia, evita contraluz.'
      ]} />

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-6 bg-gray-50 flex flex-col items-center gap-4 cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : ''
        }`}
      >
        <input {...getInputProps()} />
        {preview ? (
          <motion.img
            src={preview}
            alt={photoKey}
            className="max-h-80 rounded-xl object-contain shadow"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          />
        ) : (
          <div className="text-gray-500 text-sm">
            {isDragActive
              ? 'Suelta la imagen aquí...'
              : 'Arrastra y suelta una imagen aquí o haz clic para seleccionar/tomar foto.'}
          </div>
        )}

        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) handleFileWithGeo(e.target.files[0])
            }}
          />
          <Button onClick={() => inputRef.current?.click()} disabled={isProcessing}>
            {isProcessing ? 'Procesando...' : 'Tomar foto o seleccionar archivo'}
          </Button>
          {preview && <Button variant="secondary" onClick={() => setPhoto(photoKey, null)}>Quitar</Button>}
        </div>

        {error && <div className="text-red-600 text-sm">{error}</div>}
        {geoError && <div className="text-yellow-600 text-sm">{geoError}</div>}
        {geoData && (
          <div className="text-green-700 text-xs">
            Ubicación: {geoData.lat.toFixed(6)}, {geoData.lon.toFixed(6)}
          </div>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="back" onClick={onBack}>Atrás</Button>
        <Button onClick={onNext} disabled={!state.photos[photoKey] || isProcessing}>Continuar</Button>
      </div>
    </motion.div>
  )
}