import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Download, RotateCcw } from 'lucide-react';
import { Button } from '../../../components/common/Button';
import { useInspection } from '../../../contexts/InspectionContext';
import { Damage } from '../../../types/inspection';

export const Results: React.FC = () => {
  const { detectionResult, imagePreview, resetInspection } = useInspection();

  if (!detectionResult) return null;

  const DamageItem: React.FC<{ damage: Damage }> = ({ damage }) => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <span className="font-semibold text-red-800 capitalize">{damage.type}</span>
        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
          {(damage.confidence * 100).toFixed(1)}% seguro
        </span>
      </div>
      <p className="text-red-700 text-sm">Ubicación: {damage.location}</p>
    </div>
  );

  return (
    <div className="text-center">
      <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-6 ${
        detectionResult.hasDamage ? 'bg-red-100' : 'bg-green-100'
      }`}>
        {detectionResult.hasDamage ? (
          <AlertTriangle size={32} className="text-red-600" />
        ) : (
          <CheckCircle size={32} className="text-green-600" />
        )}
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        {detectionResult.hasDamage ? 'Daños Detectados' : '¡Vehículo en Buen Estado!'}
      </h2>

      <div className={`p-4 rounded-lg mb-6 ${
        detectionResult.hasDamage ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'
      }`}>
        <p className="font-medium">{detectionResult.message}</p>
      </div>

      {detectionResult.hasDamage && (
        <div className="mb-6 text-left">
          <h3 className="font-semibold text-gray-700 mb-3">Detalles de los daños:</h3>
          <div className="space-y-3">
            {detectionResult.damages.map((damage, index) => (
              <DamageItem key={index} damage={damage} />
            ))}
          </div>
        </div>
      )}

      <div className="mb-6">
        <h3 className="font-semibold text-gray-700 mb-3">Imagen analizada:</h3>
        <img 
          src={imagePreview} 
          alt="Resultado de inspección" 
          className="max-w-full h-auto rounded-lg shadow-md mx-auto max-h-64 object-contain"
        />
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button icon={Download} variant="outline">
          Descargar Reporte
        </Button>
        <Button onClick={resetInspection} icon={RotateCcw}>
          Nueva Inspección
        </Button>
      </div>

      {!detectionResult.hasDamage && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-blue-800 text-sm">
            💡 <strong>Recomendación:</strong> Te sugerimos realizar una inspección física adicional 
            para verificar el estado completo del vehículo.
          </p>
        </div>
      )}
    </div>
  );
};