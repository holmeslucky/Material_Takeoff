import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Calendar, Building, Filter, Trash2, AlertTriangle } from 'lucide-react'
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

export default function Projects() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | string>('all')

  // Load projects from API - no demo data
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  
  // Delete project state
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  
  // Load projects from backend
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const response = await fetch(buildApiUrl(API_ENDPOINTS.PROJECTS))
        if (response.ok) {
          const data = await response.json()
          setProjects(data)
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadProjects()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-900 text-green-300 border-green-700'
      case 'pending':
        return 'bg-yellow-900 text-yellow-300 border-yellow-700'
      case 'completed':
        return 'bg-blue-900 text-blue-300 border-blue-700'
      case 'on_hold':
        return 'bg-red-900 text-red-300 border-red-700'
      default:
        return 'bg-green-900 text-green-300 border-green-700' // Default to active green
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  // Handle project deletion
  const handleDeleteProject = async (project: Project) => {
    setProjectToDelete(project)
  }

  const confirmDeleteProject = async () => {
    if (!projectToDelete) return

    setIsDeleting(true)
    try {
      const response = await fetch(buildApiUrl(`${API_ENDPOINTS.PROJECTS}/${projectToDelete.id}`), {
        method: 'DELETE'
      })

      if (response.ok) {
        // Remove project from local state
        setProjects(prev => prev.filter(p => p.id !== projectToDelete.id))
        setProjectToDelete(null)
      } else {
        console.error('Failed to delete project:', response.statusText)
        alert('Failed to delete project. Please try again.')
      }
    } catch (error) {
      console.error('Error deleting project:', error)
      alert('Error deleting project. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const cancelDelete = () => {
    setProjectToDelete(null)
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Projects</h1>
            <p className="text-gray-400">Manage takeoff projects and estimates</p>
          </div>
          <Link
            to="/projects/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Project
          </Link>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mt-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="on_hold">On Hold</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="flex-1 p-4 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading projects...</p>
            </div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Building className="w-16 h-16 mb-4" />
            <h3 className="text-xl font-medium mb-2">No projects found</h3>
            <p>Create your first project to get started with takeoffs</p>
            <Link
              to="/projects/new"
              className="mt-4 flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Project
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 hover:bg-gray-850 transition-colors relative group"
              >
                {/* Clickable area to view project */}
                <Link
                  to={`/projects/${project.id}`}
                  className="absolute inset-0 rounded-lg"
                ></Link>
                
                {/* Delete button - positioned to not interfere with Link */}
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleDeleteProject(project)
                  }}
                  className="absolute top-2 right-2 p-1.5 rounded-lg bg-gray-800 text-gray-400 hover:text-red-400 hover:bg-red-900 opacity-0 group-hover:opacity-100 transition-all z-10"
                  title="Delete project"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                {/* Project Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white truncate">{project.name}</h3>
                    <p className="text-sm text-gray-400">{project.client}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(project.status)}`}>
                    {project.status.charAt(0).toUpperCase() + project.status.slice(1).replace('_', ' ')}
                  </span>
                </div>

                {/* Project Details */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Building className="w-4 h-4 text-gray-400" />
                    {project.location || 'No location specified'}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </div>
                </div>

                {/* Project Metrics */}
                <div className="mt-4 pt-3 border-t border-gray-800">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-400">Total Tons</p>
                      <p className="text-sm font-medium text-white">{project.total_weight_tons.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Est. Value</p>
                      <p className="text-sm font-medium text-green-400">
                        ${project.total_value.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats Bar */}
      <div className="bg-gray-900 border-t border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''} shown
          </span>
          <div className="flex items-center gap-6 text-gray-400">
            <span>
              Active: {projects.filter(p => p.status.toLowerCase() === 'active').length}
            </span>
            <span>
              Entries: {projects.reduce((sum, p) => sum + p.total_entries, 0)}
            </span>
            <span>
              Total Value: ${projects.reduce((sum, p) => sum + p.total_value, 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {projectToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-900 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Delete Project</h3>
                <p className="text-gray-400 text-sm">This action cannot be undone</p>
              </div>
            </div>

            <div className="mb-6">
              <p className="text-gray-300">
                Are you sure you want to delete <strong className="text-white">"{projectToDelete.name}"</strong>?
              </p>
              <p className="text-gray-400 text-sm mt-2">
                This will permanently delete the project and all associated takeoff entries 
                ({projectToDelete.total_entries} entries, {projectToDelete.total_weight_tons.toFixed(1)} tons).
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={cancelDelete}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDeleteProject}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    Delete Project
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}