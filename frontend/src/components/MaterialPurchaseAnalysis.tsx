import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  TrendingDown,
  Package, 
  Truck, 
  Calendar,
  DollarSign, 
  BarChart3,
  PieChart,
  AlertTriangle,
  CheckCircle,
  Clock,
  Layers,
  ShoppingBag
} from 'lucide-react'

interface MaterialPurchase {
  shape_key: string
  size_description: string
  pieces_needed: number
  total_cost: number
  waste_percentage: number
  waste_cost: number
  cuts_count: number
}

interface PurchaseAnalysis {
  project_id: string
  total_purchases: number
  total_cost: number
  total_waste_cost: number
  average_waste_percentage: number
  high_waste_items: MaterialPurchase[]
  efficient_purchases: MaterialPurchase[]
  cost_breakdown: {
    materials: number
    waste: number
    labor: number
  }
  supplier_recommendations: {
    name: string
    cost_savings: number
    delivery_time: string
    reliability_score: number
  }[]
  purchase_timeline: {
    critical_path: string[]
    lead_times: { [key: string]: number }
    recommended_order_date: string
  }
}

interface MaterialPurchaseAnalysisProps {
  projectId: string
  optimizationData?: any
}

export default function MaterialPurchaseAnalysis({ 
  projectId, 
  optimizationData 
}: MaterialPurchaseAnalysisProps) {
  const [analysis, setAnalysis] = useState<PurchaseAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'breakdown' | 'suppliers' | 'timeline'>('overview')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (optimizationData) {
      generatePurchaseAnalysis()
    }
  }, [optimizationData, projectId])

  const generatePurchaseAnalysis = async () => {
    setLoading(true)
    setError(null)

    try {
      // Simulate analysis generation (in real implementation, this would call backend API)
      const mockAnalysis: PurchaseAnalysis = {
        project_id: projectId,
        total_purchases: optimizationData?.material_purchases?.length || 0,
        total_cost: optimizationData?.total_cost || 0,
        total_waste_cost: optimizationData?.material_purchases?.reduce((sum: number, p: MaterialPurchase) => sum + p.waste_cost, 0) || 0,
        average_waste_percentage: optimizationData?.total_waste_percentage || 0,
        high_waste_items: optimizationData?.material_purchases?.filter((p: MaterialPurchase) => p.waste_percentage > 25) || [],
        efficient_purchases: optimizationData?.material_purchases?.filter((p: MaterialPurchase) => p.waste_percentage <= 15) || [],
        cost_breakdown: {
          materials: (optimizationData?.total_cost || 0) * 0.8,
          waste: (optimizationData?.total_cost || 0) * 0.15,
          labor: (optimizationData?.total_cost || 0) * 0.05
        },
        supplier_recommendations: [
          { name: "Steel Warehouse", cost_savings: 1250, delivery_time: "3-5 days", reliability_score: 95 },
          { name: "Industrial Metals", cost_savings: 890, delivery_time: "2-4 days", reliability_score: 88 },
          { name: "Capitol Steel", cost_savings: 650, delivery_time: "1-3 days", reliability_score: 92 }
        ],
        purchase_timeline: {
          critical_path: ["Order plates", "Order structural steel", "Coordinate delivery"],
          lead_times: { "Plates": 5, "Beams": 3, "Angles": 2 },
          recommended_order_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        }
      }

      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
      setAnalysis(mockAnalysis)
    } catch (error) {
      console.error('Error generating purchase analysis:', error)
      setError('Failed to generate purchase analysis')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-300">Analyzing purchase requirements...</p>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <ShoppingBag className="w-16 h-16 text-gray-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-300 mb-2">
          Purchase Analysis Ready
        </h3>
        <p className="text-gray-500 mb-6">
          Run material optimization to get detailed purchase analysis and supplier recommendations.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Tabs */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-green-400" />
          Purchase Analysis
        </h2>
        
        <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
          {(['overview', 'breakdown', 'suppliers', 'timeline'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm rounded-md capitalize transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-900 rounded-lg">
                <Package className="w-6 h-6 text-blue-400" />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">{analysis.total_purchases}</div>
                <div className="text-sm text-gray-400">Purchase Orders</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-900 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-400" />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">{formatCurrency(analysis.total_cost)}</div>
                <div className="text-sm text-gray-400">Total Cost</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-900 rounded-lg">
                <TrendingDown className="w-6 h-6 text-red-400" />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-red-400">{analysis.average_waste_percentage.toFixed(1)}%</div>
                <div className="text-sm text-gray-400">Avg Waste</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-900 rounded-lg">
                <Truck className="w-6 h-6 text-purple-400" />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">{analysis.supplier_recommendations.length}</div>
                <div className="text-sm text-gray-400">Suppliers</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Breakdown Tab */}
      {activeTab === 'breakdown' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Cost Breakdown */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-blue-400" />
              Cost Breakdown
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-blue-500 rounded"></div>
                  <span className="text-gray-300">Materials</span>
                </div>
                <span className="text-white font-medium">{formatCurrency(analysis.cost_breakdown.materials)}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span className="text-gray-300">Waste</span>
                </div>
                <span className="text-white font-medium">{formatCurrency(analysis.cost_breakdown.waste)}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-gray-300">Labor</span>
                </div>
                <span className="text-white font-medium">{formatCurrency(analysis.cost_breakdown.labor)}</span>
              </div>
            </div>
          </div>

          {/* Efficiency Analysis */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              Efficiency Analysis
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">High Efficiency Items</span>
                <span className="text-green-400 font-medium">{analysis.efficient_purchases.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">High Waste Items</span>
                <span className="text-red-400 font-medium">{analysis.high_waste_items.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Total Waste Cost</span>
                <span className="text-red-400 font-medium">{formatCurrency(analysis.total_waste_cost)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Suppliers Tab */}
      {activeTab === 'suppliers' && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-6">
            Supplier Recommendations
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Supplier</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-medium">Cost Savings</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-medium">Delivery</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-medium">Reliability</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {analysis.supplier_recommendations.map((supplier, index) => (
                  <tr key={supplier.name} className="border-b border-gray-700 hover:bg-gray-750">
                    <td className="py-3 px-4 text-white font-medium">{supplier.name}</td>
                    <td className="py-3 px-4 text-center text-green-400">
                      {formatCurrency(supplier.cost_savings)}
                    </td>
                    <td className="py-3 px-4 text-center text-gray-300">{supplier.delivery_time}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`${supplier.reliability_score >= 90 ? 'text-green-400' : 'text-yellow-400'}`}>
                        {supplier.reliability_score}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {index === 0 ? (
                        <span className="bg-green-900 text-green-200 px-2 py-1 rounded text-sm">
                          Recommended
                        </span>
                      ) : (
                        <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-sm">
                          Alternative
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Timeline Tab */}
      {activeTab === 'timeline' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Critical Path */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-orange-400" />
              Critical Path
            </h3>
            <div className="space-y-3">
              {analysis.purchase_timeline.critical_path.map((step, index) => (
                <div key={step} className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {index + 1}
                  </div>
                  <span className="text-gray-300">{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Lead Times */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-400" />
              Lead Times
            </h3>
            <div className="space-y-4">
              {Object.entries(analysis.purchase_timeline.lead_times).map(([material, days]) => (
                <div key={material} className="flex items-center justify-between">
                  <span className="text-gray-300">{material}</span>
                  <span className="text-white font-medium">{days} days</span>
                </div>
              ))}
              <div className="border-t border-gray-700 pt-4 mt-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 font-medium">Recommended Order Date</span>
                  <span className="text-blue-400 font-medium">
                    {new Date(analysis.purchase_timeline.recommended_order_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}