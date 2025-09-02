import React from 'react';
import { Car } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="text-center mb-12">
      <div className="flex items-center justify-center mb-4">
        <Car className="text-primary-600 mr-3" size={32} />
        <h1 className="text-4xl font-bold text-gray-900">
          Inspección Vehicular IA
        </h1>
      </div>
      <p className="text-lg text-gray-600 max-w-2xl mx-auto">
        Sistema inteligente para detectar y clasificar daños en vehículos mediante visión por computadora
      </p>
    </header>
  );
};