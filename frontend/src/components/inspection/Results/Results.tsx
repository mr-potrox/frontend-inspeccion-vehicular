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
  const [scratchSeverityFilter, setScratchSeverityFilter] = useState<string[]>([])

  useEffect(() => {
    (async () => {
      try {
        const h = await getHealth()
        if (h.pdf_enabled === false) setPdfEnabled(false)
        if (h.labels?.damage_labels) setAvailableDamageLabels(h.labels.damage_labels)
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

  let illumMeanAvg: string | undefined
  let illumDRAvg: string | undefined
  if (final?.illumination_frames?.length) {
    const means = final.illumination_frames.map((f: any) => f.mean || 0)
    const drs = final.illumination_frames.map((f: any) => f.dynamic_range || 0)
    const avg = (a: number[]) => a.reduce((p,c)=>p+c,0)/Math.max(1,a.length)
    illumMeanAvg = avg(means).toFixed(1)
    illumDRAvg = avg(drs).toFixed(1)
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
    } finally { setDownloading(false) }
  }

  const messages = aborted
    ? ['⚠️ Inspección abortada', 'Motivo: ' + (state.abortReason || 'No especificado')]
    : ['✅ Inspección completada', final?.status || '']

  const scratchSevLabels = ['minor','moderate','severe']

  return (
    <div className="space-y-6">
      <CoachChat messages={messages} />

      {(illumMeanAvg || final?.fraud_flags?.length) && (
        <div className="border rounded-xl p-4 bg-white text-xs flex flex-wrap gap-4 items-center">
          {illumMeanAvg && (
            <>
              <div><strong>Ilum. Mean:</strong> {illumMeanAvg}</div>
              <div><strong>Ilum. DR:</strong> {illumDRAvg}</div>
            </>
          )}
          {final?.fraud_flags?.length > 0 && (
            <div className="text-red-600">
              Fraud: {final.fraud_flags.join(', ')}
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
          const analysis = it.analysis
          const damageBoxes = (showDamage && analysis?.damage)
            ? analysis.damage
                .filter((d: any) =>
                  (damageFilter.length === 0 || damageFilter.includes(d.label)) &&
                  (d.label !== 'scratch' || scratchSeverityFilter.length === 0 ||
                    (d.scratch_severity && scratchSeverityFilter.includes(d.scratch_severity.severity)))
                )
                .map((d: any) => ({
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

              {analysis?.quality_status && (
                <div className="text-[11px]">
                  Calidad: <span className={
                    analysis.quality_status==='very_blur'?'text-red-600':
                    analysis.quality_status==='blur'?'text-amber-600':
                    analysis.quality_status==='warn'?'text-amber-500':'text-green-600'
                  }>{analysis.quality_status}</span>
                </div>
              )}

              {analysis?.illumination && (
                <div className="text-[11px]">
                  Luz: {analysis.illumination.status} |
                  Mean {analysis.illumination.mean?.toFixed(1)} /
                  DR {analysis.illumination.dynamic_range?.toFixed(1)}
                  {analysis.illumination.flags?.length > 0 && (
                    <div className="text-amber-600">
                      Flags: {analysis.illumination.flags.join(', ')}
                    </div>
                  )}
                </div>
              )}

              {analysis?.background && (
                <div className="text-[11px]">
                  Fondo: {analysis.background.label} ({Math.round(analysis.background.score*100)}%)
                  {analysis.background.policy?.inconsistent && (
                    <span className="text-red-600"> (inconsistente)</span>
                  )}
                </div>
              )}

              {analysis?.segmentation?.coverage_ratio != null && (
                <div className="text-[11px]">
                  Cobertura seg: {(analysis.segmentation.coverage_ratio*100).toFixed(1)}%
                </div>
              )}

              {analysis?.ocr?.plate_candidates?.length > 0 && (
                <div className="text-[11px]">
                  OCR Placa: {analysis.ocr.plate_candidates[0].text}
                </div>
              )}

              {analysis?.tamper && (
                <div className={`text-[11px] ${analysis.tamper.suspect?'text-red-600':'text-green-600'}`}>
                  Tamper: {analysis.tamper.suspect ? 'SOSPECHOSO' : 'OK'}
                  {analysis.tamper.reasons?.length > 0 && (
                    <span> [{analysis.tamper.reasons.join(', ')}]</span>
                  )}
                </div>
              )}

              {analysis?.damage && analysis.damage.some((d:any)=>d.label==='scratch' && d.scratch_severity) && (
                <div className="text-[11px]">
                  Severidades: {analysis.damage
                    .filter((d:any)=>d.label==='scratch' && d.scratch_severity)
                    .map((d:any)=>d.scratch_severity.severity)
                    .join(', ')}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="border rounded-xl p-4 bg-gray-50 text-sm space-y-2">
        <div><strong>Placa:</strong> {user?.plate}</div>
        {final?.inspection_id && <div><strong>ID:</strong> {final.inspection_id}</div>}
        {final?.status && <div><strong>Estado:</strong> {final.status}</div>}
        {final?.color_evaluation && (
          <div className="text-xs">
            <strong>Color fraude:</strong> {final.color_evaluation.fraud ? 'Sí':'No'} |
            mismatch {(final.color_evaluation.mismatch_ratio*100).toFixed(1)}%
          </div>
        )}
        {final?.ocr_summary && (
          <div className="text-xs">
            <strong>OCR Placa:</strong> {final.ocr_summary.plate_candidates?.[0]?.text || 'N/D'} |
            <strong> VIN:</strong> {final.ocr_summary.vin_detected || 'N/D'}
          </div>
        )}
        {final?.fraud_flags?.length > 0 && (
            <div className="text-xs text-red-600">
              <strong>Fraud:</strong> {final.fraud_flags.join(', ')}
            </div>
        )}
        {final?.part_completeness_score != null && (
          <div className="text-xs">
            <strong>Completitud partes:</strong> {(final.part_completeness_score*100).toFixed(1)}%
          </div>
        )}
        {final?.inspection_id && pdfEnabled && (
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