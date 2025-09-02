// src/components/inspection/ImageUpload.tsx
import React from 'react';
import { useInspection } from '../../../contexts/InspectionContext';
import { UserForm } from '../UserForm';
import { UploadImages } from '../UploadImages';

export const ImageUpload: React.FC = () => {
  const { currentStep } = useInspection();

  return (
    <div className="text-center">
      {currentStep === 'user-info' && <UserForm />}
      {currentStep === 'upload-image' && <UploadImages />}
    </div>
  );
};
