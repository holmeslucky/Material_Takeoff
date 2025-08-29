import React, { useState, useEffect } from 'react';

interface ElbowCalculatorProps {
  onCalculate?: (result: ElbowCalculationResult) => void;
}

interface ElbowCalculationResult {
  totalWeldInches: number;
  totalWeldFeet: number;
  circumference: number;
  explanation: string;
}

interface ElbowRow {
  name: string;
  qty: number;
  gores: number;
  endJoints: number;
  rings: number;
  longPerGore: number;
}

const ElbowCalculator: React.FC<ElbowCalculatorProps> = ({ onCalculate }) => {
  const [od, setOd] = useState(60);
  const [eff, setEff] = useState(1.0);
  const [passes, setPasses] = useState(1);
  const [isStitch, setIsStitch] = useState(false);
  const [stitchLen, setStitchLen] = useState(2);
  const [skipLen, setSkipLen] = useState(2);
  const [roundTo, setRoundTo] = useState(0.01);

  // Elbow configurations
  const [elbowRows, setElbowRows] = useState<ElbowRow[]>([
    { name: "Elbow A", qty: 0, gores: 2, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow B", qty: 0, gores: 5, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow C", qty: 0, gores: 7, endJoints: 2, rings: 0, longPerGore: 0 },
    { name: "Elbow D", qty: 0, gores: 9, endJoints: 2, rings: 0, longPerGore: 0 }
  ]);

  // Straight duct
  const [buttJoints, setButtJoints] = useState(0);
  const [ringsStraight, setRingsStraight] = useState(0);
  const [longLenStraight, setLongLenStraight] = useState(0);

  const [result, setResult] = useState<ElbowCalculationResult>({
    totalWeldInches: 0,
    totalWeldFeet: 0,
    circumference: 0,
    explanation: ''
  });

  const calculateElbow = () => {
    const circumference = Math.PI * od;
    const effectiveFactor = Math.max(0, Math.min(1, eff));
    const numberOfPasses = Math.max(1, Math.floor(passes));

    // Calculate stitch fraction
    let stitchFraction = 1;
    if (isStitch) {
      const denominator = stitchLen + skipLen;
      if (denominator > 0) {
        stitchFraction = stitchLen / denominator;
      }
    }

    let totalCircSeams = 0;
    let totalLongInches = 0;

    // Process each elbow row
    elbowRows.forEach(elbow => {
      const qty = Math.max(0, Math.floor(elbow.qty));
      const gores = Math.max(2, Math.floor(elbow.gores));
      const endJ = Math.max(0, Math.floor(elbow.endJoints));
      const rings = Math.max(0, Math.floor(elbow.rings));
      const longPerGore = Math.max(0, elbow.longPerGore);

      const seamsPerElbow = (gores - 1) + endJ + rings;
      totalCircSeams += seamsPerElbow * qty;
      totalLongInches += (longPerGore * gores) * qty;
    });

    // Add straight duct
    const buttJointsCount = Math.max(0, Math.floor(buttJoints));
    const ringsStraightCount = Math.max(0, Math.floor(ringsStraight));
    const longLenStraightValue = Math.max(0, longLenStraight);

    totalCircSeams += buttJointsCount + ringsStraightCount;
    totalLongInches += longLenStraightValue;

    const totalCircInches = circumference * totalCircSeams;
    const baseInches = totalCircInches + totalLongInches;
    const totalIn = baseInches * stitchFraction * effectiveFactor * numberOfPasses;
    const totalFt = totalIn / 12;

    const explanation = `Circ seams=${totalCircSeams} → ${totalCircInches.toFixed(1)} in; Long seams=${totalLongInches.toFixed(1)} in; Stitch=${stitchFraction.toFixed(2)}; Eff=${effectiveFactor}; Passes=${numberOfPasses}`;

    const newResult = {
      totalWeldInches: Math.round(totalIn / roundTo) * roundTo,
      totalWeldFeet: Math.round(totalFt / roundTo) * roundTo,
      circumference: Math.round(circumference / 0.01) * 0.01,
      explanation
    };

    setResult(newResult);
    
    if (onCalculate) {
      onCalculate(newResult);
    }
  };

  const updateElbowRow = (index: number, field: keyof ElbowRow, value: string | number) => {
    const newRows = [...elbowRows];
    if (field === 'name') {
      newRows[index][field] = value as string;
    } else {
      newRows[index][field] = Number(value) || 0;
    }
    setElbowRows(newRows);
  };

  const addElbowRow = () => {
    setElbowRows([...elbowRows, { 
      name: `Elbow ${String.fromCharCode(65 + elbowRows.length)}`, 
      qty: 0, 
      gores: 5, 
      endJoints: 2, 
      rings: 0, 
      longPerGore: 0 
    }]);
  };

  const removeElbowRow = (index: number) => {
    if (elbowRows.length > 1) {
      const newRows = elbowRows.filter((_, i) => i !== index);
      setElbowRows(newRows);
    }
  };

  const setExample = () => {
    setOd(72);
    setEff(0.95);
    setPasses(2);
    setIsStitch(true);
    setStitchLen(2);
    setSkipLen(2);

    // Reset all elbow rows
    const newRows = [...elbowRows];
    newRows.forEach(row => {
      row.qty = 0;
      row.longPerGore = 0;
      row.rings = 0;
      row.endJoints = 2;
    });
    
    // Set example values
    newRows[1].qty = 2; // 5-gore
    newRows[1].rings = 1;
    newRows[2].qty = 1; // 7-gore
    newRows[2].rings = 0;
    
    setElbowRows(newRows);
    setButtJoints(4);
    setRingsStraight(2);
    setLongLenStraight(0);
  };

  const resetCalculator = () => {
    setOd(60);
    setEff(1.0);
    setPasses(1);
    setIsStitch(false);
    setStitchLen(2);
    setSkipLen(2);
    setRoundTo(0.01);
    setElbowRows([
      { name: "Elbow A", qty: 0, gores: 2, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow B", qty: 0, gores: 5, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow C", qty: 0, gores: 7, endJoints: 2, rings: 0, longPerGore: 0 },
      { name: "Elbow D", qty: 0, gores: 9, endJoints: 2, rings: 0, longPerGore: 0 }
    ]);
    setButtJoints(0);
    setRingsStraight(0);
    setLongLenStraight(0);
  };

  useEffect(() => {
    calculateElbow();
  }, [od, eff, passes, isStitch, stitchLen, skipLen, roundTo, elbowRows, buttJoints, ringsStraight, longLenStraight]);

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-600 rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-slate-100">Duct Elbow Weld Calculator</h3>
        <div className="text-xs text-slate-400">
          For gored elbows with 2 / 5 / 7 / 9 gores
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Global Inputs */}
        <div className="xl:col-span-2 space-y-6">
          <div>
            <h4 className="text-lg font-semibold text-slate-200 mb-3">Global Inputs</h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Outside Diameter (OD, inches)
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
                  Effective Factor (0–1)
                  <span className="text-slate-400 text-xs ml-1">deduct cutouts/gaps</span>
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
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Passes
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
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="elbowStitch"
                  checked={isStitch}
                  onChange={(e) => setIsStitch(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="elbowStitch" className="text-sm font-medium text-slate-300">
                  Stitch Weld
                </label>
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

            {isStitch && (
              <div className="mt-4 bg-slate-700 rounded-lg p-4 grid grid-cols-2 gap-4">
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
            )}
          </div>

          {/* Elbow Components Table */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold text-slate-200">Elbow Components</h4>
              <button
                onClick={addElbowRow}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors"
              >
                Add Row
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-slate-600 text-sm">
                <thead>
                  <tr className="bg-slate-700">
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">Elbow</th>
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">Qty</th>
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">Gores</th>
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">End Joints</th>
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">Rings</th>
                    <th className="border border-slate-600 px-2 py-2 text-left text-slate-200">Long per Gore (in)</th>
                    <th className="border border-slate-600 px-2 py-2 text-center text-slate-200">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {elbowRows.map((row, index) => (
                    <tr key={index} className="bg-slate-800">
                      <td className="border border-slate-600 px-2 py-1">
                        <input
                          type="text"
                          value={row.name}
                          onChange={(e) => updateElbowRow(index, 'name', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        />
                      </td>
                      <td className="border border-slate-600 px-2 py-1">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={row.qty}
                          onChange={(e) => updateElbowRow(index, 'qty', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        />
                      </td>
                      <td className="border border-slate-600 px-2 py-1">
                        <select
                          value={row.gores}
                          onChange={(e) => updateElbowRow(index, 'gores', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        >
                          <option value={2}>2</option>
                          <option value={5}>5</option>
                          <option value={7}>7</option>
                          <option value={9}>9</option>
                        </select>
                      </td>
                      <td className="border border-slate-600 px-2 py-1">
                        <input
                          type="number"
                          min="0"
                          max="2"
                          step="1"
                          value={row.endJoints}
                          onChange={(e) => updateElbowRow(index, 'endJoints', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        />
                      </td>
                      <td className="border border-slate-600 px-2 py-1">
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={row.rings}
                          onChange={(e) => updateElbowRow(index, 'rings', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        />
                      </td>
                      <td className="border border-slate-600 px-2 py-1">
                        <input
                          type="number"
                          min="0"
                          step="0.001"
                          value={row.longPerGore}
                          onChange={(e) => updateElbowRow(index, 'longPerGore', e.target.value)}
                          className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-xs"
                        />
                      </td>
                      <td className="border border-slate-600 px-2 py-1 text-center">
                        {elbowRows.length > 1 && (
                          <button
                            onClick={() => removeElbowRow(index)}
                            className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs transition-colors"
                          >
                            ×
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Straight Duct Section */}
          <div>
            <h4 className="text-lg font-semibold text-slate-200 mb-3">Straight Duct (Optional)</h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Butt joints (duct-to-duct)
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={buttJoints}
                  onChange={(e) => setButtJoints(Number(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Rings (count)
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={ringsStraight}
                  onChange={(e) => setRingsStraight(Number(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Longitudinal seam length (in)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={longLenStraight}
                  onChange={(e) => setLongLenStraight(Number(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 text-sm"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={calculateElbow}
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
          
          <div className="grid grid-cols-1 gap-4">
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Weld Inches (total)</div>
              <div className="text-lg font-bold text-slate-100">{result.totalWeldInches.toFixed(2)}</div>
            </div>
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Weld Feet (total)</div>
              <div className="text-lg font-bold text-slate-100">{result.totalWeldFeet.toFixed(2)}</div>
            </div>
            <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
              <div className="text-xs font-medium text-slate-400 mb-1">Circumference</div>
              <div className="text-lg font-bold text-slate-100">{result.circumference.toFixed(2)} in</div>
            </div>
          </div>

          <div className="bg-slate-700 border border-slate-600 rounded-lg p-4">
            <div className="text-xs font-medium text-slate-400 mb-2">Calculation Details</div>
            <div className="text-xs text-slate-300 leading-relaxed">
              {result.explanation}
            </div>
          </div>

          <div className="bg-slate-600 rounded-lg p-3 space-y-2">
            <div className="text-xs text-slate-300">
              <strong>Notes:</strong>
            </div>
            <ul className="text-xs text-slate-300 space-y-1 ml-2">
              <li>• Each gored elbow with <strong>G</strong> gores has <strong>G − 1</strong> circumferential joints between gores</li>
              <li>• Add <strong>0–2</strong> end joints per elbow depending on connections</li>
              <li>• Rings add one circumferential weld each</li>
              <li>• Longitudinal seams are optional</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ElbowCalculator;