import React, { useState, useEffect } from 'react'
import { Calculator, Plus, RefreshCw, Play, Trash2 } from 'lucide-react'

interface ElbowCalculatorProps {
  onWeldInchesCalculated?: (weldInches: number, weldFeet: number, calculation: any) => void
}

interface ElbowConfig {
  name: string
  qty: number
  gores: number
  endJoints: number
  rings: number
  longPerGore: number
}

interface CalculationResult {
  totalInches: number
  totalFeet: number
  circumference: number
  totalCircSeams: number
  totalLongInches: number
  effectiveFactor: number
  stitchFraction: number
  passes: number
  explanation: string
}

const ElbowCalculator: React.FC<ElbowCalculatorProps> = ({ onWeldInchesCalculated }) => {
  // Global parameters
  const [od, setOd] = useState(60)
  const [eff, setEff] = useState(1.0)
  const [passes, setPasses] = useState(1)
  const [stitchOn, setStitchOn] = useState(false)
  const [stitchLen, setStitchLen] = useState(2)
  const [skipLen, setSkipLen] = useState(2)
  const [roundTo, setRoundTo] = useState(0.01)

  // Elbow configurations
  const [elbows, setElbows] = useState<ElbowConfig[]>([
    { name: "Elbow A", qty: 0, gores: 2, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow B", qty: 0, gores: 5, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow C", qty: 0, gores: 7, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow D", qty: 0, gores: 9, endJoints: 2, rings: 0, longPerGore: 0 }
  ])

  // Straight duct parameters
  const [buttJoints, setButtJoints] = useState(0)
  const [ringsStraight, setRingsStraight] = useState(0)
  const [longLenStraight, setLongLenStraight] = useState(0)

  // Results
  const [result, setResult] = useState<CalculationResult | null>(null)

  const fmt = (value: number, step: number) => {
    const dec = Math.max(0, (String(step).split(".")[1]?.length || 0))
    return Number(value).toFixed(dec)
  }

  const circumference = (diameter: number) => Math.PI * diameter

  const stitchFraction = () => {
    if (!stitchOn) return 1
    const denom = stitchLen + skipLen
    if (denom <= 0) return 1
    return stitchLen / denom
  }

  const calculate = () => {
    const circ = circumference(od)
    const stitch = stitchFraction()
    const passCount = Math.max(1, Math.floor(passes))
    const effFactor = Math.max(0, Math.min(1, eff))

    let totalCircSeams = 0
    let totalLongInches = 0

    // Calculate elbow seams
    elbows.forEach(elbow => {
      const qty = Math.max(0, Math.floor(elbow.qty))
      const gores = Math.max(2, Math.floor(elbow.gores))
      const endJ = Math.max(0, Math.floor(elbow.endJoints))
      const rings = Math.max(0, Math.floor(elbow.rings))
      const longPerGore = Math.max(0, elbow.longPerGore)

      const seamsPerElbow = (gores - 1) + endJ + rings
      totalCircSeams += seamsPerElbow * qty
      totalLongInches += (longPerGore * gores) * qty
    })

    // Add straight duct
    const buttCount = Math.max(0, Math.floor(buttJoints))
    const ringCount = Math.max(0, Math.floor(ringsStraight))
    const longLen = Math.max(0, longLenStraight)

    totalCircSeams += buttCount + ringCount
    totalLongInches += longLen

    // Calculate totals
    const totalCircInches = circ * totalCircSeams
    const baseInches = totalCircInches + totalLongInches
    const totalIn = baseInches * stitch * effFactor * passCount
    const totalFt = totalIn / 12

    const calculationResult: CalculationResult = {
      totalInches: totalIn,
      totalFeet: totalFt,
      circumference: circ,
      totalCircSeams,
      totalLongInches,
      effectiveFactor: effFactor,
      stitchFraction: stitch,
      passes: passCount,
      explanation: `Circ seams=${totalCircSeams} → ${fmt(totalCircInches, 0.1)} in; Long seams=${fmt(totalLongInches, 0.1)} in; Stitch=${fmt(stitch, 0.01)}; Eff=${effFactor}; Passes=${passCount}`
    }

    setResult(calculationResult)

    // Call callback if provided
    if (onWeldInchesCalculated) {
      onWeldInchesCalculated(totalIn, totalFt, calculationResult)
    }
  }

  const addElbow = () => {
    setElbows([...elbows, {
      name: "Elbow (custom)",
      qty: 0,
      gores: 5,
      endJoints: 2,
      rings: 0,
      longPerGore: 0
    }])
  }

  const removeElbow = (index: number) => {
    setElbows(elbows.filter((_, i) => i !== index))
  }

  const updateElbow = (index: number, field: keyof ElbowConfig, value: any) => {
    const newElbows = [...elbows]
    newElbows[index] = { ...newElbows[index], [field]: value }
    setElbows(newElbows)
  }

  const runExample = () => {
    setOd(72)
    setEff(0.95)
    setPasses(2)
    setStitchOn(true)
    setStitchLen(2)
    setSkipLen(2)

    // Set example elbows: two 5-gore with rings, one 7-gore no rings
    const exampleElbows = [...elbows]
    exampleElbows.forEach(e => { e.qty = 0; e.longPerGore = 0; e.rings = 0; e.endJoints = 2 })
    exampleElbows[1].qty = 2 // 5-gore
    exampleElbows[1].rings = 1
    exampleElbows[2].qty = 1 // 7-gore
    exampleElbows[2].rings = 0
    setElbows(exampleElbows)

    setButtJoints(4)
    setRingsStraight(2)
    setLongLenStraight(0)
  }

  const reset = () => {
    setOd(60)
    setEff(1.0)
    setPasses(1)
    setStitchOn(false)
    setStitchLen(2)
    setSkipLen(2)
    setRoundTo(0.01)
    setElbows([
      { name: "Elbow A", qty: 0, gores: 2, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow B", qty: 0, gores: 5, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow C", qty: 0, gores: 7, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow D", qty: 0, gores: 9, endJoints: 2, rings: 0, longPerGore: 0 }
    ])
    setButtJoints(0)
    setRingsStraight(0)
    setLongLenStraight(0)
    setResult(null)
  }

  // Auto-calculate on input change
  useEffect(() => {
    calculate()
  }, [od, eff, passes, stitchOn, stitchLen, skipLen, roundTo, elbows, buttJoints, ringsStraight, longLenStraight])

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-6 h-6 text-orange-400" />
        <h3 className="text-xl font-semibold text-white">Duct Elbow Weld Inches Calculator</h3>
      </div>
      <p className="text-gray-400 mb-6">
        For gored elbows with <strong>2 / 5 / 7 / 9</strong> gores. Counts circumferential seams 
        (between gores + end joints + rings) and optional longitudinal seams.
      </p>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main Inputs Section */}
        <div className="xl:col-span-2 space-y-6">
          {/* Global Inputs */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-white">Global Inputs</h4>
            
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Outside Diameter (OD, inches)</label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={od}
                  onChange={(e) => setOd(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
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
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Passes</label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={passes}
                  onChange={(e) => setPasses(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
            </div>

            {/* Stitch Weld Options */}
            <div className="grid grid-cols-2 gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Stitch Weld?</label>
                  <select
                    value={stitchOn ? 'yes' : 'no'}
                    onChange={(e) => setStitchOn(e.target.value === 'yes')}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="no">No (continuous)</option>
                    <option value="yes">Yes (stitch pattern)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Round Result To</label>
                  <select
                    value={roundTo}
                    onChange={(e) => setRoundTo(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                  >
                    <option value={0.01}>0.01 in</option>
                    <option value={0.1}>0.1 in</option>
                    <option value={1}>1 in</option>
                  </select>
                </div>
              </div>
              
              {stitchOn && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Stitch Length (in)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.001"
                      value={stitchLen}
                      onChange={(e) => setStitchLen(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Skip/Spacing (in)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.001"
                      value={skipLen}
                      onChange={(e) => setSkipLen(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Elbow Components Table */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-medium text-white">Elbow Components</h4>
              <button
                onClick={addElbow}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Elbow
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse bg-gray-700 rounded-lg">
                <thead>
                  <tr className="border-b border-gray-600">
                    <th className="text-left p-3 text-sm text-gray-300">Elbow</th>
                    <th className="text-left p-3 text-sm text-gray-300">Qty</th>
                    <th className="text-left p-3 text-sm text-gray-300">Gores</th>
                    <th className="text-left p-3 text-sm text-gray-300">End Joints/Elbow</th>
                    <th className="text-left p-3 text-sm text-gray-300">Rings/Elbow</th>
                    <th className="text-left p-3 text-sm text-gray-300">Longitudinal seam per gore (in)</th>
                    <th className="text-left p-3 text-sm text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {elbows.map((elbow, index) => (
                    <tr key={index} className="border-b border-gray-600">
                      <td className="p-2">
                        <input
                          value={elbow.name}
                          onChange={(e) => updateElbow(index, 'name', e.target.value)}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={elbow.qty}
                          onChange={(e) => updateElbow(index, 'qty', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <select
                          value={elbow.gores}
                          onChange={(e) => updateElbow(index, 'gores', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        >
                          <option value={2}>2</option>
                          <option value={5}>5</option>
                          <option value={7}>7</option>
                          <option value={9}>9</option>
                        </select>
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          max="2"
                          step="1"
                          value={elbow.endJoints}
                          onChange={(e) => updateElbow(index, 'endJoints', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={elbow.rings}
                          onChange={(e) => updateElbow(index, 'rings', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="0"
                          step="0.001"
                          value={elbow.longPerGore}
                          onChange={(e) => updateElbow(index, 'longPerGore', Number(e.target.value))}
                          className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </td>
                      <td className="p-2">
                        {index >= 4 && (
                          <button
                            onClick={() => removeElbow(index)}
                            className="text-red-400 hover:text-red-300 p-1"
                            title="Remove elbow"
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
              Elbow circumferential seams per elbow = (gores − 1) + end joints + rings. Each one counts one full circumference.
            </div>
          </div>

          {/* Straight Duct Section */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-white">Straight Duct (Optional)</h4>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Butt joints (duct-to-duct)</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={buttJoints}
                  onChange={(e) => setButtJoints(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Rings (count)</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={ringsStraight}
                  onChange={(e) => setRingsStraight(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Longitudinal seam length (in)</label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={longLenStraight}
                  onChange={(e) => setLongLenStraight(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
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
                  <div className="text-xl font-bold text-orange-400">{fmt(result.totalInches, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Weld Feet (total)</div>
                  <div className="text-xl font-bold text-orange-400">{fmt(result.totalFeet, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Circumference</div>
                  <div className="text-lg font-bold text-orange-400">{fmt(result.circumference, 0.01)} in</div>
                </div>
              </div>

              {/* Explanation */}
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-sm text-gray-300">{result.explanation}</div>
              </div>
            </>
          )}

          {/* Notes */}
          <div className="bg-gray-700 rounded-lg p-4">
            <h5 className="text-sm font-medium text-white mb-2">Notes & Assumptions</h5>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• Each gored elbow with <strong>G</strong> gores has <strong>G − 1</strong> circumferential joints between gores.</li>
              <li>• Add <strong>0–2</strong> end joints per elbow depending on connections to duct/spools.</li>
              <li>• Rings add one circumferential weld apiece.</li>
              <li>• Longitudinal seams are optional—enter approximate length per gore if needed.</li>
              <li>• Results apply global: effective factor, stitch fraction, and number of passes.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ElbowCalculator