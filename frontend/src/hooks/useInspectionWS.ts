import { useEffect, useRef } from 'react'
import { useInspectionStore } from './useInspectionStore'

export function useInspectionWS(sessionId: string | null) {
  const { setAbort } = useInspectionStore()
  const ref = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!sessionId) return
    const base = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/,'')
    const wsUrl = base.replace(/^http/,'ws') + `/ws/inspection/${sessionId}`
    const ws = new WebSocket(wsUrl)
    ref.current = ws

    ws.onmessage = ev => {
      try {
        const data = JSON.parse(ev.data)
        if (data.event === 'session:aborted') {
          setAbort(data.reason || 'ABORT')
        }
      } catch { /* ignore */ }
    }
    ws.onclose = () => { ref.current = null }
    return () => { ws.close() }
  }, [sessionId, setAbort])
}