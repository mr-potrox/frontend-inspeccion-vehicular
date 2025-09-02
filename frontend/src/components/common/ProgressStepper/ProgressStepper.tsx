import React from 'react';
import { CheckCircle } from 'lucide-react';
import { InspectionStep } from '../../../types/inspection';

interface ProgressStepperProps {
  currentStep: InspectionStep;
}

const steps: { key: InspectionStep; label: string }[] = [
  { key: 'upload', label: 'Subir imagen' },
  { key: 'quality-check', label: 'Verificar calidad' },
  { key: 'damage-detection', label: 'Detección de daños' },
  { key: 'results', label: 'Resultados' }
];

export const ProgressStepper: React.FC<ProgressStepperProps> = ({ currentStep }) => {
  const currentIndex = steps.findIndex(step => step.key === currentStep);

  return (
    <div className="flex justify-between items-center mb-8 relative">
      <div className="absolute top-1/2 left-0 right-0 h-1 bg-gray-200 -translate-y-1/2 -z-10"></div>
      
      {steps.map((step, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;
        
        return (
          <div key={step.key} className="flex flex-col items-center relative bg-white px-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
              isCurrent ? 'bg-primary-600 border-primary-600 text-white' :
              isCompleted ? 'bg-green-500 border-green-500 text-white' : 
              'bg-white border-gray-300 text-gray-400'
            }`}>
              {isCompleted ? (
                <CheckCircle size={20} />
              ) : (
                index + 1
              )}
            </div>
            <span className={`text-sm font-medium mt-2 ${
              isCurrent || isCompleted ? 'text-gray-800' : 'text-gray-400'
            }`}>
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};