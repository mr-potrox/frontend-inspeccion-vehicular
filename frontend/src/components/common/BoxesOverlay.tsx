import React from 'react'

interface Box {
  box: [number, number, number, number]
  label?: string
  confidence?: number
  aspect?: number
  type: 'damage' | 'scratch'
}

export const BoxesOverlay: React.FC<{
  src: string
  width?: number
  height?: number
  boxes: Box[]
  showLabels?: boolean
}> = ({ src, boxes, showLabels = true }) => {
  return (
    <div className="relative w-full max-h-56 overflow-hidden flex items-center justify-center bg-black/5 rounded-lg">
      <img
        src={src}
        alt="analyzed"
        className="object-contain max-h-56 w-auto select-none pointer-events-none rounded"
        draggable={false}
      />
      <div className="absolute inset-0 pointer-events-none">
        {boxes.map((b, i) => {
          const [x1, y1, x2, y2] = b.box
          const left = `${x1}px`
            , top = `${y1}px`
            , w = `${x2 - x1}px`
            , h = `${y2 - y1}px`
          const color = b.type === 'damage' ? 'rgba(255,0,0,0.55)' : 'rgba(0,120,255,0.55)'
          const border = b.type === 'damage' ? 'border-red-500' : 'border-blue-500'
          return (
            <div
              key={i}
              className={`absolute ${border} border-2 rounded-sm`}
              style={{ left, top, width: w, height: h }}
            >
              {showLabels && (
                <div
                  className="absolute -top-5 left-0 text-[10px] px-1 py-[1px] rounded text-white"
                  style={{ background: color }}
                >
                  {b.type === 'damage'
                    ? `${b.label || 'damage'}${b.confidence != null ? ` ${(b.confidence * 100).toFixed(0)}%` : ''}`
                    : `scratch${b.aspect ? ` a:${b.aspect}` : ''}`
                  }
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}