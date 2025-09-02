import React from 'react';
import { InspectionStep } from '../../types/inspection';
import { ImageUpload } from './ImageUpload/ImageUpload';
import { QualityCheck } from './QualityCheck/QualityCheck';
import { Results } from './Results/Results';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ProgressStepper } from '../common/ProgressStepper';
import { useInspection } from '../../contexts/InspectionContext';

export const InspectionFlow: React.FC = () => {
  const { currentStep, isProcessing } = useInspection();

  if (isProcessing) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <LoadingSpinner 
          title="Procesando imagen" 
          message="Estamos analizando tu vehículo, esto puede tomar unos segundos..." 
          size="lg"
        />
      </div>
    );
  }

  return (
    <>
      <ProgressStepper currentStep={currentStep} />
      
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {currentStep === 'upload' && <ImageUpload />}
        {currentStep === 'quality-check' && <QualityCheck />}
        {currentStep === 'results' && <Results />}
      </div>
    </>
  )
}