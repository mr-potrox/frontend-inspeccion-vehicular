import React, { createContext, useContext } from 'react';
import { useInspectionStore } from '../hooks/useInspectionStore';

const InspectionContext = createContext<ReturnType<typeof useInspectionStore> | null>(null);

export const useInspection = () => {
  const context = useContext(InspectionContext);
  if (!context) {
    throw new Error('useInspection must be used within an InspectionProvider');
  }
  return context;
};

export const InspectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = useInspectionStore();

  return (
    <InspectionContext.Provider value={store}>
      {children}
    </InspectionContext.Provider>
  );
};