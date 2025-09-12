import { useEffect } from 'react'

export function usePrefetch(when: boolean, importer: () => Promise<unknown>) {
  useEffect(() => {
    if (when) {
      importer()
        .catch(() => { /* silent */ })
    }
  }, [when, importer])
}