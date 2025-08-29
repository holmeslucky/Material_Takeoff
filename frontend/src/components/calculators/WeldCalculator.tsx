import React, { useState, useEffect } from 'react'
import { Calculator, RefreshCw, Play } from 'lucide-react'

interface WeldCalculatorProps {
  onWeldInchesCalculated?: (weldInches: number, weldFeet: number, calculation: any) => void
}

interface CalculationResult {
  totalInches: number
  totalFeet: number
  perSeam: number
  baseLength: number
  effectiveFactor: number
  stitchFraction: number
  passes: number
  seams: number
  explanation: string
}

const WeldCalculator: React.FC<WeldCalculatorProps> = ({ onWeldInchesCalculated }) => {
  // State for form inputs
  const [seamType, setSeamType] = useState<'circ' | 'custom'>('circ')
  const [seams, setSeams] = useState(1)
  const [od, setOd] = useState(165)
  const [eff, setEff] = useState(1.0)
  const [customLen, setCustomLen] = useState(120)
  const [eff2, setEff2] = useState(1.0)
  const [stitch, setStitch] = useState(false)
  const [stitchLen, setStitchLen] = useState(2)
  const [skipLen, setSkipLen] = useState(2)
  const [passes, setPasses] = useState(1)
  const [roundTo, setRoundTo] = useState(0.01)

  // State for results
  const [result, setResult] = useState<CalculationResult | null>(null)

  const fmt = (value: number, step: number) => {
    const dec = Math.max(0, (String(step).split(".")[1]?.length || 0))
    return Number(value).toFixed(dec)
  }

  const currentBaseLength = () => {
    if (seamType === 'circ') {
      return Math.PI * od
    } else {
      return customLen
    }
  }

  const effectiveFactor = () => {
    if (seamType === 'circ') {
      return Math.max(0, Math.min(1, eff))
    } else {
      return Math.max(0, Math.min(1, eff2))
    }
  }

  const stitchFraction = () => {
    if (!stitch) return 1
    const denom = stitchLen + skipLen
    if (denom <= 0) return 1
    return stitchLen / denom
  }

  const calculate = () => {
    const seamCount = Math.max(1, Math.floor(seams))
    const passCount = Math.max(1, Math.floor(passes))

    const base = currentBaseLength()
    const effFactor = effectiveFactor()
    const stitchFrac = stitchFraction()

    const perSeam = base * effFactor * stitchFrac * passCount
    const totalIn = perSeam * seamCount
    const totalFt = totalIn / 12

    // Build explanation
    let detail = []
    if (seamType === 'circ') {
      detail.push(`Circumference = π × OD = ${fmt(Math.PI * od, 0.01)} in`)
    } else {
      detail.push(`Custom seam length = ${fmt(base, 0.01)} in`)
    }
    detail.push(`Effective factor = ${effFactor}`)
    if (stitch) {
      detail.push(`Stitch fraction = ${fmt(stitchLen, 0.01)} / (${fmt(stitchLen, 0.01)} + ${fmt(skipLen, 0.01)}) = ${fmt(stitchFrac, 0.01)}`)
    } else {
      detail.push(`Stitch fraction = 1 (continuous weld)`)
    }
    detail.push(`Passes = ${passCount}, Seams = ${seamCount}`)

    const calculationResult: CalculationResult = {
      totalInches: totalIn,
      totalFeet: totalFt,
      perSeam: perSeam,
      baseLength: base,
      effectiveFactor: effFactor,
      stitchFraction: stitchFrac,
      passes: passCount,
      seams: seamCount,
      explanation: detail.join(' • ')
    }

    setResult(calculationResult)

    // Call callback if provided
    if (onWeldInchesCalculated) {
      onWeldInchesCalculated(totalIn, totalFt, calculationResult)
    }
  }

  const runExample = () => {
    setSeamType('circ')
    setOd(165)
    setSeams(2)
    setPasses(2)
    setStitch(false)
    setEff(1.0)
    setRoundTo(0.1)
  }

  const reset = () => {
    setSeamType('circ')
    setSeams(1)
    setOd(165)
    setEff(1.0)
    setCustomLen(120)
    setEff2(1.0)
    setStitch(false)
    setStitchLen(2)
    setSkipLen(2)
    setPasses(1)
    setRoundTo(0.01)
    setResult(null)
  }

  // Auto-calculate on input change
  useEffect(() => {
    calculate()
  }, [seamType, seams, od, eff, customLen, eff2, stitch, stitchLen, skipLen, passes, roundTo])

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-6 h-6 text-orange-400" />
        <h3 className="text-xl font-semibold text-white">Ductwork Weld Inches Calculator</h3>
      </div>
      <p className="text-gray-400 mb-6">Compute total weld inches for circumferential or custom seams. Handles stitch welds, multipass, and multiple seams.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inputs Section */}
        <div className="space-y-4">
          <h4 className="text-lg font-medium text-white">Inputs</h4>
          
          {/* Seam Type and Count */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Seam Type</label>
              <select
                value={seamType}
                onChange={(e) => setSeamType(e.target.value as 'circ' | 'custom')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
              >
                <option value="circ">Circumferential (uses π × OD)</option>
                <option value="custom">Custom / Longitudinal (enter seam length)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Number of Seams</label>
              <input
                type="number"
                min="1"
                step="1"
                value={seams}
                onChange={(e) => setSeams(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>

          {/* Circumferential Inputs */}
          {seamType === 'circ' && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Outside Diameter (OD inches)</label>
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
                  Effective Weld Factor (0–1)
                  <span className="text-xs text-gray-400 block">deduct cutouts/gaps, e.g. 0.95</span>
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
            </div>
          )}

          {/* Custom Length Inputs */}
          {seamType === 'custom' && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Seam Length (inches)</label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={customLen}
                  onChange={(e) => setCustomLen(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Effective Weld Factor (0–1)</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={eff2}
                  onChange={(e) => setEff2(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
                />
              </div>
            </div>
          )}

          {/* Stitch Weld Toggle */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="stitch-weld"
              checked={stitch}
              onChange={(e) => setStitch(e.target.checked)}
              className="rounded bg-gray-700 border-gray-600"
            />
            <label htmlFor="stitch-weld" className="text-sm font-medium text-gray-300">Stitch Weld</label>
          </div>

          {/* Stitch Weld Parameters */}
          {stitch && (
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="grid grid-cols-2 gap-3 mb-2">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Stitch Length (in)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={stitchLen}
                    onChange={(e) => setStitchLen(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white focus:ring-2 focus:ring-orange-500"
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
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white focus:ring-2 focus:ring-orange-500"
                  />
                </div>
              </div>
              <div className="text-xs text-gray-400">
                Pattern = <span className="font-medium">stitch</span> then <span className="font-medium">skip</span>. 
                Effective fraction = stitch / (stitch + skip).
              </div>
            </div>
          )}

          {/* Additional Parameters */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Number of Passes</label>
              <input
                type="number"
                min="1"
                step="1"
                value={passes}
                onChange={(e) => setPasses(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-2 focus:ring-orange-500"
              />
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

          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={runExample}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Play className="w-4 h-4" />
              Example (165" OD, 2 seams, 2-pass)
            </button>
            <button
              onClick={reset}
              className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Reset
            </button>
          </div>

          <div className="text-xs text-gray-400">
            Tip: For a full circumferential weld, total length per seam is the circumference. For longitudinal seams, enter the seam length.
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h4 className="text-lg font-medium text-white">Results</h4>
          
          {result && (
            <>
              {/* KPI Cards */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Weld Inches (total)</div>
                  <div className="text-lg font-bold text-orange-400">{fmt(result.totalInches, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Weld Feet (total)</div>
                  <div className="text-lg font-bold text-orange-400">{fmt(result.totalFeet, roundTo)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-xs text-gray-400 mb-1">Per Seam (inches)</div>
                  <div className="text-lg font-bold text-orange-400">{fmt(result.perSeam, roundTo)}</div>
                </div>
              </div>

              {/* Explanation */}
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-sm text-gray-300">{result.explanation}</div>
              </div>

              {/* Formula */}
              <div className="text-xs text-gray-400">
                <strong>Formula:</strong> BaseLength × EffectiveFactor × StitchFraction × Passes × Seams. 
                For circumferential seams, BaseLength = π × OD.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default WeldCalculator