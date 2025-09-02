import React, { useState } from "react";
import { InspectionProvider } from "@/hooks/useInspectionStore";
import InspectionFlow from "@/components/inspection/InspectionFlow/InspectionFlow";
import Button from "@/components/common/Button/Button";
import CoachChat from "@/components/common/CoachChat/CoachChat";

export default function App() {
  const [started, setStarted] = useState(false);

  return (
    <InspectionProvider>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        {!started ? (
          // Landing Page
          <div className="text-center max-w-lg">
            {/* Logo */}
            <img
              src="/logo.png"
              alt="Logo Inspección Vehicular"
              className="mx-auto w-28 h-28 mb-6"
            />

            {/* Mensajes del Coach */}
            <CoachChat
              messages={[
                "👋 ¡Hola! Soy tu asistente de inspección vehicular.",
                "Vamos a revisar paso a paso tu vehículo 🚗",
                "Cuando estés listo, haz clic en Iniciar Inspección ✅",
              ]}
            />

            {/* Botón para iniciar */}
            <div className="mt-6">
              <Button variant="primary" onClick={() => setStarted(true)}>
                Iniciar Inspección
              </Button>
            </div>
          </div>
        ) : (
          // Flujo de inspección
          <div className="w-full">
            <InspectionFlow />
          </div>
        )}
      </div>
    </InspectionProvider>
  );
}
