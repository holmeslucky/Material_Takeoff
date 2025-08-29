import React, { useState } from 'react'
import { Calculator, ArrowLeft, Settings, Info } from 'lucide-react'
import { Link } from 'react-router-dom'
import CalculatorPanel from '../components/CalculatorPanel'

export default function CalculatorDemo() {
  const [selectedTemplate, setSelectedTemplate] = useState<'Main Takeoff' | 'Ductwork Takeoff' | 'Pipe Takeoff'>('Ductwork Takeoff')
  const [weldResults, setWeldResults] = useState<any>(null)

  const handleWeldInchesUpdate = (calculatorType: string, totalWeldInches: number, totalWeldFeet: number, results: any) => {
    setWeldResults({
      calculatorType,
      totalWeldInches,
      totalWeldFeet,
      results
    })
    console.log('Weld calculation updated:', { calculatorType, totalWeldInches, totalWeldFeet, results })
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center gap-4">
          <Link
            to="/projects"
            className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Calculator className="w-7 h-7 text-blue-400" />
              Weld Calculator Demo
            </h1>
            <p className="text-gray-400">
              Demonstration of integrated weld calculators for different template types
            </p>
          </div>
          
          {/* Template Selector */}
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-300">Template Type:</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value as any)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Main Takeoff">Main Takeoff</option>
              <option value="Ductwork Takeoff">Ductwork Takeoff</option>
              <option value="Pipe Takeoff">Pipe Takeoff</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-6">
          {/* Template Information */}
          <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className={`p-4 rounded-lg border-2 transition-all ${
              selectedTemplate === 'Main Takeoff' 
                ? 'bg-green-900/20 border-green-600' 
                : 'bg-gray-800 border-gray-700'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Settings className="w-5 h-5 text-green-400" />
                <h3 className="font-medium text-white">Main Takeoff</h3>
              </div>
              <p className="text-sm text-gray-400">
                Structural steel, plates, angles, and miscellaneous items. 
                Focus on material quantities and manual labor entry.
              </p>
            </div>

            <div className={`p-4 rounded-lg border-2 transition-all ${
              selectedTemplate === 'Ductwork Takeoff' 
                ? 'bg-orange-900/20 border-orange-600' 
                : 'bg-gray-800 border-gray-700'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Calculator className="w-5 h-5 text-orange-400" />
                <h3 className="font-medium text-white">Ductwork Takeoff</h3>
              </div>
              <p className="text-sm text-gray-400">
                Includes Main functionality plus weld calculators for circumferential 
                seams and gored elbows (2/5/7/9 gores).
              </p>
            </div>

            <div className={`p-4 rounded-lg border-2 transition-all ${
              selectedTemplate === 'Pipe Takeoff' 
                ? 'bg-purple-900/20 border-purple-600' 
                : 'bg-gray-800 border-gray-700'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Calculator className="w-5 h-5 text-purple-400" />
                <h3 className="font-medium text-white">Pipe Takeoff</h3>
              </div>
              <p className="text-sm text-gray-400">
                Includes Main functionality plus pipe calculators with NPS sizing, 
                standard fittings, and butt/fillet weld calculations.
              </p>
            </div>
          </div>

          {/* Results Summary */}
          {weldResults && (
            <div className="mb-6 bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <Info className="w-5 h-5 text-blue-400" />
                <h3 className="font-medium text-white">Live Calculation Results</h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Total Weld Inches</div>
                  <div className="text-xl font-bold text-blue-400">{weldResults.totalWeldInches.toFixed(2)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Total Weld Feet</div>
                  <div className="text-xl font-bold text-blue-400">{weldResults.totalWeldFeet.toFixed(2)}</div>
                </div>
              </div>
              <div className="mt-3 text-sm text-gray-400">
                Calculator: <span className="text-white font-medium">{weldResults.calculatorType}</span>
              </div>
            </div>
          )}

          {/* Calculator Panel */}
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <Calculator className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-semibold text-white">
                Available Calculators for {selectedTemplate}
              </h2>
            </div>

            <CalculatorPanel 
              templateCategory={selectedTemplate}
              onWeldInchesUpdate={handleWeldInchesUpdate}
            />
          </div>

          {/* Integration Instructions */}
          <div className="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Integration Overview</h3>
            <div className="space-y-4 text-sm text-gray-300">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-white mb-2">How It Works</h4>
                  <ul className="space-y-1 text-gray-400">
                    <li>• Each template type shows relevant calculators</li>
                    <li>• Calculators automatically update weld inch totals</li>
                    <li>• Results can be integrated into takeoff calculations</li>
                    <li>• Manual labor entry remains primary input method</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-white mb-2">Template Benefits</h4>
                  <ul className="space-y-1 text-gray-400">
                    <li>• <strong>Main:</strong> Clean, focused on structural items</li>
                    <li>• <strong>Ductwork:</strong> Specialized for duct fabrication</li>
                    <li>• <strong>Pipe:</strong> Standard pipe sizing and fittings</li>
                    <li>• All templates support manual labor with checkboxes</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}