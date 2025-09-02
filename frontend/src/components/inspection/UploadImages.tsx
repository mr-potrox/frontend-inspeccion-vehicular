// src/components/inspection/UploadImages.tsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Camera } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { useInspection } from '../../contexts/InspectionContext';
import { useImageProcessing } from '../../hooks/useImageProcessing';

export const UploadImages: React.FC = () => {
  const { setUploadedImage, setIsProcessing, setQualityResult, setCurrentStep } = useInspection();
  const { processImageQuality } = useImageProcessing();

  const [fileName, setFileName] = useState<string | null>(null);
  const [geoData, setGeoData] = useState<{ lat: number; lon: number } | null>(null);
  const [geoError, setGeoError] = useState<string | null>(null);

  const processFile = async (file: File, coords: { lat: number; lon: number } | null) => {
    const preview = URL.createObjectURL(file);
    setUploadedImage(file, preview);
    setFileName(file.name);

    try {
      const qualityResult = await processImageQuality(file);
      setQualityResult(qualityResult);
    } catch (error) {
      console.error('Error processing image quality:', error);
    } finally {
      setIsProcessing(false);
      setCurrentStep('quality-check');
    }
  };

  const handleFileWithGeo = async (file: File) => {
    setIsProcessing(true);

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
          setGeoData(coords);
          setGeoError(null);
          processFile(file, coords);
        },
        (err) => {
          let message = '';
          switch (err.code) {
            case 1: message = 'Permiso de ubicación denegado'; break;
            case 2: message = 'Posición no disponible'; break;
            case 3: message = 'Timeout al obtener ubicación'; break;
            default: message = 'Error desconocido';
          }
          setGeoError(message);
          setGeoData(null);
          processFile(file, null);
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    } else {
      setGeoError('Geolocalización no soportada');
      setGeoData(null);
      processFile(file, null);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) await handleFileWithGeo(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1
  });

  return (
    <>
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Sube una imagen de tu vehículo</h2>

      <div {...getRootProps()} className={`border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-colors ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}`}>
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <Upload className="text-primary-600" size={32} />
          </div>
          {isDragActive ? <p className="text-lg text-primary-600">Suelta la imagen aquí...</p> : <>
            <p className="text-lg text-gray-700">Arrastra y suelta una imagen aquí</p>
            <p className="text-gray-500">o</p>
            <label htmlFor="file-input">
              <Button icon={Camera} variant="secondary">Tomar foto o seleccionar archivo</Button>
            </label>
            <input id="file-input" type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => {
              if (e.target.files && e.target.files[0]) handleFileWithGeo(e.target.files[0]);
            }} />
          </>}
        </div>
      </div>

      {(fileName || geoData || geoError) && (
        <div className="mt-8 text-left bg-green-50 rounded-lg p-4 border border-green-200 shadow-sm">
          <h3 className="font-semibold text-green-800 mb-2">📋 Información de la inspección:</h3>
          <ul className="text-green-700 list-disc list-inside space-y-1">
            {fileName && <li><strong>Archivo:</strong> {fileName}</li>}
            {geoData ? <>
              <li><strong>Latitud:</strong> {geoData.lat.toFixed(6)}</li>
              <li><strong>Longitud:</strong> {geoData.lon.toFixed(6)}</li>
            </> : geoError ? <li>{geoError}</li> : <li>Obteniendo geolocalización...</li>}
          </ul>
        </div>
      )}
    </>
  );
};
