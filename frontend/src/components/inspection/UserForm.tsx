import React, { useState } from 'react'
import { Button } from '../common/Button'
import { useInspectionStore } from "@/hooks/useInspectionStore"
import { verifyVehicle } from "@/services/api"

export const UserForm: React.FC = () => {
  const { setStep, setUserInfo: setGlobalUserInfo } = useInspectionStore()
  const [plate, setPlate] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userData, setUserData] = useState<{ name?: string; idNumber?: string; plate?: string; brand?: string; model?: string; year?: string } | null>(null)

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await verifyVehicle(plate)
      if (result.found && result.data) {
        setUserData({
          name: result.data.owner,
          idNumber: result.data.id,
          plate: result.data.plate,
          brand: result.data.brand,
          model: result.data.model,
          year: result.data.year
        })
        setGlobalUserInfo({
          name: result.data.owner,
          idNumber: result.data.id,
          plate: result.data.plate
        })
      } else {
        setError("Vehículo no encontrado.")
        setUserData(null)
      }
    } catch {
      setError("Error al consultar el servicio.")
      setUserData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault()
    if (!userData) {
      setError('Primero verifica la placa.')
      return
    }
    setStep('front')
  }

  return (
    <form onSubmit={handleContinue} className="space-y-4 max-w-md mx-auto text-left bg-gray-50 p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Identificación del vehículo</h2>

      <label className="block">
        Placa del vehículo:
        <input
          type="text"
          value={plate}
          onChange={(e) => setPlate(e.target.value)}
          className="w-full mt-1 p-2 border rounded"
          required
        />
        <Button type="button" onClick={handleVerify} disabled={loading || !plate} className="mt-2">
          {loading ? "Verificando..." : "Verificar vehículo"}
        </Button>
      </label>

      {userData && (
        <div className="mt-4 bg-white rounded p-4 border">
          <div><strong>Nombre:</strong> {userData.name}</div>
          <div><strong>Número de identificación:</strong> {userData.idNumber}</div>
          <div><strong>Marca:</strong> {userData.brand}</div>
          <div><strong>Modelo:</strong> {userData.model}</div>
          <div><strong>Año:</strong> {userData.year}</div>
          <div><strong>Placa:</strong> {userData.plate}</div>
        </div>
      )}

      {error && <div className="text-red-600 text-sm">{error}</div>}

      <Button type="submit" disabled={!userData}>Continuar</Button>
    </form>
  )
}