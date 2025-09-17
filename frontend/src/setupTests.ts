import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock URL API for blob handling
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock WebSocket for testing
class MockWebSocket {
  url: string
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onopen: (() => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
  }

  close() {
    if (this.onclose) {
      this.onclose()
    }
  }

  send(data: string) {
    // Mock implementation
  }
}

Object.defineProperty(global, 'WebSocket', {
  value: MockWebSocket,
  writable: true
})

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: vi.fn(() => 'mock-uuid-' + Math.random().toString(36).slice(2))
  },
  writable: true
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Suppress console errors in tests unless needed
const originalError = console.error
beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalError
})