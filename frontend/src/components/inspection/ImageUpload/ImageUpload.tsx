import React from 'react'
import { useInspectionStore } from '@/hooks/useInspectionStore'
import { UserForm } from '../UserForm'

export const ImageUpload: React.FC = () => {
  const { state } = useInspectionStore()
  const { currentStep } = state;
  
  return (
    <div className="text-center">
      {currentStep === 'user-info' && <UserForm />}
    </div>
  );
};