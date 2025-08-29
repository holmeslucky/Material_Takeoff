import React, { useState, useEffect } from 'react'
import { Calculator, Info } from 'lucide-react'

interface PlateInterfaceProps {
  onPlateDataChange: (data: any) => void
  isCalculating?: boolean
}

export default function PlateInterface({ onPlateDataChange, isCalculating = false }: PlateInterfaceProps) {
  const [plateData, setPlateData] = useState({
    qty: 1,
    shape_key: 'PL1/4',
    thickness: 0.25,
    width_in: 0,
    length_ft: 0,
    length_in: 0,
    description: ''
  })
  
  const [plateResult, setPlateResult] = useState<any>(null)

  const plateThicknesses = [
    { key: 'PL1/8', thickness: 0.125, display: '1/8"' },
    { key: 'PL1/4', thickness: 0.25, display: '1/4"' },
    { key: 'PL3/8', thickness: 0.375, display: '3/8"' },
    { key: 'PL1/2', thickness: 0.5, display: '1/2"' },
    { key: 'PL5/8', thickness: 0.625, display: '5/8"' },
    { key: 'PL3/4', thickness: 0.75, display: '3/4"' },
    { key: 'PL1', thickness: 1.0, display: '1"' },
    { key: 'PL1.25', thickness: 1.25, display: '1-1/4"' },
    { key: 'PL1.5', thickness: 1.5, display: '1-1/2"' },
  ]

  const calculatePlate = async () => {
    // Convert to feet for calculations
    const width_ft = plateData.width_in / 12  // inches to feet
    const total_length_ft = plateData.length_ft + (plateData.length_in / 12)  // feet + inches to feet
    
    if (width_ft > 0 && total_length_ft > 0) {
      try {
        const response = await fetch('/api/v1/takeoff/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            qty: plateData.qty,
            shape_key: plateData.shape_key,
            length_ft: total_length_ft,
            width_ft: width_ft,
            calculate_labor: true,
            labor_mode: 'auto'
          })
        })

        if (response.ok) {
          const result = await response.json()
          setPlateResult(result)
          onPlateDataChange(result)
        }
      } catch (error) {
        console.error('Plate calculation error:', error)
      }
    }
  }

  useEffect(() => {
    const timer = setTimeout(calculatePlate, 500)
    return () => clearTimeout(timer)
  }, [plateData])

  const handleFieldChange = (field: string, value: any) => {
    setPlateData(prev => ({ ...prev, [field]: value }))
  }

  const handleThicknessChange = (thicknessData: any) => {
    setPlateData(prev => ({
      ...prev,
      shape_key: thicknessData.key,
      thickness: thicknessData.thickness,
      description: `Plate ${thicknessData.display} thick`
    }))
  }

  const areaDimensionsClass = "text-2xl font-bold text-blue-600 bg-blue-50 border-2 border-blue-300"
  
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Calculator className="w-6 h-6 text-blue-400" />
        <h3 className="text-xl font-semibold text-white">Enhanced Plate Interface</h3>
        <div className="flex items-center gap-1 text-yellow-400">
          <Info className="w-4 h-4" />
          <span className="text-sm">Area calculations only</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Quantity</label>
            <input
              type="number"
              value={plateData.qty}
              onChange={(e) => handleFieldChange('qty', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Plate Thickness Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Plate Thickness</label>
            <div className="grid grid-cols-3 gap-2">
              {plateThicknesses.map((thick) => (
                <button
                  key={thick.key}
                  onClick={() => handleThicknessChange(thick)}
                  className={`px-3 py-2 text-sm rounded transition-colors ${
                    plateData.shape_key === thick.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {thick.display}
                </button>
              ))}
            </div>
          </div>

          {/* PROMINENT WIDTH (IN) FIELD */}
          <div>
            <label className="block text-lg font-bold text-blue-400 mb-2">
              WIDTH (IN) - REQUIRED FOR PLATES
            </label>
            <input
              type="number"
              value={plateData.width_in || ''}
              onChange={(e) => handleFieldChange('width_in', parseFloat(e.target.value) || 0)}
              step="0.25"
              placeholder="Width in inches..."
              className={`w-full px-4 py-3 ${areaDimensionsClass} rounded-lg focus:outline-none focus:ring-3 focus:ring-blue-500`}
            />
          </div>

          {/* LENGTH (FT) FIELD */}
          <div>
            <label className="block text-lg font-bold text-blue-400 mb-2">
              LENGTH (FT) - REQUIRED FOR PLATES
            </label>
            <input
              type="number"
              value={plateData.length_ft || ''}
              onChange={(e) => handleFieldChange('length_ft', parseFloat(e.target.value) || 0)}
              step="1"
              placeholder="Length in feet..."
              className={`w-full px-4 py-3 ${areaDimensionsClass} rounded-lg focus:outline-none focus:ring-3 focus:ring-blue-500`}
            />
          </div>

          {/* LENGTH (IN) FIELD */}
          <div>
            <label className="block text-lg font-bold text-blue-400 mb-2">
              LENGTH (IN) - ADDITIONAL INCHES
            </label>
            <input
              type="number"
              value={plateData.length_in || ''}
              onChange={(e) => handleFieldChange('length_in', parseFloat(e.target.value) || 0)}
              step="0.25"
              min="0"
              max="11"
              placeholder="Additional inches (0-11)..."
              className={`w-full px-4 py-3 ${areaDimensionsClass} rounded-lg focus:outline-none focus:ring-3 focus:ring-blue-500`}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
            <input
              type="text"
              value={plateData.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              placeholder="Optional description..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">Plate Calculations</h4>
          
          {plateResult ? (
            <div className="bg-gray-800 rounded-lg p-4 space-y-3">
              {/* Area Calculation */}
              <div className="bg-blue-900/30 border border-blue-700 rounded p-3">
                <div className="text-blue-300 font-medium mb-2">Area Calculation</div>
                <div className="text-white text-sm">
                  Width: {plateData.width_in}" ({(plateData.width_in / 12).toFixed(2)} ft)<br/>
                  Length: {plateData.length_ft}' {plateData.length_in}" ({(plateData.length_ft + plateData.length_in / 12).toFixed(2)} ft)<br/>
                  <strong>Area: {((plateData.width_in / 12) * (plateData.length_ft + plateData.length_in / 12)).toFixed(2)} sq ft</strong>
                </div>
              </div>

              {/* Weight */}
              <div className="flex justify-between">
                <span className="text-gray-400">Weight per Sq Ft:</span>
                <span className="text-white">{plateResult.weight_per_ft?.toFixed(2)} lbs</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-400">Total Weight:</span>
                <span className="text-white font-bold">{plateResult.total_weight_tons?.toFixed(3)} tons</span>
              </div>

              {/* Pricing */}
              <div className="flex justify-between">
                <span className="text-gray-400">Unit Price:</span>
                <span className="text-green-400">${plateResult.unit_price_per_cwt?.toFixed(2)}/cwt</span>
              </div>
              
              <div className="flex justify-between border-t border-gray-600 pt-2">
                <span className="text-white font-semibold">Total Price:</span>
                <span className="text-green-400 font-bold text-lg">${plateResult.total_price?.toFixed(2)}</span>
              </div>

              {/* Labor */}
              {plateResult.labor_hours && (
                <div className="border-t border-gray-600 pt-2 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Labor Hours:</span>
                    <span className="text-yellow-400">{plateResult.labor_hours.toFixed(1)} hrs</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Labor Cost:</span>
                    <span className="text-yellow-400">${plateResult.labor_cost?.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg p-4 text-center">
              <div className="text-gray-400">
                {plateData.width_in === 0 || (plateData.length_ft === 0 && plateData.length_in === 0)
                  ? "Enter WIDTH (IN) and LENGTH to see calculations"
                  : isCalculating 
                  ? "Calculating..."
                  : "Ready to calculate"}
              </div>
            </div>
          )}

          {/* Area Warning */}
          <div className="bg-yellow-900/30 border border-yellow-700 rounded p-3">
            <div className="flex items-start gap-2">
              <Info className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div>
                <div className="text-yellow-300 font-medium">Plate Area Mode</div>
                <div className="text-yellow-200 text-sm">
                  Plates calculate by area (width × length). No linear calculations are performed for plate materials.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}