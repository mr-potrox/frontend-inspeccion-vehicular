const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Verificar vehículo
export async function verifyVehicle(plate: string) {
  const res = await fetch(`${API_BASE_URL}/inspection/verify?plate=${plate}`);
  return res.json();
}

// Verificar calidad de imagen
export async function checkImageQuality(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/inspection/quality`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

// Detectar daños en imagen
export async function detectDamage(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/inspection/damage`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

// Subir imagen con metadatos
export async function uploadInspectionImage({ file, tipo, lat, lon, sessionId }: {
  file: File,
  tipo: string,
  lat?: number,
  lon?: number,
  sessionId: string
}) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('tipo', tipo);
  if (lat) formData.append('lat', lat.toString());
  if (lon) formData.append('lon', lon.toString());
  formData.append('session_id', sessionId);
  const res = await fetch(`${API_BASE_URL}/inspection/upload`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

// Guardar nota
export async function saveInspectionNote(sessionId: string, note: string) {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('note', note);
  const res = await fetch(`${API_BASE_URL}/inspection/note`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

// Obtener resultado de inspección
export async function getInspectionResult(sessionId: string) {
  const res = await fetch(`${API_BASE_URL}/inspection/result?session_id=${sessionId}`);
  return res.json();
}

// Descargar informe
export async function downloadInspectionReport(sessionId: string) {
  const res = await fetch(`${API_BASE_URL}/inspection/report?session_id=${sessionId}`);
  return res.json(); // O res.blob() si es PDF
}