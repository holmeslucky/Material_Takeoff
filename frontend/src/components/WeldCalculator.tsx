import React, { useState, useEffect } from 'react';

interface WeldCalculatorProps {
  onCalculate?: (result: WeldCalculationResult) => void;
}

interface WeldCalculationResult {
  totalWeldInches: number;
  totalWeldFeet: number;
  perSeamInches: number;
  explanation: string;
}

const WeldCalculator: React.FC<WeldCalculatorProps> = ({ onCalculate }) => {
  const [seamType, setSeamType] = useState<'circ' | 'custom'>('circ');
  const [seams, setSeams] = useState(1);
  const [od, setOd] = useState(165);
  const [customLen, setCustomLen] = useState(120);
  const [eff, setEff] = useState(1.0);
  const [eff2, setEff2] = useState(1.0);
  const [isStitch, setIsStitch] = useState(false);
  const [stitchLen, setStitchLen] = useState(2);
  const [skipLen, setSkipLen] = useState(2);
  const [passes, setPasses] = useState(1);
  const [roundTo, setRoundTo] = useState(0.1);
  
  const [result, setResult] = useState<WeldCalculationResult>({
    totalWeldInches: 0,
    totalWeldFeet: 0,
    perSeamInches: 0,
    explanation: ''
  });

  const calculateWeld = () => {
    const numberOfSeams = Math.max(1, Math.floor(seams));
    const numberOfPasses = Math.max(1, Math.floor(passes));

    // Calculate base length
    const baseLength = seamType === 'circ' ? Math.PI * od : customLen;
    
    // Get effective factor
    const effectiveFactor = seamType === 'circ' ? 
      Math.max(0, Math.min(1, eff)) : 
      Math.max(0, Math.min(1, eff2));

    // Calculate stitch fraction
    let stitchFraction = 1;
    if (isStitch) {
      const denominator = stitchLen + skipLen;
      if (denominator > 0) {
        stitchFraction = stitchLen / denominator;
      }
    }

    const perSeamInches = baseLength * effectiveFactor * stitchFraction * numberOfPasses;
    const totalInches = perSeamInches * numberOfSeams;
    const totalFeet = totalInches / 12;

    // Build explanation
    const explanationParts = [];
    
    if (seamType === 'circ') {
      explanationParts.push(`Circumference = π × OD = ${(Math.PI * od).toFixed(2)} in`);
    } else {
      explanationParts.push(`Custom seam length = ${baseLength.toFixed(2)} in`);
    }
    
    explanationParts.push(`Effective factor = ${effectiveFactor}`);
    
    if (isStitch) {
      explanationParts.push(`Stitch fraction = ${stitchLen.toFixed(2)} / (${stitchLen.toFixed(2)} + ${skipLen.toFixed(2)}) = ${stitchFraction.toFixed(2)}`);
    } else {
      explanationParts.push(`Stitch fraction = 1 (continuous weld)`);
    }
    
    explanationParts.push(`Passes = ${numberOfPasses}, Seams = ${numberOfSeams}`);

    const newResult = {
      totalWeldInches: Math.round(totalInches / roundTo) * roundTo,
      totalWeldFeet: Math.round((totalFeet) / roundTo) * roundTo,
      perSeamInches: Math.round(perSeamInches / roundTo) * roundTo,
      explanation: explanationParts.join(' • ')
    };

    setResult(newResult);
    
    if (onCalculate) {
      onCalculate(newResult);
    }
  };

  const setExample = () => {
    setSeamType('circ');
    setOd(165);
    setSeams(2);
    setPasses(2);
    setIsStitch(false);
    setEff(1.0);
    setRoundTo(0.1);
    calculateWeld();
  };

  const resetCalculator = () => {
    setSeamType('circ');
    setSeams(1);
    setOd(165);
    setCustomLen(120);
    setEff(1.0);
    setEff2(1.0);
    setIsStitch(false);
    setStitchLen(2);
    setSkipLen(2);
    setPasses(1);
    setRoundTo(0.1);
    calculateWeld();
  };

  useEffect(() => {
    calculateWeld();
  }, [seamType, seams, od, customLen, eff, eff2, isStitch, stitchLen, skipLen, passes, roundTo]);

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-600 rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-slate-100">Ductwork Weld Calculator</h3>
        <div className="text-xs text-slate-400">
          Circumferential & Custom Seams
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inputs Section */}
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                Seam Type
              </label>
              <select
                value={seamType}
                onChange={(e) => setSeamType(e.target.value as 'circ' | 'custom')}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
              >
                <option value="circ">Circumferential (uses π × OD)</option>
                <option value="custom">Custom / Longitudinal (enter seam length)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                Number of Seams
              </label>
              <input
                type="number"
                min="1"
                step="1"
                value={seams}
                onChange={(e) => setSeams(Number(e.target.value) || 1)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
              />
            </div>
          </div>

          {seamType === 'circ' ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Outside Diameter (OD inches)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={od}
                  onChange={(e) => setOd(Number(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Effective Weld Factor (0–1)
                  <span className="text-slate-400 text-xs ml-1">— deduct cutouts/gaps</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={eff}
                  onChange={(e) => setEff(Number(e.target.value) || 1)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Seam Length (inches)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={customLen}
                  onChange={(e) => setCustomLen(Number(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Effective Weld Factor (0–1)
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={eff2}
                  onChange={(e) => setEff2(Number(e.target.value) || 1)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
            </div>
          )}

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="stitch"
              checked={isStitch}
              onChange={(e) => setIsStitch(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
            />
            <label htmlFor="stitch" className="text-sm font-medium text-slate-300">
              Stitch Weld
            </label>
          </div>

          {isStitch && (
            <div className="bg-slate-700 rounded-lg p-4 space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Stitch Length (in)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={stitchLen}
                    onChange={(e) => setStitchLen(Number(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-lg text-slate-200 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Skip/Spacing (in)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={skipLen}
                    onChange={(e) => setSkipLen(Number(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-lg text-slate-200 text-sm"
                  />
                </div>
              </div>
              <div className="text-xs text-slate-400">
                Pattern = <strong>stitch</strong> then <strong>skip</strong>. Effective fraction = stitch / (stitch + skip).
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                Number of Passes
              </label>
              <input
                type="number"
                min="1"
                step="1"
                value={passes}
                onChange={(e) => setPasses(Number(e.target.value) || 1)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                Round Result To
              </label>
              <select
                value={roundTo}
                onChange={(e) => setRoundTo(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
              >
                <option value={0.01}>0.01 in</option>
                <option value={0.1}>0.1 in</option>
                <option value={1}>1 in</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={calculateWeld}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Calculate
            </button>
            <button
              onClick={setExample}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Quick Example
            </button>
            <button
              onClick={resetCalculator}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-slate-200">Results</h4>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Weld Inches (total)</div>
              <div className="text-lg font-bold text-slate-100">{result.totalWeldInches.toFixed(2)}</div>
            </div>
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Weld Feet (total)</div>
              <div className="text-lg font-bold text-slate-100">{result.totalWeldFeet.toFixed(2)}</div>
            </div>
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Per Seam (inches)</div>
              <div className="text-lg font-bold text-slate-100">{result.perSeamInches.toFixed(2)}</div>
            </div>
          </div>

          <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
            <div className="text-xs font-medium text-slate-400 mb-2">Calculation Details</div>
            <div className="text-xs text-slate-300 leading-relaxed">
              {result.explanation}
            </div>
          </div>

          <div className="bg-slate-600 rounded-lg p-3">
            <div className="text-xs text-slate-300">
              <strong>Formula:</strong> BaseLength × EffectiveFactor × StitchFraction × Passes × Seams. 
              For circumferential seams, BaseLength = π × OD.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeldCalculator;