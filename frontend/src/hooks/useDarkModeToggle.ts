import { useEffect, useState } from 'react'

export function useDarkModeToggle() {
  const prefers = window.matchMedia('(prefers-color-scheme: dark)')
  const [dark, setDark] = useState(prefers.matches)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  return { dark, setDark }
}