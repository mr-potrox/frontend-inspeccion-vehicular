import React, { useState, useEffect } from 'react'
import Button from '@/components/common/Button/Button'
import CoachChat from '@/components/common/CoachChat/CoachChat'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { PhotoKey } from '@/types/inspection'
import { BoxesOverlay } from '@/components/common/BoxesOverlay'
import { getReportPdf, getHealth } from '@/services/inspectionService'

// NOTA: Se usan casts a 'any' porque las interfaces TS aún no contemplan
// los campos extendidos (color_evaluation, ocr_summary, part_completeness_score,
// illumination/background/segmentation/ocr/tamper). Actualiza las definiciones luego.

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
  const [scratchSeverityFilter, setScratchSeverityFilter] = useState<string[]>([])

  useEffect(() => {
    (async () => {
      try {
        const h = await getHealth()
        if (h?.pdf_enabled === false) setPdfEnabled(false)
        if (h?.labels?.damage_labels) setAvailableDamageLabels(h.labels.damage_labels)
      } catch { /* ignore */ }
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

  // Promedios iluminación (campos extendidos)
  let illumMeanAvg: string | undefined
  let illumDRAvg: string | undefined
  const finalAny = final as any
  if (finalAny?.illumination_frames?.length) {
    const means = finalAny.illumination_frames.map((f: any) => f?.mean || 0)
    const drs = finalAny.illumination_frames.map((f: any) => f?.dynamic_range || 0)
    const avg = (a: number[]) => a.reduce((p,c)=>p+c,0)/Math.max(1,a.length)
    illumMeanAvg = avg(means).toFixed(1)
    illumDRAvg = avg(drs).toFixed(1)
  }

  const handleDownloadPdf = async () => {
    if (!finalAny?.inspection_id) return
    try {
      setDownloading(true)
      const blob = await getReportPdf(finalAny.inspection_id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `reporte_${finalAny.inspection_id}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } finally { setDownloading(false) }
  }

  const messages = aborted
    ? ['⚠️ Inspección abortada', 'Motivo: ' + (state.abortReason || 'No especificado')]
    : ['✅ Inspección completada', finalAny?.status || '']

  const scratchSevLabels = ['minor','moderate','severe']

  return (
    <div className="space-y-6">
      <CoachChat messages={messages} />

      {(illumMeanAvg || (finalAny?.fraud_flags && finalAny.fraud_flags.length>0)) && (
        <div className="border rounded-xl p-4 bg-white text-xs flex flex-wrap gap-4 items-center">
          {illumMeanAvg && (
            <>
              <div><strong>Ilum. Mean:</strong> {illumMeanAvg}</div>
              <div><strong>Ilum. DR:</strong> {illumDRAvg}</div>
            </>
          )}
          {finalAny?.fraud_flags?.length > 0 && (
            <div className="text-red-600">
              Fraud: {finalAny.fraud_flags.join(', ')}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3 flex-wrap text-xs items-start">
        <label className="flex gap-1 items-center">
          <input type="checkbox" checked={showDamage} onChange={e=>setShowDamage(e.target.checked)}/> Daños
        </label>
        <label className="flex gap-1 items-center">
          <input type="checkbox" checked={showScratches} onChange={e=>setShowScratches(e.target.checked)}/> Scratches
        </label>
        {availableDamageLabels.length > 0 && (
          <select
            multiple
            className="border rounded px-2 py-1"
            size={Math.min(6, availableDamageLabels.length)}
            value={damageFilter}
            onChange={e => {
              setDamageFilter(Array.from(e.target.selectedOptions).map(o=>o.value))
            }}
          >
            {availableDamageLabels.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        )}
        {damageFilter.length > 0 && (
          <button className="underline" onClick={()=>setDamageFilter([])}>Limpiar daños</button>
        )}
        <select
          multiple
          className="border rounded px-2 py-1"
          size={scratchSevLabels.length}
          value={scratchSeverityFilter}
          onChange={e => {
            setScratchSeverityFilter(Array.from(e.target.selectedOptions).map(o=>o.value))
          }}
        >
          {scratchSevLabels.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        {scratchSeverityFilter.length > 0 && (
          <button className="underline" onClick={()=>setScratchSeverityFilter([])}>Limpiar severidad</button>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {items.map(it => {
          const analysisAny = it.analysis as any
            // Asegura arrays
          const rawDamage: any[] = Array.isArray(analysisAny?.damage) ? analysisAny.damage : []

          const damageBoxes = (showDamage && rawDamage.length)
            ? rawDamage
                .filter(d =>
                  (damageFilter.length === 0 || damageFilter.includes(d.label)) &&
                  (showScratches || d.label !== 'scratch') &&
                  (d.label !== 'scratch' ||
                    scratchSeverityFilter.length === 0 ||
                    (d.scratch_severity && scratchSeverityFilter.includes(d.scratch_severity.severity)))
                )
                .map(d => ({
                  box: d.box,
                  label: d.label === 'scratch' && d.scratch_severity
                    ? `${d.label} (${d.scratch_severity.severity})`
                    : d.label,
                  confidence: d.confidence,
                  type: 'damage' as const
                }))
            : []

          return (
            <div key={it.key} className="border rounded-xl p-3 bg-white space-y-1">
              <div className="text-sm font-semibold">{it.label}</div>
              {it.url
                ? (damageBoxes.length
                    ? <BoxesOverlay src={it.url} boxes={damageBoxes}/>
                    : <img src={it.url} alt={it.label} className="rounded mb-1 max-h-56 object-contain w-full" />)
                : <div className="h-40 flex items-center justify-center text-xs text-gray-500">Sin imagen</div>
              }

              {analysisAny?.quality_status && (
                <div className="text-[11px]">
                  Calidad: <span className={
                    analysisAny.quality_status==='very_blur'?'text-red-600':
                    analysisAny.quality_status==='blur'?'text-amber-600':
                    analysisAny.quality_status==='warn'?'text-amber-500':'text-green-600'
                  }>{analysisAny.quality_status}</span>
                </div>
              )}

              {analysisAny?.illumination && (
                <div className="text-[11px]">
                  Luz: {analysisAny.illumination.status} |
                  Mean {analysisAny.illumination.mean != null ? analysisAny.illumination.mean.toFixed(1) : '—'} /
                  DR {analysisAny.illumination.dynamic_range != null
                      ? analysisAny.illumination.dynamic_range.toFixed(1) : '—'}
                  {analysisAny.illumination.flags?.length > 0 && (
                    <div className="text-amber-600">
                      Flags: {analysisAny.illumination.flags.join(', ')}
                    </div>
                  )}
                </div>
              )}

              {analysisAny?.background && (
                <div className="text-[11px]">
                  Fondo: {analysisAny.background.label}
                  {analysisAny.background.score!=null && ` (${Math.round(analysisAny.background.score*100)}%)`}
                  {analysisAny.background.policy?.inconsistent && (
                    <span className="text-red-600"> (inconsistente)</span>
                  )}
                </div>
              )}

              {analysisAny?.segmentation?.coverage_ratio != null && (
                <div className="text-[11px]">
                  Cobertura seg: {(analysisAny.segmentation.coverage_ratio*100).toFixed(1)}%
                </div>
              )}

              {analysisAny?.ocr?.plate_candidates?.length > 0 && (
                <div className="text-[11px]">
                  OCR Placa: {analysisAny.ocr.plate_candidates[0]?.text}
                </div>
              )}

              {analysisAny?.tamper && (
                <div className={`text-[11px] ${analysisAny.tamper.suspect?'text-red-600':'text-green-600'}`}>
                  Tamper: {analysisAny.tamper.suspect ? 'SOSPECHOSO' : 'OK'}
                  {analysisAny.tamper.reasons?.length > 0 && (
                    <span> [{analysisAny.tamper.reasons.join(', ')}]</span>
                  )}
                </div>
              )}

              {rawDamage.some(d=>d.label==='scratch' && d.scratch_severity) && showScratches && (
                <div className="text-[11px]">
                  Severidades: {rawDamage
                    .filter(d=>d.label==='scratch' && d.scratch_severity)
                    .map(d=>d.scratch_severity.severity)
                    .join(', ')}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="border rounded-xl p-4 bg-gray-50 text-sm space-y-2">
        <div><strong>Placa:</strong> {user?.plate || finalAny?.plate || '—'}</div>
        {finalAny?.inspection_id && <div><strong>ID:</strong> {finalAny.inspection_id}</div>}
        {finalAny?.status && <div><strong>Estado:</strong> {finalAny.status}</div>}
        {finalAny?.color_evaluation && (
          <div className="text-xs">
            <strong>Color fraude:</strong> {finalAny.color_evaluation.fraud ? 'Sí':'No'} |
            mismatch {finalAny.color_evaluation.mismatch_ratio!=null
              ? (finalAny.color_evaluation.mismatch_ratio*100).toFixed(1) : '—'}%
          </div>
        )}
        {finalAny?.ocr_summary && (
          <div className="text-xs">
            <strong>OCR Placa:</strong> {finalAny.ocr_summary.plate_candidates?.[0]?.text || 'N/D'} |
            <strong> VIN:</strong> {finalAny.ocr_summary.vin_detected || 'N/D'}
          </div>
        )}
        {finalAny?.fraud_flags?.length > 0 && (
          <div className="text-xs text-red-600">
            <strong>Fraud:</strong> {finalAny.fraud_flags.join(', ')}
          </div>
        )}
        {finalAny?.part_completeness_score != null && (
          <div className="text-xs">
            <strong>Completitud partes:</strong> {(finalAny.part_completeness_score*100).toFixed(1)}%
          </div>
        )}
        {finalAny?.inspection_id && pdfEnabled && (
          <Button variant="secondary" onClick={handleDownloadPdf} disabled={downloading}>
            {downloading ? 'Descargando...' : 'PDF'}
          </Button>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <Button onClick={reset}>Nueva</Button>
      </div>
    </div>
  )
}