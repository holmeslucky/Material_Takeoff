import React, { useState, useEffect } from 'react'
import { Plus, BookTemplate, Edit, Trash2, Copy, Download, Upload } from 'lucide-react'

interface Template {
  id: string
  name: string
  category: 'Main Takeoff' | 'Ductwork Takeoff' | 'Pipe Takeoff'
  description?: string
  items: any[]
  created_date: string
  modified_date: string
}

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Load templates from API
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/templates/')
        if (response.ok) {
          const data = await response.json()
          setTemplates(data)
        }
      } catch (error) {
        console.error('Failed to load templates:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadTemplates()
  }, [])

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || template.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const categories = ['all', 'Main Takeoff', 'Ductwork Takeoff', 'Pipe Takeoff']

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <BookTemplate className="w-7 h-7 text-blue-400" />
              Takeoff Templates
            </h1>
            <p className="text-gray-400">Create templates for Main (Structural), Ductwork (with weld calculators), and Pipe systems</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Template
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-4 mt-4">
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="flex-1 p-4 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading templates...</p>
            </div>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <BookTemplate className="w-16 h-16 mb-4" />
            <h3 className="text-xl font-medium mb-2">No templates found</h3>
            <div className="text-center mb-6 max-w-2xl">
              <p className="mb-4">Create templates for your takeoff workflows:</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-gray-800 rounded-lg p-3">
                  <div className="text-green-400 font-medium mb-1">Main Takeoff</div>
                  <div>Structural steel, plates, angles, misc items</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-3">
                  <div className="text-orange-400 font-medium mb-1">Ductwork Takeoff</div>
                  <div>Includes Main + weld calculators & elbow tools</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-3">
                  <div className="text-purple-400 font-medium mb-1">Pipe Takeoff</div>
                  <div>Includes Main + pipe calculators & fittings</div>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Template
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 hover:bg-gray-850 transition-colors"
              >
                {/* Template Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white truncate">{template.name}</h3>
                    <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${
                      template.category === 'Main Takeoff' 
                        ? 'bg-green-900 text-green-300 border border-green-700'
                        : template.category === 'Ductwork Takeoff'
                        ? 'bg-orange-900 text-orange-300 border border-orange-700'
                        : 'bg-purple-900 text-purple-300 border border-purple-700'
                    }`}>
                      {template.category}
                    </span>
                  </div>
                </div>

                {/* Template Details */}
                <div className="space-y-2 mb-4">
                  {template.description && (
                    <p className="text-sm text-gray-400">{template.description}</p>
                  )}
                  <div className="text-xs text-gray-500">
                    {template.items?.length || 0} items • Created {new Date(template.created_date).toLocaleDateString()}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-3 border-t border-gray-800">
                  <button className="flex items-center gap-1 px-3 py-2 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors">
                    <Download className="w-3 h-3" />
                    Use
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors">
                    <Edit className="w-3 h-3" />
                    Edit
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors">
                    <Copy className="w-3 h-3" />
                    Copy
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors">
                    <Trash2 className="w-3 h-3" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Template Categories Summary */}
      <div className="bg-gray-900 border-t border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} shown
          </span>
          <div className="flex items-center gap-6 text-gray-400">
            {categories.filter(c => c !== 'all').map(category => (
              <span key={category}>
                {category}: {templates.filter(t => t.category === category).length}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}