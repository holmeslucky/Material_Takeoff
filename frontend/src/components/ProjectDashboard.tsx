import React, { useState, useEffect } from 'react'
import { TrendingUp, DollarSign, Scale, Clock, Calculator, FileText } from 'lucide-react'

interface ProjectDashboardProps {
  projectId: string
}

interface ProjectStats {
  total_entries: number
  total_weight_tons: number
  total_material_cost: number
  total_labor_hours: number
  total_labor_cost: number
  total_project_cost: number
  by_category: Record<string, any>
}

export default function ProjectDashboard({ projectId }: ProjectDashboardProps) {
  const [stats, setStats] = useState<ProjectStats | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchProjectStats = async () => {
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/summary`)
      if (response.ok) {
        const data = await response.json()
        setStats(data.totals)
      }
    } catch (error) {
      console.error('Failed to fetch project stats:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjectStats()
    // Refresh stats every 30 seconds for real-time updates
    const interval = setInterval(fetchProjectStats, 30000)
    return () => clearInterval(interval)
  }, [projectId])

  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded mb-4"></div>
          <div className="grid grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

  const StatCard = ({ icon: Icon, title, value, subtitle, color = 'blue' }: any) => (
    <div className={`bg-gray-800 border border-gray-700 rounded-lg p-4`}>
      <div className="flex items-center justify-between mb-2">
        <div className={`p-2 rounded-lg bg-${color}-900/30`}>
          <Icon className={`w-5 h-5 text-${color}-400`} />
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold text-${color}-400`}>{value}</div>
          <div className="text-xs text-gray-500">{title}</div>
        </div>
      </div>
      {subtitle && (
        <div className="text-xs text-gray-400 mt-1">{subtitle}</div>
      )}
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">Project Dashboard</h2>
          <div className="ml-auto">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              Real-time updates
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard
          icon={FileText}
          title="Total Entries"
          value={stats?.total_entries || 0}
          subtitle="Takeoff line items"
          color="blue"
        />

        <StatCard
          icon={Scale}
          title="Total Weight"
          value={`${(stats?.total_weight_tons || 0).toFixed(2)} tons`}
          subtitle="Steel weight"
          color="purple"
        />

        <StatCard
          icon={DollarSign}
          title="Material Cost"
          value={formatCurrency(stats?.total_material_cost || 0)}
          subtitle="Steel & materials"
          color="green"
        />

        <StatCard
          icon={Clock}
          title="Labor Hours"
          value={`${(stats?.total_labor_hours || 0).toFixed(1)} hrs`}
          subtitle="Shop fabrication"
          color="yellow"
        />

        <StatCard
          icon={Calculator}
          title="Labor Cost"
          value={formatCurrency(stats?.total_labor_cost || 0)}
          subtitle="@ $120/hr + markup"
          color="yellow"
        />

        <StatCard
          icon={TrendingUp}
          title="Total Project"
          value={formatCurrency(stats?.total_project_cost || 0)}
          subtitle="Materials + labor"
          color="blue"
        />
      </div>

      {/* Cost Breakdown Chart */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Cost Breakdown</h3>
        
        {stats && (
          <div className="space-y-4">
            {/* Progress bars */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">Material Cost</span>
                  <span className="text-green-400">{formatCurrency(stats.total_material_cost)}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{
                      width: `${(stats.total_material_cost / stats.total_project_cost) * 100}%`
                    }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">Labor Cost</span>
                  <span className="text-yellow-400">{formatCurrency(stats.total_labor_cost)}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-yellow-500 h-2 rounded-full" 
                    style={{
                      width: `${(stats.total_labor_cost / stats.total_project_cost) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Summary row */}
            <div className="border-t border-gray-700 pt-3">
              <div className="flex justify-between items-center">
                <span className="text-white font-semibold">Project Total:</span>
                <span className="text-2xl font-bold text-blue-400">
                  {formatCurrency(stats.total_project_cost)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Project Efficiency</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Labor vs Material Ratio:</span>
              <span className="text-white">
                {stats ? ((stats.total_labor_cost / stats.total_material_cost) * 100).toFixed(1) : 0}%
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-400">Cost per Ton:</span>
              <span className="text-white">
                {stats && stats.total_weight_tons > 0 
                  ? formatCurrency(stats.total_project_cost / stats.total_weight_tons)
                  : '$0.00'
                }
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-400">Hours per Ton:</span>
              <span className="text-white">
                {stats && stats.total_weight_tons > 0 
                  ? (stats.total_labor_hours / stats.total_weight_tons).toFixed(1)
                  : '0.0'
                } hrs/ton
              </span>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Project Status</h3>
          
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-gray-300">Active Project</span>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
              <span className="text-gray-300">Real-time Calculations</span>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <span className="text-gray-300">Shop Fabrication Only</span>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
              <span className="text-gray-300">Labor Rate: $120/hr</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}