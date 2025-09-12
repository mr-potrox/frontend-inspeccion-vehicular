import { AnalyzeImageResponse, FinalizeResponse, QualityThresholds } from '@/types/inspection'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').trim()
const BASE = API_BASE_URL || 'http://localhost:8000'
function buildUrl(path: string) { return `${BASE.replace(/\/+$/, '')}${path}` }

async function fetchWithControl(
  url: string,
  opts: RequestInit = {},
  timeoutMs = 20000,
  retries = 1
): Promise<Response> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), timeoutMs)
    try {
      const res = await fetch(url, { ...opts, signal: ctrl.signal })
      clearTimeout(timer)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res
    } catch (e) {
      clearTimeout(timer)
      if (attempt === retries) throw e
      await new Promise(r => setTimeout(r, 600 * (attempt + 1)))
    }
  }
  throw new Error('unreachable')
}

export interface ApiVersionInfo {
  version?: string
  build?: string
  commit?: string
}
export async function getApiVersion(): Promise<ApiVersionInfo> {
  const r = await fetchWithControl(buildUrl('/model/info'), {}, 6000, 0)
  return r.json()
}

export interface HealthInfo {
  status: string
  model_version?: string
  models?: {
    damage: { name: string; path: string; default_conf: number }
    parts: { name: string; path: string; default_conf: number }
  }
  quality_thresholds?: QualityThresholds
  debug_images_enabled?: boolean
  pdf_enabled?: boolean
  labels?: {
    damage_labels: string[]
    part_labels: string[]
  }
  config_version?: number
}
export async function getHealth(): Promise<HealthInfo> {
  const r = await fetchWithControl(buildUrl('/health'), {}, 6000, 0)
  return r.json()
}

export interface VehicleVerifyData {
  plate: string
  brand?: string
  model?: string
  year?: string
  owner?: string
  id?: string
  history?: any
}
export interface VehicleVerifyResponse {
  found: boolean
  data?: VehicleVerifyData
}

const VEH_CACHE_TTL_MS = 10 * 60 * 1000

export async function verifyVehicle(plateRaw: string): Promise<VehicleVerifyResponse> {
  const plate = plateRaw.toUpperCase().trim()
  const key = `veh_verify_${plate}`
  try {
    const cached = sessionStorage.getItem(key)
    if (cached) {
      const parsed = JSON.parse(cached)
      if (Date.now() - parsed.t < VEH_CACHE_TTL_MS) return parsed.v
      sessionStorage.removeItem(key)
    }
  } catch {}
  const res = await fetchWithControl(buildUrl(`/inspection/verify?plate=${encodeURIComponent(plate)}`), {}, 10000, 0)
  const json: VehicleVerifyResponse = await res.json()
  try { sessionStorage.setItem(key, JSON.stringify({ t: Date.now(), v: json })) } catch {}
  return json
}

export interface IdentityVerifyRequest {
  name: string
  document: string
}
export interface IdentityVerifyResponse {
  valid: boolean
  matched_driver?: any
}
export async function verifyIdentity(payload: IdentityVerifyRequest): Promise<IdentityVerifyResponse> {
  const res = await fetchWithControl(buildUrl('/identity/verify'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, 8000, 0)
  return res.json()
}

export interface VehicleHistoryResponse {
  plate: string
  infractions: number
  previous_owners: number
  tech_ok: boolean
  notes: string[]
}
export async function getVehicleHistory(plate: string): Promise<VehicleHistoryResponse> {
  const r = await fetchWithControl(buildUrl(`/vehicle/history?plate=${encodeURIComponent(plate)}`), {}, 8000, 0)
  return r.json()
}

export async function analyzeImage(params: {
  file: File
  sessionId: string
  plate: string
  lat?: number
  lon?: number
  note?: string
  confDamage?: number
  confParts?: number
  debug?: boolean
  photoKey?: string
}): Promise<AnalyzeImageResponse> {
  const form = new FormData()
  form.append('file', params.file)
  form.append('session_id', params.sessionId)
  form.append('plate', params.plate)
  if (params.photoKey) form.append('photo_key', params.photoKey)
  if (params.lat != null) form.append('browser_lat', String(params.lat))
  if (params.lon != null) form.append('browser_lon', String(params.lon))
  if (params.note) form.append('note', params.note)
  if (params.confDamage != null) form.append('conf_damage', String(params.confDamage))
  if (params.confParts != null) form.append('conf_parts', String(params.confParts))
  if (params.debug) form.append('debug', '1')
  const res = await fetchWithControl(buildUrl('/inspection/analyze'), { method: 'POST', body: form }, 30000, 1)
  return res.json()
}

export async function finalizeInspection(
  sessionId: string,
  plate: string,
  confDamage?: number,
  confParts?: number
): Promise<FinalizeResponse> {
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('plate', plate)
  if (confDamage != null) form.append('conf_damage', String(confDamage))
  if (confParts != null) form.append('conf_parts', String(confParts))
  const res = await fetchWithControl(buildUrl('/inspection/finalize'), { method: 'POST', body: form }, 35000, 1)
  return res.json()
}

export async function getReportPdf(inspectionId: string): Promise<Blob> {
  const res = await fetchWithControl(buildUrl(`/inspection/report/${inspectionId}/pdf`))
  return res.blob()
}