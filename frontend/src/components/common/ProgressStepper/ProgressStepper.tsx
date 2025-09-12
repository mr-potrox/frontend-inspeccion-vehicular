import React from 'react'
import { motion } from 'framer-motion'

export function ProgressStepper({ steps, active }: { steps: string[]; active: number }) {
  return (
    <div className="w-full bg-transparent p-2">
      <div className="flex items-center gap-4">
        {steps.map((s, i) => {
          const done = i < active
          const isActive = i === active
            return (
              <div key={s} className="flex-1">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs ${done ? 'bg-green-500 text-white' : isActive ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}>
                    {i + 1}
                  </div>
                  <div className={`${isActive ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>{s}</div>
                </div>
                {i < steps.length - 1 && (
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    className={`h-1 mt-2 rounded ${i < active ? 'bg-green-300' : 'bg-gray-200'}`}
                  />
                )}
              </div>
            )
        })}
      </div>
    </div>
  )
}