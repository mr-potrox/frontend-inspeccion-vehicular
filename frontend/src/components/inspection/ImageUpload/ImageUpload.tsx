import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Camera } from 'lucide-react';
import { Button } from '../../../components/common/Button';
import { useInspection } from '../../../contexts/InspectionContext';
import { useImageProcessing } from '../../../hooks/useImageProcessing';

export const ImageUpload: React.FC = () => {
  const { setUploadedImage, setCurrentStep, setIsProcessing, setQualityResult } = useInspection();
  const { processImageQuality } = useImageProcessing();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      const preview = URL.createObjectURL(file);
      setUploadedImage(file, preview);
      setCurrentStep('quality-check');
      
      setIsProcessing(true);
      try {
        const qualityResult = await processImageQuality(file);
        setQualityResult(qualityResult);
      } catch (error) {
        console.error('Error processing image quality:', error);
      } finally {
        setIsProcessing(false);
      }
    }
  }, [setUploadedImage, setCurrentStep, setIsProcessing, setQualityResult, processImageQuality]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1
  });

  return (
    <div className="text-center">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Sube una imagen de tu vehículo</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <Upload className="text-primary-600" size={32} />
          </div>
          
          {isDragActive ? (
            <p className="text-lg text-primary-600">Suelta la imagen aquí...</p>
          ) : (
            <>
              <p className="text-lg text-gray-700">Arrastra y suelta una imagen aquí</p>
              <p className="text-gray-500">o</p>
              <Button icon={Camera}>
                Seleccionar archivo
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="mt-8 text-left bg-blue-50 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-2">Requisitos de la imagen:</h3>
        <ul className="text-blue-700 list-disc list-inside space-y-1">
          <li>Formatos aceptados: JPG, PNG</li>
          <li>Resolución mínima: 640x480 píxeles</li>
          <li>Tamaño máximo: 10MB</li>
          <li>Buena iluminación y enfoque nítido</li>
          <li>Toma la foto desde varios ángulos para mejor detección</li>
        </ul>
      </div>
    </div>
  );
};