// src/components/inspection/UserForm.tsx
import React, { useState } from 'react';
import { Button } from '../../components/common/Button';
import { useInspection } from '../../contexts/InspectionContext';

interface UserInfo {
  name: string;
  idNumber: string;
  plate: string;
}

export const UserForm: React.FC = () => {
  const { setCurrentStep, setUserInfo: setGlobalUserInfo } = useInspection();
  const [userInfo, setUserInfo] = useState<UserInfo>({ name: '', idNumber: '', plate: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInfo.name || !userInfo.idNumber || !userInfo.plate) {
      alert('Por favor completa todos los campos');
      return;
    }
    setGlobalUserInfo(userInfo); // guardamos info globalmente si es necesario
    setCurrentStep('upload-image'); // avanzar al paso de imágenes
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto text-left bg-gray-50 p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Identificación del usuario</h2>

      <label className="block">
        Nombre:
        <input type="text" value={userInfo.name} onChange={(e) => setUserInfo({ ...userInfo, name: e.target.value })} className="w-full mt-1 p-2 border rounded" required />
      </label>

      <label className="block">
        Número de identificación:
        <input type="text" value={userInfo.idNumber} onChange={(e) => setUserInfo({ ...userInfo, idNumber: e.target.value })} className="w-full mt-1 p-2 border rounded" required />
      </label>

      <label className="block">
        Placa del vehículo:
        <input type="text" value={userInfo.plate} onChange={(e) => setUserInfo({ ...userInfo, plate: e.target.value })} className="w-full mt-1 p-2 border rounded" required />
      </label>

      <Button type="submit">Continuar</Button>
    </form>
  );
};
