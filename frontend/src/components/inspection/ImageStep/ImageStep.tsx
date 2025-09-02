import React, { useRef, useState } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { PhotoKey } from '@/types/inspection'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { motion } from 'framer-motion'

export default function ImageStep({ photoKey, title, helper, onNext, onBack }: { photoKey: PhotoKey; title: string; helper: string; onNext: () => void; onBack?: () => void }) {
  const { state, setPhoto } = useInspectionStore()
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const preview = state.previews[photoKey]

  const onFile = (f?: File) => {
    setError(null)
    if (!f) return setPhoto(photoKey, null)
    if (!f.type.startsWith('image/')) return setError('El archivo debe ser una imagen.')
    if (f.size > 8 * 1024 * 1024) return setError('La imagen supera 8MB. Reduce su tamaño.')
    setPhoto(photoKey, f)
  }

  return (
    <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.35 }} className="space-y-6">
      <CoachChat messages={[`📸 ${title}`, helper, 'Consejo: mantén 2m de distancia, evita contraluz.']} />

      <div className="border-2 border-dashed rounded-2xl p-6 bg-gray-50 flex flex-col items-center gap-4">
        {preview ? (
          <motion.img src={preview} alt={photoKey} className="max-h-80 rounded-xl object-contain shadow" initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} />
        ) : (
          <div className="text-gray-500 text-sm">Aún no has seleccionado una imagen.</div>
        )}

        <div className="flex gap-2">
          <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={(e) => onFile(e.target.files?.[0] ?? undefined)} />
          <Button onClick={() => inputRef.current?.click()}>Seleccionar imagen</Button>
          {preview && <Button variant="secondary" onClick={() => onFile(undefined)}>Quitar</Button>}
        </div>

        {error && <div className="text-red-600 text-sm">{error}</div>}
      </div>

      <div className="flex justify-between">
        <Button variant="back" onClick={onBack} disabled={!onBack}>Atrás</Button>
        <Button onClick={onNext} disabled={!state.photos[photoKey]}>Continuar</Button>
      </div>
    </motion.div>
  )
}