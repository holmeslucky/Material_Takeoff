import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Package, 
  Scissors, 
  DollarSign, 
  AlertCircle, 
  CheckCircle,
  Loader,
  BarChart3,
  ShoppingCart,
  Zap,
  FileBarChart
} from 'lucide-react'
import MaterialPurchaseAnalysis from './MaterialPurchaseAnalysis'

interface MaterialPurchase {
  shape_key: string
  size_description: string
  pieces_needed: number
  total_cost: number
  waste_percentage: number
  waste_cost: number
  cuts_count: number
}

interface OptimizationResult {
  project_id: string
  material_purchases: MaterialPurchase[]
  total_waste_percentage: number
  total_cost: number
  cost_savings: number
  optimization_summary: string
  recommendations: string[]
}

interface WasteAnalysis {
  project_id: string
  current_material_cost: number
  optimized_material_cost: number
  potential_savings: number
  savings_percentage: number
  total_waste_percentage: number
  optimization_feasible: boolean
}

interface MaterialOptimizationDashboardProps {
  projectId: string
  onOptimizationComplete?: (result: OptimizationResult) => void
}

export default function MaterialOptimizationDashboard({ 
  projectId, 
  onOptimizationComplete 
}: MaterialOptimizationDashboardProps) {
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null)
  const [wasteAnalysis, setWasteAnalysis] = useState<WasteAnalysis | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'optimization' | 'analysis'>('optimization')

  // Load waste analysis on mount
  useEffect(() => {
    if (projectId) {
      loadWasteAnalysis()
    }
  }, [projectId])

  const loadWasteAnalysis = async () => {
    setIsAnalyzing(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/nesting/waste-analysis/${projectId}`)
      if (response.ok) {
        const analysis = await response.json()
        setWasteAnalysis(analysis)
      } else {
        throw new Error('Failed to load waste analysis')
      }
    } catch (error) {
      console.error('Error loading waste analysis:', error)
      setError('Failed to analyze current material usage')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const runOptimization = async () => {
    setIsOptimizing(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/nesting/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          include_waste_costs: true,
          optimization_level: 'standard'
        }),
      })

      if (response.ok) {
        const result = await response.json()
        setOptimizationResult(result)
        if (onOptimizationComplete) {
          onOptimizationComplete(result)
        }
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Optimization failed')
      }
    } catch (error) {
      console.error('Error running optimization:', error)
      setError(error instanceof Error ? error.message : 'Failed to optimize materials')
    } finally {
      setIsOptimizing(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <Package className="w-8 h-8 text-blue-400" />
          Material Optimization
        </h2>
        
        <div className="flex items-center gap-4">
          {/* View Toggle */}
          <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveView('optimization')}
              className={`px-3 py-2 text-sm rounded-md transition-colors ${
                activeView === 'optimization'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <Package className="w-4 h-4 inline mr-1" />
              Optimization
            </button>
            <button
              onClick={() => setActiveView('analysis')}
              className={`px-3 py-2 text-sm rounded-md transition-colors ${
                activeView === 'analysis'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <FileBarChart className="w-4 h-4 inline mr-1" />
              Analysis
            </button>
          </div>
          
          <button
            onClick={runOptimization}
            disabled={isOptimizing}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-lg transition-colors"
          >
            {isOptimizing ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Zap className="w-5 h-5" />
            )}
            {isOptimizing ? 'Optimizing...' : 'Run Optimization'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 border border-red-700 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-200">{error}</span>
        </div>
      )}

      {/* Content based on active view */}
      {activeView === 'analysis' ? (
        <MaterialPurchaseAnalysis 
          projectId={projectId}
          optimizationData={optimizationResult}
        />
      ) : (
        <>
          {/* Waste Analysis Card */}
          {wasteAnalysis && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-yellow-400" />
                Current Material Analysis
              </h3>
              
              {isAnalyzing ? (
                <div className="flex items-center justify-center py-8">
                  <Loader className="w-6 h-6 animate-spin text-gray-400" />
                  <span className="ml-3 text-gray-400">Analyzing materials...</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-sm text-gray-400">Current Cost</div>
                    <div className="text-2xl font-bold text-white">
                      {formatCurrency(wasteAnalysis.current_material_cost)}
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-sm text-gray-400">Optimized Cost</div>
                    <div className="text-2xl font-bold text-green-400">
                      {formatCurrency(wasteAnalysis.optimized_material_cost)}
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-sm text-gray-400">Potential Savings</div>
                    <div className="text-2xl font-bold text-blue-400">
                      {formatCurrency(wasteAnalysis.potential_savings)}
                      <span className="text-sm text-gray-400 ml-2">
                        ({wasteAnalysis.savings_percentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Optimization Results */}
          {optimizationResult && (
            <div className="space-y-6">
              {/* Results Summary */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  Optimization Results
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <DollarSign className="w-6 h-6 text-green-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-400">Total Cost</div>
                    <div className="text-xl font-bold text-white">
                      {formatCurrency(optimizationResult.total_cost)}
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <Scissors className="w-6 h-6 text-red-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-400">Waste</div>
                    <div className="text-xl font-bold text-red-400">
                      {optimizationResult.total_waste_percentage.toFixed(1)}%
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <TrendingUp className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-400">Savings</div>
                    <div className="text-xl font-bold text-blue-400">
                      {formatCurrency(optimizationResult.cost_savings)}
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <ShoppingCart className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                    <div className="text-sm text-gray-400">Purchases</div>
                    <div className="text-xl font-bold text-white">
                      {optimizationResult.material_purchases.length}
                    </div>
                  </div>
                </div>

                {/* Optimization Summary */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="font-semibold text-white mb-2">Optimization Summary</h4>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                    {optimizationResult.optimization_summary}
                  </pre>
                </div>
              </div>

              {/* Material Purchases */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Material Purchase Recommendations
                </h3>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-3 px-4 text-gray-300 font-medium">Material</th>
                        <th className="text-left py-3 px-4 text-gray-300 font-medium">Size</th>
                        <th className="text-center py-3 px-4 text-gray-300 font-medium">Pieces</th>
                        <th className="text-center py-3 px-4 text-gray-300 font-medium">Cuts</th>
                        <th className="text-right py-3 px-4 text-gray-300 font-medium">Waste</th>
                        <th className="text-right py-3 px-4 text-gray-300 font-medium">Cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      {optimizationResult.material_purchases.map((purchase, index) => (
                        <tr key={index} className="border-b border-gray-700 hover:bg-gray-750">
                          <td className="py-3 px-4 text-white font-medium">{purchase.shape_key}</td>
                          <td className="py-3 px-4 text-gray-300">{purchase.size_description}</td>
                          <td className="py-3 px-4 text-center text-white">{purchase.pieces_needed}</td>
                          <td className="py-3 px-4 text-center text-gray-300">{purchase.cuts_count}</td>
                          <td className="py-3 px-4 text-right">
                            <span className={`${purchase.waste_percentage > 25 ? 'text-red-400' : 'text-yellow-400'}`}>
                              {purchase.waste_percentage.toFixed(1)}%
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right text-white font-medium">
                            {formatCurrency(purchase.total_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Recommendations */}
              {optimizationResult.recommendations.length > 0 && (
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-xl font-semibold text-white mb-4">
                    Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {optimizationResult.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-start gap-3 text-gray-300">
                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                        {recommendation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Empty State */}
          {!optimizationResult && !isOptimizing && (
            <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
              <Package className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-300 mb-2">
                Ready to Optimize Materials
              </h3>
              <p className="text-gray-500 mb-6">
                Run optimization to get purchase recommendations and minimize waste costs.
              </p>
              <button
                onClick={runOptimization}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg transition-colors"
              >
                Start Optimization
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}