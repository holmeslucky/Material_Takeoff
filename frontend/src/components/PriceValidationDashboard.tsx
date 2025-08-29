import React, { useState, useEffect } from 'react'
import { AlertCircle, Flag, DollarSign, TrendingUp, Check, X } from 'lucide-react'
import { buildApiUrl } from '../config/api'

interface ValidationDashboardData {
  summary: {
    total_materials: number
    flagged_count: number
    needs_validation_count: number
    confidence_breakdown: {
      high: number
      medium: number
      low: number
      missing: number
    }
  }
  recent_flags: Array<{
    id: number
    shape_key: string
    flagged_by: string
    reason: string
    flagged_date: string
    current_price: number
  }>
  high_variance_materials: Array<{
    id: number
    shape_key: string
    variance_percent: number
    current_price: number
    confidence: string
  }>
}

export default function PriceValidationDashboard() {
  const [dashboardData, setDashboardData] = useState<ValidationDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${buildApiUrl('/api/v1/materials/validation/dashboard')}`)
      if (!response.ok) throw new Error('Failed to load dashboard')
      const data = await response.json()
      setDashboardData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  if (isLoading) {
    return (
      <div className="p-6 bg-gray-900 rounded-lg">
        <div className="animate-pulse text-gray-400">Loading price validation data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900 rounded-lg border border-red-700">
        <div className="flex items-center gap-2 text-red-300">
          <AlertCircle className="w-5 h-5" />
          Error loading dashboard: {error}
        </div>
      </div>
    )
  }

  if (!dashboardData) return null

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center gap-3">
            <DollarSign className="w-8 h-8 text-blue-400" />
            <div>
              <div className="text-2xl font-bold text-white">{dashboardData.summary.total_materials}</div>
              <div className="text-sm text-gray-400">Total Materials</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center gap-3">
            <Flag className="w-8 h-8 text-red-400" />
            <div>
              <div className="text-2xl font-bold text-red-300">{dashboardData.summary.flagged_count}</div>
              <div className="text-sm text-gray-400">Flagged Prices</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-8 h-8 text-yellow-400" />
            <div>
              <div className="text-2xl font-bold text-yellow-300">{dashboardData.summary.needs_validation_count}</div>
              <div className="text-sm text-gray-400">Need Validation</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-green-400" />
            <div>
              <div className="text-2xl font-bold text-green-300">{dashboardData.summary.confidence_breakdown.high}</div>
              <div className="text-sm text-gray-400">High Confidence</div>
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Breakdown */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-4">Price Confidence Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{dashboardData.summary.confidence_breakdown.high}</div>
            <div className="text-sm text-gray-400">High</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{dashboardData.summary.confidence_breakdown.medium}</div>
            <div className="text-sm text-gray-400">Medium</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-400">{dashboardData.summary.confidence_breakdown.low}</div>
            <div className="text-sm text-gray-400">Low</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-400">{dashboardData.summary.confidence_breakdown.missing}</div>
            <div className="text-sm text-gray-400">Missing</div>
          </div>
        </div>
      </div>

      {/* Recent Flags */}
      {dashboardData.recent_flags.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">Recently Flagged Materials</h3>
          <div className="space-y-3">
            {dashboardData.recent_flags.map((flag) => (
              <div key={flag.id} className="flex items-center justify-between bg-gray-700 p-3 rounded-lg">
                <div className="flex items-center gap-3">
                  <Flag className="w-5 h-5 text-red-400" />
                  <div>
                    <div className="text-white font-medium">{flag.shape_key}</div>
                    <div className="text-sm text-gray-400">
                      Flagged by {flag.flagged_by}: {flag.reason}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg text-green-400">${flag.current_price?.toFixed(2)}</div>
                  <div className="text-xs text-gray-400">{new Date(flag.flagged_date).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* High Variance Materials */}
      {dashboardData.high_variance_materials.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">High Price Variance Materials</h3>
          <div className="space-y-3">
            {dashboardData.high_variance_materials.map((material) => (
              <div key={material.id} className="flex items-center justify-between bg-gray-700 p-3 rounded-lg">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-yellow-400" />
                  <div>
                    <div className="text-white font-medium">{material.shape_key}</div>
                    <div className="text-sm text-gray-400">
                      {material.variance_percent > 0 ? '+' : ''}{material.variance_percent.toFixed(1)}% variance
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg text-green-400">${material.current_price?.toFixed(2)}</div>
                  <div className={`text-xs px-2 py-1 rounded ${
                    material.confidence === 'HIGH' ? 'bg-green-900 text-green-300' :
                    material.confidence === 'MEDIUM' ? 'bg-yellow-900 text-yellow-300' :
                    material.confidence === 'LOW' ? 'bg-orange-900 text-orange-300' :
                    'bg-gray-900 text-gray-300'
                  }`}>
                    {material.confidence}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}