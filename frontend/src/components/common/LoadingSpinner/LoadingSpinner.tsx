import React from 'react';
import { Loader } from 'lucide-react';

export interface LoadingSpinnerProps {
  title?: string;
  message?: string;
  size?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  title = "Procesando",
  message = "Por favor espere...",
  size = 28,
  className
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader className={`animate-spin text-primary-600 mb-4 ${sizeClasses[size]}`} />
      {title && <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>}
      {message && <p className="text-gray-600 text-center">{message}</p>}
    </div>
  );
};