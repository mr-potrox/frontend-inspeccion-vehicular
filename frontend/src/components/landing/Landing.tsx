import React from 'react'
import { motion } from 'framer-motion'
import Button from '@/components/common/Button/Button'
import { useInspectionStore } from '@/hooks/useInspectionStore'

export default function Landing() {
  const { setStep } = useInspectionStore()
  return (
    <div className="min-h-screen flex items-center justify-center">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="max-w-3xl w-full p-8">
        <div className="card flex flex-col md:flex-row items-center gap-6">
          <div className="flex-1">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-2xl font-bold">AV</div>
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">AV — Asistente de Inspección Vehicular</h1>
            <p className="mt-2 text-gray-600">Te guiaré paso a paso para obtener las fotos necesarias y generar un reporte listo para aseguradora.</p>
            <div className="mt-4 flex gap-3">
              <Button onClick={() => setStep('front')}>Iniciar inspección</Button>
              <Button variant="secondary" onClick={() => alert('Próximamente: ver ejemplo de reporte')}>Ver demo</Button>
            </div>
          </div>
        </div>

        <div className="mt-6 text-sm text-gray-500">Consejo: ten el vehículo en un lugar con buena iluminación para mejores resultados.</div>
      </motion.div>
    </div>
  )
}