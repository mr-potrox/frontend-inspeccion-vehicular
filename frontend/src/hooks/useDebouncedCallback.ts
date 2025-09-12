import { useRef, useCallback } from 'react'

export function useDebouncedCallback<T extends (...a:any[])=>void>(fn: T, delay = 400) {
  const ref = useRef<number>()
  return useCallback((...args: Parameters<T>) => {
    if (ref.current) window.clearTimeout(ref.current)
    ref.current = window.setTimeout(() => fn(...args), delay)
  }, [fn, delay])
}