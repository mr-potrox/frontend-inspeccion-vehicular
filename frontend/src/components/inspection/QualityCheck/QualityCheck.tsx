import React from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Button } from '../../../components/common/Button';
import { useInspection } from '../../../contexts/InspectionContext';
import { useImageProcessing } from '../../../hooks/useImageProcessing';

export const QualityCheck: React.FC = () => {
  const { qualityResult, imagePreview, uploadedImage, setCurrentStep, setDetectionResult, setIsProcessing } = useInspection();
  const { processDamageDetection } = useImageProcessing();

  const handleContinue = async () => {
    if (!uploadedImage) return;
    
    setIsProcessing(true);
    try {
      const detectionResult = await processDamageDetection(uploadedImage);
      setDetectionResult(detectionResult);
      setCurrentStep('results');
    } catch (error) {
      console.error('Error processing damage detection:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!qualityResult) return null;

  return (
    <div className="text-center">
      <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-6 ${
        qualityResult.success ? 'bg-green-100' : 'bg-red-100'
      }`}>
        {qualityResult.success ? (
          <CheckCircle size={32} className="text-green-600" />
        ) : (
          <XCircle size={32} className="text-red-600" />
        )}
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        {qualityResult.success ? '¡Calidad Aprobada!' : 'Problema con la Calidad'}
      </h2>

      <div className={`p-4 rounded-lg mb-6 ${
        qualityResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
      }`}>
        <p className="font-medium">{qualityResult.message}</p>
        {qualityResult.sharpness && (
          <p className="text-sm mt-2">Nitidez: {qualityResult.sharpness.toFixed(2)}%</p>
        )}
      </div>

      <div className="mb-6">
        <h3 className="font-semibold text-gray-700 mb-3">Imagen analizada:</h3>
        <img 
          src={imagePreview} 
          alt="Vehículo inspeccionado" 
          className="max-w-full h-auto rounded-lg shadow-md mx-auto max-h-64 object-contain"
        />
      </div>

      {qualityResult.success ? (
        <div className="space-y-4">
          <Button onClick={handleContinue} size="lg">
            Continuar con Detección de Daños
          </Button>
          <div className="flex items-center justify-center text-yellow-700 bg-yellow-50 p-3 rounded-lg">
            <AlertTriangle size={20} className="mr-2" />
            <span className="text-sm">El análisis puede tomar unos segundos</span>
          </div>
        </div>
      ) : (
        <Button onClick={() => window.location.reload()} variant="secondary">
          Intentar con Otra Imagen
        </Button>
      )}
    </div>
  );
};