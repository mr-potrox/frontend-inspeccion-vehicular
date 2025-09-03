import React, { useState, useEffect } from "react";
import { InspectionProvider } from "@/hooks/useInspectionStore";
import InspectionFlow from "@/components/inspection/InspectionFlow/InspectionFlow";
import Button from "@/components/common/Button/Button";
import CoachChat from "@/components/common/CoachChat/CoachChat";

export default function App() {
  const [isMobile, setIsMobile] = useState(() =>
    window.innerWidth <= 600 &&
    /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  );
  const [started, setStarted] = useState(false); // <-- Mueve aquí

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(
        window.innerWidth <= 600 &&
        /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
      );
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!isMobile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-xl shadow text-center max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-4">Solo disponible en modo móvil</h2>
          <p>
            Por favor abre esta aplicación en tu teléfono móvil y/o ajusta el tamaño de la ventana para simular un dispositivo móvil.
          </p>
        </div>
      </div>
    );
  }

  return (
    <InspectionProvider>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        {!started ? (
          <div className="text-center max-w-lg">
            <img
              src="/logo.png"
              alt="Logo Inspección Vehicular"
              className="mx-auto w-28 h-28 mb-6"
            />
            <CoachChat
              messages={[
                "👋 ¡Hola! Soy tu asistente de inspección vehicular.",
                "Vamos a revisar paso a paso tu vehículo 🚗",
                "Cuando estés listo, haz clic en Iniciar Inspección ✅",
              ]}
            />
            <div className="mt-6">
              <Button variant="primary" onClick={() => setStarted(true)}>
                Iniciar Inspección
              </Button>
            </div>
          </div>
        ) : (
          <div className="w-full">
            <InspectionFlow />
          </div>
        )}
      </div>
    </InspectionProvider>
  );
}