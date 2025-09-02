// src/components/inspection/ImageUpload.tsx
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Camera, MapPin, RefreshCw, Video, X, AlertCircle } from 'lucide-react';
import { Button } from '../../../components/common/Button';
import { useInspection } from '../../../contexts/InspectionContext';
import { useImageProcessing } from '../../../hooks/useImageProcessing';

export const ImageUpload: React.FC = () => {
  const { setUploadedImage, setCurrentStep, setIsProcessing, setQualityResult } = useInspection();
  const { processImageQuality } = useImageProcessing();

  const [geoData, setGeoData] = useState<{ lat: number; lon: number } | null>(null);
  const [geoError, setGeoError] = useState<string | null>(null);
  const [isGettingLocation, setIsGettingLocation] = useState<boolean>(true);
  const [fileName, setFileName] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [cameraPermission, setCameraPermission] = useState<PermissionState | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Verificar permisos de cámara
  const checkCameraPermission = useCallback(async () => {
    try {
      if (!navigator.permissions) {
        console.log("Permissions API no disponible");
        return;
      }
      
      const permissionStatus = await navigator.permissions.query({ name: 'camera' as PermissionName });
      setCameraPermission(permissionStatus.state);
      
      permissionStatus.onchange = () => {
        setCameraPermission(permissionStatus.state);
      };
    } catch (error) {
      console.log("No se pudo verificar el estado del permiso de cámara:", error);
    }
  }, []);

  // Función para obtener geolocalización
  const getGeolocation = useCallback(async () => {
    if (!("geolocation" in navigator)) {
      setGeoError("Geolocalización no soportada en este navegador");
      setIsGettingLocation(false);
      return;
    }

    // Verificar permisos primero
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'geolocation' });
      
      if (permissionStatus.state === 'denied') {
        setGeoError("Permisos de geolocalización denegados. Por favor, habilita los permisos de ubicación en tu navegador.");
        setIsGettingLocation(false);
        return;
      }
    } catch (error) {
      console.warn("No se pudo verificar permisos de geolocalización:", error);
    }

    setIsGettingLocation(true);
    setGeoError(null);

    const geoOptions = {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0
    };

    const success = (position: GeolocationPosition) => {
      const coords = {
        lat: position.coords.latitude,
        lon: position.coords.longitude
      };
      setGeoData(coords);
      setGeoError(null);
      setIsGettingLocation(false);
      console.log("📍 Geolocalización obtenida:", coords);
    };

    const error = (err: GeolocationPositionError) => {
      console.warn(`ERROR(${err.code}): ${err.message}`);
      
      let errorMessage = "No se pudo obtener la geolocalización";
      switch (err.code) {
        case err.PERMISSION_DENIED:
          errorMessage = "Permisos de geolocalización denegados. Por favor, habilita los permisos de ubicación en tu navegador.";
          break;
        case err.POSITION_UNAVAILABLE:
          errorMessage = "La información de ubicación no está disponible. Verifica tu conexión o GPS.";
          break;
        case err.TIMEOUT:
          errorMessage = "Tiempo de espera agotado. Intenta nuevamente.";
          break;
      }
      
      setGeoError(errorMessage);
      setGeoData(null);
      setIsGettingLocation(false);
    };

    navigator.geolocation.getCurrentPosition(success, error, geoOptions);
  }, []);

  // 🔑 Pedir geolocalización apenas cargue el componente
  useEffect(() => {
    getGeolocation();
    checkCameraPermission();
  }, [getGeolocation, checkCameraPermission]);

  // Función fallback para obtener ubicación por IP
  const getGeolocationByIP = async () => {
    try {
      setIsGettingLocation(true);
      const response = await fetch('https://ipapi.co/json/');
      const data = await response.json();
      
      if (data.latitude && data.longitude) {
        setGeoData({
          lat: data.latitude,
          lon: data.longitude
        });
        setGeoError(null);
        console.log("📍 Geolocalización aproximada por IP:", data);
      } else {
        setGeoError("No se pudo obtener ubicación aproximada");
      }
    } catch (error) {
      console.warn("No se pudo obtener geolocalización por IP");
      setGeoError("No se pudo obtener ninguna forma de ubicación");
    } finally {
      setIsGettingLocation(false);
    }
  };

  // Iniciar cámara
  const startCamera = async () => {
    try {
      setCameraError(null);
      
      // Verificar si ya tenemos permisos
      if (cameraPermission === 'denied') {
        setCameraError("Permiso de cámara denegado. Por favor, habilita los permisos de cámara en la configuración de tu navegador.");
        return;
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }, 
        audio: false 
      });
      
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setShowCamera(true);
      // Actualizar estado de permisos
      setCameraPermission('granted');
    } catch (err) {
      console.error("Error al acceder a la cámara:", err);
      if (err instanceof DOMException && err.name === 'NotAllowedError') {
        setCameraError("Permiso de cámara denegado. Por favor, habilita los permisos de cámara en la configuración de tu navegador.");
        setCameraPermission('denied');
      } else if (err instanceof DOMException && err.name === 'NotFoundError') {
        setCameraError("No se encontró ninguna cámara disponible.");
      } else {
        setCameraError("No se pudo acceder a la cámara. Asegúrate de dar los permisos necesarios.");
      }
    }
  };

  // Detener cámara
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
  };

  // Capturar foto desde la cámara
  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async (blob) => {
          if (blob) {
            const file = new File([blob], `vehicle-photo-${new Date().getTime()}.jpg`, { 
              type: 'image/jpeg' 
            });
            
            stopCamera();
            await handleFileWithGeo(file);
          }
        }, 'image/jpeg', 0.9);
      }
    }
  };

  const handleFileWithGeo = async (file: File) => {
    const preview = URL.createObjectURL(file);
    setUploadedImage(file, preview);
    setFileName(file.name);
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
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      await handleFileWithGeo(file);
    }
  }, [setUploadedImage, setCurrentStep, setIsProcessing, setQualityResult, processImageQuality]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1
  });

  // Función para abrir configuración de permisos (solo funciona en algunos navegadores)
  const openPermissionSettings = () => {
    // Esto solo funciona en algunos navegadores móviles
    if (navigator.userAgent.includes('Android') || navigator.userAgent.includes('iPhone')) {
      window.open('app-settings://');
    } else {
      alert("Por favor, abre manualmente la configuración de tu navegador para gestionar los permisos.");
    }
  };

  return (
    <div className="text-center">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Sube una imagen de tu vehículo</h2>
      
      {/* Estado de geolocalización */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-center mb-2">
          <MapPin className="text-blue-500 mr-2" size={20} />
          <h3 className="font-medium text-blue-800">Estado de geolocalización</h3>
        </div>
        
        {isGettingLocation ? (
          <div className="flex items-center justify-center text-blue-700">
            <RefreshCw className="animate-spin mr-2" size={16} />
            <p>Obteniendo ubicación...</p>
          </div>
        ) : geoError ? (
          <div className="text-amber-700">
            <p className="mb-2">{geoError}</p>
            <div className="flex flex-col sm:flex-row justify-center space-y-2 sm:space-y-0 sm:space-x-2 mt-3">
              <Button onClick={getGeolocation} variant="outline" size="sm">
                <RefreshCw size={14} className="mr-1" /> Reintentar GPS
              </Button>
              <Button onClick={getGeolocationByIP} variant="outline" size="sm">
                Usar ubicación aproximada
              </Button>
              <Button onClick={openPermissionSettings} variant="outline" size="sm">
                <AlertCircle size={14} className="mr-1" /> Configurar permisos
              </Button>
            </div>
          </div>
        ) : geoData ? (
          <div className="text-green-700">
            <p>Ubicación obtenida correctamente</p>
            <p className="text-sm mt-1">
              Lat: {geoData.lat.toFixed(6)}, Lon: {geoData.lon.toFixed(6)}
            </p>
          </div>
        ) : null}
      </div>

      {/* Vista de cámara */}
      {showCamera ? (
        <div className="camera-container mb-6">
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-64 object-cover"
            />
            <button
              onClick={stopCamera}
              className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full"
            >
              <X size={20} />
            </button>
          </div>
          
          {cameraError && (
            <div className="mt-2 p-2 bg-red-100 text-red-700 rounded">
              {cameraError}
              <div className="mt-2">
                <Button onClick={openPermissionSettings} variant="outline" size="sm">
                  <AlertCircle size={14} className="mr-1" /> Configurar permisos
                </Button>
              </div>
            </div>
          )}
          
          <div className="mt-4 flex justify-center space-x-4">
            <Button onClick={capturePhoto} className="flex items-center">
              <Camera size={18} className="mr-2" />
              Capturar foto
            </Button>
            <Button onClick={stopCamera} variant="outline">
              Cancelar
            </Button>
          </div>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-colors mb-6 ${
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
                
                <div className="flex flex-col sm:flex-row gap-3">
                  {/* Botón para seleccionar archivo */}
                  <label htmlFor="file-input">
                    <Button icon={Upload} variant="secondary">
                      Seleccionar archivo
                    </Button>
                  </label>
                  <input
                    id="file-input"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileWithGeo(e.target.files[0]);
                      }
                    }}
                  />
                  
                  {/* Botón para usar cámara */}
                  <Button 
                    onClick={startCamera} 
                    icon={Video} 
                    variant="primary"
                    disabled={cameraPermission === 'denied'}
                  >
                    {cameraPermission === 'denied' ? 'Permiso denegado' : 'Usar cámara'}
                  </Button>
                </div>
                
                {cameraPermission === 'denied' && (
                  <div className="mt-2 p-2 bg-red-100 text-red-700 rounded text-sm">
                    <p>Permiso de cámara denegado. Por favor, habilita los permisos de cámara en la configuración de tu navegador.</p>
                    <Button onClick={openPermissionSettings} variant="outline" size="sm" className="mt-2">
                      <AlertCircle size={14} className="mr-1" /> Configurar permisos
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* 📦 BOX de información de la imagen */}
      {(fileName || geoData) && (
        <div className="mt-8 text-left bg-green-50 rounded-lg p-4 border border-green-200 shadow-sm">
          <h3 className="font-semibold text-green-800 mb-2">📋 Información de la imagen:</h3>
          <ul className="text-green-700 list-disc list-inside space-y-1">
            {fileName && <li><strong>Archivo:</strong> {fileName}</li>}
            {geoData ? (
              <>
                <li><strong>Latitud:</strong> {geoData.lat.toFixed(6)}</li>
                <li><strong>Longitud:</strong> {geoData.lon.toFixed(6)}</li>
              </>
            ) : (
              <li>No se pudo obtener geolocalización</li>
            )}
          </ul>
        </div>
      )}

      {/* Estilos para la cámara */}
      <style>{`
        .camera-container {
          position: relative;
        }
        @media (max-width: 640px) {
          .camera-container {
            margin: 0 -1rem;
          }
        }
      `}</style>
    </div>
  );
};