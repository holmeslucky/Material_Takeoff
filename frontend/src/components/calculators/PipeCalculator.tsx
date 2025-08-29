import React, { useState, useEffect } from 'react'
import { Calculator, Plus, RefreshCw, Play, Trash2 } from 'lucide-react'

interface PipeCalculatorProps {
  onWeldInchesCalculated?: (weldInches: number, weldFeet: number, calculation: any) => void
}

interface PipeComponent {
  name: string
  qty: number
  welds: number
  type: 'Butt' | 'Fillet'
}

interface CalculationResult {
  totalInches: number
  totalFeet: number
  circumference: number
  weldCount: number
  od: number
  effectiveFactor: number
  passes: number
  explanation: string
}

// NPS to OD lookup table (ASME B36.10/B36.19)
const NPS_OD: Record<string, number> = {
  "0.5": 0.840, "0.75": 1.050, "1": 1.315, "1.25": 1.660, "1.5": 1.900, "2": 2.375,
  "2.5": 2.875, "3": 3.500, "3.5": 4.000, "4": 4.500, "5": 5.563, "6": 6.625,
  "8": 8.625, "10": 10.750, "12": 12.750, "14": 14.000, "16": 16.000, "18": 18.000,
  "20": 20.000, "22": 22.000, "24": 24.000, "26": 26.000, "28": 28.000, "30": 30.000,
  "32": 32.000, "34": 34.000, "36": 36.000
}

const PipeCalculator: React.FC<PipeCalculatorProps> = ({ onWeldInchesCalculated }) => {
  // Line size parameters
  const [nps, setNps] = useState("4")
  const [od, setOd] = useState(4.500)
  const [eff, setEff] = useState(1.0)
  
  // Component parameters
  const [buttJoints, setButtJoints] = useState(0)
  const [passes, setPasses] = useState(1)
  const [roundTo, setRoundTo] = useState(0.01)

  // Components array
  const [components, setComponents] = useState<PipeComponent[]>([
    { name: "Elbow (BW)", qty: 0, welds: 2, type: "Butt" },
    { name: "Tee (BW)", qty: 0, welds: 3, type: "Butt" },
    { name: "Reducer (BW)", qty: 0, welds: 2, type: "Butt" },
    { name: "Cap (BW)", qty: 0, welds: 1, type: "Butt" },
    { name: "Weld Neck Flange", qty: 0, welds: 1, type: "Butt" },
    { name: "Slip‑On Flange", qty: 0, welds: 2, type: "Fillet" },
    { name: "Valve (BW ends)", qty: 0, welds: 2, type: "Butt" }
  ])

  // Results
  const [result, setResult] = useState<CalculationResult | null>(null)

  const fmt = (value: number, step: number) => {
    const dec = Math.max(0, (String(step).split(".")[1]?.length || 0))
    return Number(value).toFixed(dec)
  }

  const circumference = (diameter: number) => Math.PI * diameter

  const calculate = () => {
    const currentOd = od || NPS_OD[nps] || 0
    const effFactor = Math.max(0, Math.min(1, eff))
    const passCount = Math.max(1, Math.floor(passes))
    const buttCount = Math.max(0, Math.floor(buttJoints))

    const circ = circumference(currentOd)
    let weldCount = buttCount // Start with straight butt joints

    // Sum component welds
    components.forEach(component => {
      const qty = Math.max(0, Math.floor(component.qty))
      const welds = Math.max(0, Math.floor(component.welds))
      weldCount += qty * welds
    })

    const totalIn = circ * weldCount * passCount * effFactor
    const totalFt = totalIn / 12

    const calculationResult: CalculationResult = {
      totalInches: totalIn,
      totalFeet: totalFt,
      circumference: circ,
      weldCount,
      od: currentOd,
      effectiveFactor: effFactor,
      passes: passCount,
      explanation: `OD=${fmt(currentOd, 0.001)} in; Circumference=π×OD=${fmt(circ, 0.01)} in; Weld events=${weldCount}; Passes=${passCount}; Eff=${effFactor}`
    }

    setResult(calculationResult)

    // Call callback if provided
    if (onWeldInchesCalculated) {
      onWeldInchesCalculated(totalIn, totalFt, calculationResult)
    }
  }

  const addComponent = () => {
    setComponents([...components, {
      name: "Custom",
      qty: 0,
      welds: 1,
      type: "Butt"
    }])
  }

  const removeComponent = (index: number) => {
    setComponents(components.filter((_, i) => i !== index))
  }

  const updateComponent = (index: number, field: keyof PipeComponent, value: any) => {
    const newComponents = [...components]
    newComponents[index] = { ...newComponents[index], [field]: value }
    setComponents(newComponents)
  }

  const runExample = () => {
    setNps("6")
    setOd(NPS_OD["6"])
    setEff(1.0)
    setPasses(2)
    setButtJoints(6)
    
    // Example components: 4 elbows, 2 tees, 2 WN flanges, 1 valve
    const exampleComponents = [...components]
    exampleComponents.forEach(c => { c.qty = 0 })
    exampleComponents[0].qty = 4 // elbows BW (2 welds each)
    exampleComponents[1].qty = 2 // tees BW (3 welds each)
    exampleComponents[4].qty = 2 // WN flanges (1 weld each)
    exampleComponents[6].qty = 1 // valve (2 welds)
    setComponents(exampleComponents)
  }

  const reset = () => {
    setNps("4")
    setOd(4.500)
    setEff(1.0)
    setButtJoints(0)
    setPasses(1)
    setRoundTo(0.01)
    setComponents([
      { name: "Elbow (BW)", qty: 0, welds: 2, type: "Butt" },
      { name: "Tee (BW)", qty: 0, welds: 3, type: "Butt" },
      { name: "Reducer (BW)", qty: 0, welds: 2, type: "Butt" },
      { name: "Cap (BW)", qty: 0, welds: 1, type: "Butt" },
      { name: "Weld Neck Flange", qty: 0, welds: 1, type: "Butt" },
      { name: "Slip‑On Flange", qty: 0, welds: 2, type: "Fillet" },
      { name: "Valve (BW ends)", qty: 0, welds: 2, type: "Butt" }
    ])
    setResult(null)
  }

  // Handle NPS change
  const handleNpsChange = (newNps: string) => {
    setNps(newNps)
    setOd(NPS_OD[newNps] || 0)
  }

  // Auto-calculate on input change
  useEffect(() => {
    calculate()
  }, [nps, od, eff, buttJoints, passes, roundTo, components])

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-6 h-6 text-purple-400" />
        <h3 className="text-xl font-semibold text-white">Pipe Weld Inches Calculator</h3>
      </div>
      <p className="text-gray-400 mb-6">
        Compute weld inches for a pipe line with common fittings & flanges. Uses line size OD for 
        circumferential welds; add passes & factors as needed.
      </p>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main Inputs Section */}
        <div className="xl:col-span-2 space-y-6">
          {/* Line Size */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-white">Line Size</h4>
            
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">NPS (Nominal Pipe Size)</label>
                <select
                  value={nps}
                  onChange={(e) => handleNpsChange(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                >
                  {Object.keys(NPS_OD).map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  OD (inches)
                  <span className="text-xs text-gray-400 block">(auto from NPS, override if needed)</span>
                </label>
                <input
                  type="number"
                  step="0.001"
                  min="0"
                  value={od}
                  onChange={(e) => setOd(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Effective Factor (0–1)
                  <span className="text-xs text-gray-400 block">deduct cutouts/gaps</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={eff}
                  onChange={(e) => setEff(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
          </div>

          {/* Components Parameters */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-white">Components</h4>
            
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Butt Joints (pipe-to-pipe)</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={buttJoints}
                  onChange={(e) => setButtJoints(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Passes (for butt/fillet)</label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={passes}
                  onChange={(e) => setPasses(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Round Result To</label>
                <select
                  value={roundTo}
                  onChange={(e) => setRoundTo(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-purple-500"
                >
                  <option value={0.01}>0.01 in</option>
                  <option value={0.1}>0.1 in</option>
                  <option value={1}>1 in</option>
                </select>
              </div>
            </div>
          </div>

          {/* Components Table */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-medium text-white">Pipe Components</h4>
              <button
                onClick={addComponent}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Custom Component
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse bg-gray-700 rounded-lg">
                <thead>
                  <tr className="border-b border-gray-600">
                    <th className="text-left p-3 text-sm text-gray-300">Component</th>
                    <th className="text-left p-3 text-sm text-gray-300">Qty</th>
                    <th className="text-left p-3 text-sm text-gray-300">Welds per Item</th>
                    <th className="text-left p-3 text-sm text-gray-300">Type</th>
                    <th className="text-left p-3 text-sm text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {components.map((component, index) => (
                    <tr key={index} className="border-b border-gray-600">
                      <td className="p-2">
                        <input
                          value={component.name}
                          onChange={(e) => updateComponent(index, 'name', e.target.value)}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={component.qty}
                          onChange={(e) => updateComponent(index, 'qty', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={component.welds}
                          onChange={(e) => updateComponent(index, 'welds', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <select
                          value={component.type}
                          onChange={(e) => updateComponent(index, 'type', e.target.value as 'Butt' | 'Fillet')}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        >
                          <option value="Butt">Butt</option>
                          <option value="Fillet">Fillet</option>
                        </select>
                      </td>
                      <td className="p-2">
                        {index >= 7 && (
                          <button
                            onClick={() => removeComponent(index)}
                            className="text-red-400 hover:text-red-300 p-1"
                            title="Remove component"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="text-xs text-gray-400">
              Assumptions: BW fittings use circumferential butt welds; slip‑on flanges use two fillet welds (both sides). 
              All taken at line OD. Adjust "Welds per Item" if your detail is different.
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={runExample}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Play className="w-4 h-4" />
              Quick Example
            </button>
            <button
              onClick={reset}
              className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h4 className="text-lg font-medium text-white">Results</h4>
          
          {result && (
            <>
              {/* KPI Cards */}
              <div className="space-y-3">
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Weld Inches (total)</div>
                  <div className="text-xl font-bold text-purple-400">{fmt(result.totalInches, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Weld Feet (total)</div>
                  <div className="text-xl font-bold text-purple-400">{fmt(result.totalFeet, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Per Circumference</div>
                  <div className="text-lg font-bold text-purple-400">{fmt(result.circumference, 0.01)} in</div>
                </div>
              </div>

              {/* Explanation */}
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-sm text-gray-300">{result.explanation}</div>
              </div>
            </>
          )}

          {/* Presets / Notes */}
          <div className="bg-gray-700 rounded-lg p-4">
            <h5 className="text-sm font-medium text-white mb-2">Presets / Notes</h5>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• <strong>Elbow (BW):</strong> usually 2 butt welds</li>
              <li>• <strong>Tee (BW):</strong> 3 butt welds (2 run + 1 branch) – assumes branch same NPS</li>
              <li>• <strong>Reducer (BW):</strong> 2 butt welds</li>
              <li>• <strong>Cap (BW):</strong> 1 butt weld</li>
              <li>• <strong>Weld Neck Flange:</strong> 1 butt weld</li>
              <li>• <strong>Slip‑On Flange:</strong> 2 fillet welds (both sides)</li>
              <li>• <strong>Valve (BW ends):</strong> 2 butt welds</li>
            </ul>
            <div className="text-xs text-gray-400 mt-2">
              <strong>Formula:</strong> <em>Total</em> = (π × OD) × (Sum over components: Qty × Welds/Item) × Passes × EffectiveFactor.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PipeCalculator