import { useState } from 'react';
import { InspectionState, InspectionStep } from '../types/inspection';

export const useInspectionStore = () => {
  const [state, setState] = useState<InspectionState>({
    currentStep: 'upload',
    uploadedImage: null,
    imagePreview: '',
    qualityResult: null,
    detectionResult: null,
    isProcessing: false,
    error: null
  });

  const setCurrentStep = (step: InspectionStep) => {
    setState(prev => ({ ...prev, currentStep: step }));
  };

  const setUploadedImage = (file: File | null, preview: string = '') => {
    setState(prev => ({ ...prev, uploadedImage: file, imagePreview: preview }));
  };

  const setQualityResult = (result: InspectionState['qualityResult']) => {
    setState(prev => ({ ...prev, qualityResult: result }));
  };

  const setDetectionResult = (result: InspectionState['detectionResult']) => {
    setState(prev => ({ ...prev, detectionResult: result }));
  };

  const setIsProcessing = (processing: boolean) => {
    setState(prev => ({ ...prev, isProcessing: processing }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const resetInspection = () => {
    setState({
      currentStep: 'upload',
      uploadedImage: null,
      imagePreview: '',
      qualityResult: null,
      detectionResult: null,
      isProcessing: false,
      error: null
    });
  };

  return {
    ...state,
    setCurrentStep,
    setUploadedImage,
    setQualityResult,
    setDetectionResult,
    setIsProcessing,
    setError,
    resetInspection
  };
};