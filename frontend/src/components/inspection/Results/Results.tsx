import React, { useState, useEffect } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { PhotoKey } from '@/types/inspection'
import { BoxesOverlay } from '@/components/common/BoxesOverlay'
import { getReportPdf, getHealth } from '@/services/inspectionService'

const LABELS: Record<PhotoKey, string> = {
  front: 'Frontal',
  rear: 'Trasera',
  left: 'Lateral Izq',
  right: 'Lateral Der',
  dashboard: 'Tablero',
  vin: 'VIN/Motor'
}

export default function Results({ onBack }: { onBack: () => void }) {
  const { state, reset } = useInspectionStore()
  const final = state.finalizeResult
  const aborted = state.aborted
  const user = state.userInfo

  const [pdfEnabled, setPdfEnabled] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [showScratches, setShowScratches] = useState(true)
  const [showDamage, setShowDamage] = useState(true)

  const [damageFilter, setDamageFilter] = useState<string[]>([])
  const [availableDamageLabels, setAvailableDamageLabels] = useState<string[]>([])

  useEffect(() => {
    (async () => {
      try {
        const h = await getHealth()
        if (h.pdf_enabled === false) setPdfEnabled(false)
        if (h.labels?.damage_labels) setAvailableDamageLabels(h.labels.damage_labels)
      } catch {
        /* silencio */
      }
    })()
  }, [])

  const items = (Object.keys(LABELS) as PhotoKey[]).map(k => {
    const analysis = state.analyses[k]
    return {
      key: k,
      label: LABELS[k],
      analysis,
      url: state.previews[k],
      coords: state.geoData?.[k]
    }
  })

  const metricsList = items.map(i => i.analysis?.preproc_metrics).filter(Boolean) as any[]
  let avgLap: string | undefined
  let avgEdge: string | undefined
  if (metricsList.length) {
    const sumLap = metricsList.reduce((a, m) => a + (m.lap_var || 0), 0)
    const sumEdge = metricsList.reduce((a, m) => a + (m.edge_density || 0), 0)
    avgLap = (sumLap / metricsList.length).toFixed(2)
    avgEdge = (sumEdge / metricsList.length).toFixed(4)
  }

  const handleDownloadPdf = async () => {
    if (!final?.inspection_id) return
    try {
      setDownloading(true)
      const blob = await getReportPdf(final.inspection_id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `reporte_${final.inspection_id}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setDownloading(false)
    }
  }

  const messages = aborted
    ? ['⚠️ Inspección abortada', 'Motivo: ' + (state.abortReason || 'No especificado')]
    : ['✅ Inspección completada', final?.status || '']

  return (
    <div className="space-y-6">
      <CoachChat messages={messages} />

      {!aborted && (
        <div className="border rounded-xl p-5 bg-gradient-to-r from-green-50 to-green-100 text-sm text-green-800 shadow-sm">
          <h3 className="font-semibold mb-1">¡Gracias por completar la inspección!</h3>
          Un miembro de la aseguradora se comunicará contigo para continuar el proceso.
          {final?.inspection_id && (
            <div className="mt-2 text-[11px] text-green-700">
              ID de inspección: {final.inspection_id}
            </div>
          )}
        </div>
      )}

      {metricsList.length > 0 && (
        <div className="border rounded-xl p-4 bg-white text-xs flex flex-wrap gap-4">
          <div><strong>Métricas:</strong></div>
          <div>Nitidez prom: {avgLap}</div>
          <div>Densidad bordes prom: {avgEdge}</div>
          <div>Imgs: {metricsList.length}</div>
        </div>
      )}

      <div className="space-y-2">
        <div className="flex gap-2 text-xs items-start flex-wrap">
          <label className="flex gap-1 items-center">
            <input type="checkbox" checked={showDamage} onChange={e => setShowDamage(e.target.checked)} /> Daños
          </label>
          <label className="flex gap-1 items-center">
            <input type="checkbox" checked={showScratches} onChange={e => setShowScratches(e.target.checked)} /> Scratches
          </label>
          {availableDamageLabels.length > 0 && (
            <select
              className="border rounded px-2 py-1 text-xs"
              multiple
              size={Math.min(6, availableDamageLabels.length)}
              value={damageFilter}
              onChange={e => {
                const v = Array.from(e.target.selectedOptions).map(o => o.value)
                setDamageFilter(v)
              }}
            >
              {availableDamageLabels.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          )}
          {damageFilter.length > 0 && (
            <button
              type="button"
              className="text-[10px] underline text-blue-600"
              onClick={() => setDamageFilter([])}
            >
              Limpiar filtro
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {items.map(it => {
          const damageBoxes = (showDamage && it.analysis?.damage)
            ? it.analysis.damage
                .filter(d => damageFilter.length === 0 || damageFilter.includes(d.label))
                .map(d => ({
                  box: d.box as any,
                  label: d.label,
                  confidence: d.confidence,
                  type: 'damage' as const
                }))
            : []
          const scratchBoxes = (showScratches && it.analysis?.scratch?.scratch_candidates)
            ? it.analysis.scratch.scratch_candidates.map(sc => ({
                box: sc.box as any,
                aspect: sc.aspect,
                type: 'scratch' as const
              }))
            : []
          const allBoxes = [...damageBoxes, ...scratchBoxes]

            return (
              <div key={it.key} className="border rounded-xl p-3 bg-white">
                {it.url
                  ? (allBoxes.length
                    ? <BoxesOverlay src={it.url} boxes={allBoxes} />
                    : <img
                        src={it.url}
                        alt={it.label}
                        className="rounded-lg mb-2 max-h-56 object-contain w-full"
                      />)
                  : <div className="h-40 flex items-center justify-center text-xs text-gray-500">
                      Sin imagen
                    </div>
                }
                <div className="text-sm font-medium mt-1">{it.label}</div>
                {it.coords && (
                  <div className="text-green-700 text-[11px] mt-1">
                    Geo: {it.coords.lat.toFixed(4)}, {it.coords.lon.toFixed(4)}
                  </div>
                )}
                {it.analysis?.quality_status && (
                  <div className={`text-[11px] mt-1 ${
                    it.analysis.quality_status === 'very_blur' ? 'text-red-600' :
                    it.analysis.quality_status === 'blur' ? 'text-amber-600' :
                    it.analysis.quality_status === 'warn' ? 'text-amber-500' :
                    'text-green-600'
                  }`}>
                    Calidad: {it.analysis.quality_status}
                  </div>
                )}
                {it.analysis?.scratch?.count != null && it.analysis.scratch.count > 0 && (
                  <div className="text-[11px] text-blue-600">
                    Scratches: {it.analysis.scratch.count}
                  </div>
                )}
                {it.analysis?.review_flags?.length ? (
                  <div className="text-[11px] text-amber-600">
                    Review: {it.analysis.review_flags.join(', ')}
                  </div>
                ) : null}
              </div>
            )
        })}
      </div>

      <div className="border rounded-xl p-4 bg-gray-50 text-sm space-y-2">
        <div><strong>Placa:</strong> {user?.plate}</div>
        {final?.identity_validated !== undefined && (
          <div><strong>Identidad validada:</strong> {final.identity_validated ? 'Sí' : 'No'}</div>
        )}
        {final?.vehicle_history && (
          <div className="text-xs space-y-1">
            <div><strong>Infracciones:</strong> {final.vehicle_history.infractions}</div>
            <div><strong>Dueños previos:</strong> {final.vehicle_history.previous_owners}</div>
            <div><strong>Técnica OK:</strong> {final.vehicle_history.tech_ok ? 'Sí' : 'No'}</div>
          </div>
        )}
        {final?.inspection_id && pdfEnabled && (
          <Button
            variant="secondary"
            onClick={handleDownloadPdf}
            disabled={downloading}
          >
            {downloading ? 'Descargando...' : 'PDF'}
          </Button>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex gap-2">
          <Button onClick={reset}>Nueva</Button>
        </div>
      </div>
    </div>
  )
}