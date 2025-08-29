import React, { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Download, FileText, Building, Loader2, Package } from 'lucide-react'
import TakeoffGrid from '../components/TakeoffGrid'
import CEProposal from '../components/CEProposal'
import { buildApiUrl, API_ENDPOINTS } from '../config/api'

interface Project {
  id: string
  name: string
  client: string
  location: string | null
  description: string | null
  status: string
  quote_number: string | null
  estimator: string | null
  project_date: string | null
  created_at: string
  updated_at: string | null
  total_entries: number
  total_weight_tons: number
  total_value: number
}

export default function ProjectView() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const laborMode = 'manual' // Fixed to manual only
  const [activeTab, setActiveTab] = useState<'takeoff' | 'proposal'>('takeoff')
  const [projectTotals, setProjectTotals] = useState({
    total_weight_tons: 0,
    total_price: 0,
    total_length_ft: 0,
    total_labor_hours: 0,
    total_labor_cost: 0,
  })
  const [saveFunction, setSaveFunction] = useState<(() => Promise<void>) | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  // Real project data from API
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load project data from API
  useEffect(() => {
    const loadProject = async () => {
      if (!id) {
        setError('No project ID provided')
        setLoading(false)
        return
      }

      try {
        const response = await fetch(buildApiUrl(`${API_ENDPOINTS.PROJECTS}/${id}`))
        if (!response.ok) {
          if (response.status === 404) {
            setError('Project not found')
          } else {
            setError('Failed to load project')
          }
          setLoading(false)
          return
        }

        const projectData = await response.json()
        setProject(projectData)
        setError(null)
      } catch (err) {
        console.error('Error loading project:', err)
        setError('Failed to load project')
      } finally {
        setLoading(false)
      }
    }

    loadProject()
  }, [id])

  const handleTotalsChange = (totals: any) => {
    setProjectTotals(totals)
  }

  const handleSaveProject = async () => {
    if (saveFunction && activeTab === 'takeoff') {
      setIsSaving(true)
      try {
        await saveFunction()
        setLastSaved(new Date())
      } catch (error) {
        console.error('Save failed:', error)
      } finally {
        setIsSaving(false)
      }
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="h-full flex flex-col bg-gray-950">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-300">Loading project...</p>
          </div>
        </div>
      </div>
    )
  }

  // Show error state
  if (error || !project) {
    return (
      <div className="h-full flex flex-col bg-gray-950">
        <div className="bg-gray-900 border-b border-gray-800 p-4">
          <div className="flex items-center gap-4">
            <Link
              to="/projects"
              className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">Project Not Found</h1>
              <p className="text-gray-400">Unable to load project details</p>
            </div>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-400 text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-white mb-2">
              {error || 'Project not found'}
            </h2>
            <p className="text-gray-400 mb-6">
              The project you're looking for doesn't exist or couldn't be loaded.
            </p>
            <Link
              to="/projects"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Back to Projects
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/projects"
              className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">{project.name}</h1>
              <p className="text-gray-400">
                {project.client}
                {project.location && ` • ${project.location}`}
                {project.quote_number && ` • Quote: ${project.quote_number}`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Tab Navigation */}
            <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('takeoff')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  activeTab === 'takeoff'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Takeoff
              </button>
              <button
                onClick={() => setActiveTab('proposal')}
                className={`flex items-center gap-1 px-3 py-1 text-sm rounded-md transition-colors ${
                  activeTab === 'proposal'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <Building className="w-3 h-3" />
                CE Proposal
              </button>
            </div>

            {/* Manual Labor Only - Auto labor removed */}

            <button 
              onClick={handleSaveProject}
              disabled={isSaving || activeTab !== 'takeoff'}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              title={lastSaved ? `Last saved: ${lastSaved.toLocaleTimeString()}` : 'Save project'}
            >
              {isSaving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="w-4 h-4" />
              )}
              {isSaving ? 'Saving...' : 'Save'}
            </button>
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === 'takeoff' ? (
          /* Takeoff Grid */
          <div className="flex-1 p-4">
            <TakeoffGrid 
              projectId={project.id}
              laborMode={laborMode}
              onTotalsChange={handleTotalsChange}
              onSaveFunctionReady={setSaveFunction}
            />
          </div>
        ) : (
          /* CE Proposal System */
          <div className="flex-1 overflow-hidden">
            <CEProposal
              projectId={project.id}
              projectName={project.name}
              onProposalGenerated={(proposal) => {
                console.log('Proposal generated:', proposal)
              }}
            />
          </div>
        )}

        {/* Calculations Panel - Only show on takeoff tab */}
        {activeTab === 'takeoff' && (
          <div className="w-80 calculations-panel m-4">
            <h3 className="text-lg font-semibold text-white mb-4">Project Totals</h3>
            
            <div className="space-y-4">
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Weight Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Length:</span>
                  <span className="text-white">{projectTotals.total_length_ft.toFixed(1)} ft</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Weight:</span>
                  <span className="text-white font-semibold">{projectTotals.total_weight_tons.toFixed(2)} tons</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Cost Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Material Cost:</span>
                  <span className="text-green-400">${projectTotals.total_price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Labor (Manual):</span>
                  <span className="text-yellow-400">${projectTotals.total_labor_cost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between border-t border-gray-600 pt-2">
                  <span className="text-white font-semibold">Total:</span>
                  <span className="text-green-400 font-semibold">
                    ${(projectTotals.total_price + projectTotals.total_labor_cost).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Labor Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Labor Hours:</span>
                  <span className="text-white">{projectTotals.total_labor_hours.toFixed(1)} hrs</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Labor Mode:</span>
                  <span className="text-blue-400 capitalize">Manual Only</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  Manual labor entry with checkboxes enabled
                </p>
              </div>
            </div>

              <button 
                onClick={() => setActiveTab('proposal')}
                className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                <Building className="w-4 h-4" />
                CE Proposal System
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}