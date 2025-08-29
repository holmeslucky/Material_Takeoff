import React, { useState } from 'react'
import { Calculator, ChevronDown, ChevronUp } from 'lucide-react'
import WeldCalculator from './calculators/WeldCalculator'
import ElbowCalculator from './calculators/ElbowCalculator'
import PipeCalculator from './calculators/PipeCalculator'

interface CalculatorPanelProps {
  templateCategory: 'Main Takeoff' | 'Ductwork Takeoff' | 'Pipe Takeoff'
  onWeldInchesUpdate?: (calculatorType: string, weldInches: number, weldFeet: number, calculation: any) => void
}

const CalculatorPanel: React.FC<CalculatorPanelProps> = ({ 
  templateCategory, 
  onWeldInchesUpdate 
}) => {
  const [expandedCalculators, setExpandedCalculators] = useState<{ [key: string]: boolean }>({
    weld: true,
    elbow: false,
    pipe: true
  })
  
  const [totalWeldInches, setTotalWeldInches] = useState(0)
  const [totalWeldFeet, setTotalWeldFeet] = useState(0)
  const [calculatorResults, setCalculatorResults] = useState<{ [key: string]: any }>({})

  const toggleCalculator = (calculatorKey: string) => {
    setExpandedCalculators(prev => ({
      ...prev,
      [calculatorKey]: !prev[calculatorKey]
    }))
  }

  const handleWeldInchesCalculated = (calculatorType: string, weldInches: number, weldFeet: number, calculation: any) => {
    // Update individual calculator results
    const newResults = {
      ...calculatorResults,
      [calculatorType]: { weldInches, weldFeet, calculation }
    }
    setCalculatorResults(newResults)

    // Calculate total from all calculators
    const total = Object.values(newResults).reduce((sum, result: any) => sum + (result.weldInches || 0), 0)
    const totalFeet = total / 12

    setTotalWeldInches(total)
    setTotalWeldFeet(totalFeet)

    // Call parent callback
    if (onWeldInchesUpdate) {
      onWeldInchesUpdate(calculatorType, total, totalFeet, newResults)
    }
  }

  const getAvailableCalculators = () => {
    switch (templateCategory) {
      case 'Main Takeoff':
        return []
      case 'Ductwork Takeoff':
        return ['weld', 'elbow']
      case 'Pipe Takeoff':
        return ['pipe']
      default:
        return []
    }
  }

  const availableCalculators = getAvailableCalculators()

  if (availableCalculators.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Calculator className="w-6 h-6 text-gray-400" />
          <h3 className="text-xl font-semibold text-white">Weld Calculators</h3>
        </div>
        <div className="text-center py-8">
          <Calculator className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-400 mb-2">Main Takeoff Template</h4>
          <p className="text-gray-500">
            This template focuses on structural steel and miscellaneous items. 
            Weld calculators are available in Ductwork and Pipe templates.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      {(availableCalculators.includes('weld') || availableCalculators.includes('elbow') || availableCalculators.includes('pipe')) && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Calculator className="w-5 h-5 text-green-400" />
            <h4 className="text-lg font-semibold text-white">Total Weld Summary</h4>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400 mb-1">Total Weld Inches</div>
              <div className="text-xl font-bold text-green-400">
                {totalWeldInches.toFixed(2)}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400 mb-1">Total Weld Feet</div>
              <div className="text-xl font-bold text-green-400">
                {totalWeldFeet.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Weld Calculator (Ductwork) */}
      {availableCalculators.includes('weld') && (
        <div>
          <button
            onClick={() => toggleCalculator('weld')}
            className="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-t-lg p-3 hover:bg-gray-750 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-orange-400" />
              <span className="text-white font-medium">Ductwork Weld Calculator</span>
            </div>
            {expandedCalculators.weld ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedCalculators.weld && (
            <div className="border border-gray-700 border-t-0 rounded-b-lg">
              <WeldCalculator 
                onWeldInchesCalculated={(weldInches, weldFeet, calculation) => 
                  handleWeldInchesCalculated('weld', weldInches, weldFeet, calculation)
                }
              />
            </div>
          )}
        </div>
      )}

      {/* Elbow Calculator (Ductwork) */}
      {availableCalculators.includes('elbow') && (
        <div>
          <button
            onClick={() => toggleCalculator('elbow')}
            className="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-t-lg p-3 hover:bg-gray-750 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-orange-400" />
              <span className="text-white font-medium">Gored Elbow Calculator</span>
            </div>
            {expandedCalculators.elbow ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedCalculators.elbow && (
            <div className="border border-gray-700 border-t-0 rounded-b-lg">
              <ElbowCalculator 
                onWeldInchesCalculated={(weldInches, weldFeet, calculation) => 
                  handleWeldInchesCalculated('elbow', weldInches, weldFeet, calculation)
                }
              />
            </div>
          )}
        </div>
      )}

      {/* Pipe Calculator (Pipe) */}
      {availableCalculators.includes('pipe') && (
        <div>
          <button
            onClick={() => toggleCalculator('pipe')}
            className="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-t-lg p-3 hover:bg-gray-750 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-purple-400" />
              <span className="text-white font-medium">Pipe System Calculator</span>
            </div>
            {expandedCalculators.pipe ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedCalculators.pipe && (
            <div className="border border-gray-700 border-t-0 rounded-b-lg">
              <PipeCalculator 
                onWeldInchesCalculated={(weldInches, weldFeet, calculation) => 
                  handleWeldInchesCalculated('pipe', weldInches, weldFeet, calculation)
                }
              />
            </div>
          )}
        </div>
      )}

      {/* Usage Instructions */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-white mb-2">Calculator Usage</h4>
        <div className="text-xs text-gray-400 space-y-1">
          {templateCategory === 'Ductwork Takeoff' && (
            <>
              <p>• <strong>Weld Calculator:</strong> Use for standard circumferential or longitudinal seams</p>
              <p>• <strong>Elbow Calculator:</strong> Use for gored elbows (2, 5, 7, or 9 gores)</p>
              <p>• Results are automatically combined in the Total Weld Summary above</p>
            </>
          )}
          {templateCategory === 'Pipe Takeoff' && (
            <>
              <p>• <strong>Pipe Calculator:</strong> Includes standard fittings and NPS sizing</p>
              <p>• Supports butt welds, fillet welds, and various pipe components</p>
              <p>• All calculations use standard ASME pipe outside diameters</p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default CalculatorPanel