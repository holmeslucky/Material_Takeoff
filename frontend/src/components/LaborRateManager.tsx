import React, { useState, useEffect } from 'react'
import { Wrench, DollarSign, Plus, Edit3, Trash2, Save, X, Settings } from 'lucide-react'

interface LaborOperation {
  id: number
  name: string
  rate: string
  operation_type: 'per_ft' | 'per_piece'
  description: string
  unit_display: string
  active: boolean
}

interface CoatingSystem {
  id: number
  name: string
  coating_type: 'area' | 'weight' | 'none'
  rate: string
  description: string
  unit_display: string
  active: boolean
}

interface LaborSetting {
  id: number
  setting_key: string
  setting_value: string
  description: string
  unit: string
}

interface EditingItem {
  id: number
  field: string
  value: string
}

interface NewOperation {
  name: string
  rate: string
  operation_type: 'per_ft' | 'per_piece'
  description: string
  unit_display: string
}

interface NewCoating {
  name: string
  coating_type: 'area' | 'weight' | 'none'
  rate: string
  description: string
  unit_display: string
}

export default function LaborRateManager() {
  const [laborOperations, setLaborOperations] = useState<LaborOperation[]>([])
  const [coatingSystems, setCoatingSystems] = useState<CoatingSystem[]>([])
  const [laborSettings, setLaborSettings] = useState<LaborSetting[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<EditingItem | null>(null)
  const [showAddOperation, setShowAddOperation] = useState(false)
  const [showAddCoating, setShowAddCoating] = useState(false)
  const [newOperation, setNewOperation] = useState<NewOperation>({
    name: '',
    rate: '',
    operation_type: 'per_piece',
    description: '',
    unit_display: 'per piece'
  })
  const [newCoating, setNewCoating] = useState<NewCoating>({
    name: '',
    coating_type: 'area',
    rate: '',
    description: '',
    unit_display: 'per square foot'
  })

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [operationsRes, coatingsRes, settingsRes] = await Promise.all([
        fetch('http://localhost:7000/api/v1/labor-mgmt/operations'),
        fetch('http://localhost:7000/api/v1/labor-mgmt/coatings'),
        fetch('http://localhost:7000/api/v1/labor-mgmt/settings')
      ])

      if (!operationsRes.ok || !coatingsRes.ok || !settingsRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const [operations, coatings, settings] = await Promise.all([
        operationsRes.json(),
        coatingsRes.json(),
        settingsRes.json()
      ])

      setLaborOperations(operations)
      setCoatingSystems(coatings)
      setLaborSettings(settings)
      setError(null)
    } catch (err) {
      setError('Failed to load data. Please check that the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleEditStart = (id: number, field: string, currentValue: string) => {
    setEditing({ id, field, value: currentValue })
  }

  const handleEditSave = async (type: 'operation' | 'coating' | 'setting') => {
    if (!editing) return

    try {
      const endpoint = type === 'operation' 
        ? `http://localhost:7000/api/v1/labor-mgmt/operations/${editing.id}`
        : type === 'coating'
        ? `http://localhost:7000/api/v1/labor-mgmt/coatings/${editing.id}`
        : `http://localhost:7000/api/v1/labor-mgmt/settings/${laborSettings.find(s => s.id === editing.id)?.setting_key}`

      const body = type === 'setting' 
        ? { setting_value: editing.value }
        : { [editing.field]: editing.value }

      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!response.ok) throw new Error('Failed to save')

      await fetchAllData()
      setEditing(null)
    } catch (err) {
      setError('Failed to save changes')
    }
  }

  const handleDelete = async (type: 'operation' | 'coating', id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return

    try {
      const endpoint = type === 'operation'
        ? `http://localhost:7000/api/v1/labor-mgmt/operations/${id}`
        : `http://localhost:7000/api/v1/labor-mgmt/coatings/${id}`

      const response = await fetch(endpoint, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to delete')

      await fetchAllData()
    } catch (err) {
      setError('Failed to delete item')
    }
  }

  const handleAddOperation = async () => {
    if (!newOperation.name || !newOperation.rate) {
      setError('Name and rate are required')
      return
    }

    try {
      const response = await fetch('http://localhost:7000/api/v1/labor-mgmt/operations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newOperation)
      })

      if (!response.ok) throw new Error('Failed to create operation')

      await fetchAllData()
      setShowAddOperation(false)
      setNewOperation({
        name: '',
        rate: '',
        operation_type: 'per_piece',
        description: '',
        unit_display: 'per piece'
      })
      setError(null)
    } catch (err) {
      setError('Failed to create new operation')
    }
  }

  const handleAddCoating = async () => {
    if (!newCoating.name || !newCoating.rate) {
      setError('Name and rate are required')
      return
    }

    try {
      const response = await fetch('http://localhost:7000/api/v1/labor-mgmt/coatings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCoating)
      })

      if (!response.ok) throw new Error('Failed to create coating')

      await fetchAllData()
      setShowAddCoating(false)
      setNewCoating({
        name: '',
        coating_type: 'area',
        rate: '',
        description: '',
        unit_display: 'per square foot'
      })
      setError(null)
    } catch (err) {
      setError('Failed to create new coating')
    }
  }

  const handleCoatingTypeChange = (type: 'area' | 'weight' | 'none') => {
    const unitDisplay = type === 'area' 
      ? 'per square foot' 
      : type === 'weight' 
      ? 'per pound' 
      : 'none'
    
    setNewCoating({
      ...newCoating,
      coating_type: type,
      unit_display: unitDisplay
    })
  }

  const renderEditableField = (id: number, field: string, value: string, type: 'operation' | 'coating' | 'setting') => {
    const isEditing = editing?.id === id && editing?.field === field

    if (isEditing) {
      return (
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={editing.value}
            onChange={(e) => setEditing({ ...editing, value: e.target.value })}
            className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-lg"
            onKeyPress={(e) => e.key === 'Enter' && handleEditSave(type)}
            autoFocus
          />
          <button
            onClick={() => handleEditSave(type)}
            className="p-2 text-green-400 hover:text-green-300"
          >
            <Save className="w-5 h-5" />
          </button>
          <button
            onClick={() => setEditing(null)}
            className="p-2 text-red-400 hover:text-red-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )
    }

    return (
      <div
        className="flex items-center justify-between group cursor-pointer hover:bg-gray-700 px-3 py-2 rounded"
        onClick={() => handleEditStart(id, field, value)}
      >
        <span>{value}</span>
        <Edit3 className="w-4 h-4 text-gray-500 group-hover:text-gray-300 opacity-0 group-hover:opacity-100" />
      </div>
    )
  }

  if (loading) {
    return (
      <div className="h-full bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-xl text-gray-400">Loading labor rates...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-gray-950 text-white overflow-auto">
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Wrench className="w-12 h-12 text-blue-500" />
            <h1 className="text-4xl font-bold">Labor & Coatings Management</h1>
          </div>
          <p className="text-xl text-gray-400">
            Manage labor operation rates, coating system prices, and base settings
          </p>
        </div>

        {error && (
          <div className="mb-8 p-6 bg-red-900/50 border border-red-600 rounded-lg">
            <p className="text-lg text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Labor Operations */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <Settings className="w-8 h-8 text-blue-400" />
                Labor Operations
              </h2>
              <button
                onClick={() => setShowAddOperation(true)}
                className="flex items-center gap-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-medium transition-colors"
              >
                <Plus className="w-6 h-6" />
                Add New
              </button>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 gap-4 p-4 bg-gray-800 text-lg font-medium text-gray-300 border-b border-gray-700">
                <div>Operation</div>
                <div>Rate</div>
                <div>Type</div>
                <div>Actions</div>
              </div>
              
              {laborOperations.map((operation) => (
                <div key={operation.id} className="grid grid-cols-4 gap-4 p-4 border-b border-gray-800 last:border-b-0 hover:bg-gray-800/50">
                  <div>
                    <div className="font-medium text-lg">{renderEditableField(operation.id, 'name', operation.name, 'operation')}</div>
                    <div className="text-sm text-gray-400 mt-1">{operation.description}</div>
                  </div>
                  <div>
                    <div className="text-lg">{renderEditableField(operation.id, 'rate', operation.rate, 'operation')}</div>
                    <div className="text-sm text-gray-400 mt-1">{operation.unit_display}</div>
                  </div>
                  <div>
                    <span className={`px-3 py-1 rounded text-sm ${
                      operation.operation_type === 'per_ft' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-green-600 text-white'
                    }`}>
                      {operation.operation_type === 'per_ft' ? 'Per Foot' : 'Per Piece'}
                    </span>
                  </div>
                  <div>
                    <button
                      onClick={() => handleDelete('operation', operation.id)}
                      className="p-2 text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Coating Systems */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <DollarSign className="w-8 h-8 text-green-400" />
                Coating Systems
              </h2>
              <button
                onClick={() => setShowAddCoating(true)}
                className="flex items-center gap-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-lg font-medium transition-colors"
              >
                <Plus className="w-6 h-6" />
                Add New
              </button>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 gap-4 p-4 bg-gray-800 text-lg font-medium text-gray-300 border-b border-gray-700">
                <div>Coating</div>
                <div>Rate</div>
                <div>Type</div>
                <div>Actions</div>
              </div>
              
              {coatingSystems.map((coating) => (
                <div key={coating.id} className="grid grid-cols-4 gap-4 p-4 border-b border-gray-800 last:border-b-0 hover:bg-gray-800/50">
                  <div>
                    <div className="font-medium text-lg">{renderEditableField(coating.id, 'name', coating.name, 'coating')}</div>
                    <div className="text-sm text-gray-400 mt-1">{coating.description}</div>
                  </div>
                  <div>
                    <div className="text-lg">{renderEditableField(coating.id, 'rate', coating.rate, 'coating')}</div>
                    <div className="text-sm text-gray-400 mt-1">{coating.unit_display}</div>
                  </div>
                  <div>
                    <span className={`px-3 py-1 rounded text-sm ${
                      coating.coating_type === 'area' 
                        ? 'bg-purple-600 text-white' 
                        : coating.coating_type === 'weight'
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-600 text-white'
                    }`}>
                      {coating.coating_type === 'area' ? 'Area' : coating.coating_type === 'weight' ? 'Weight' : 'None'}
                    </span>
                  </div>
                  <div>
                    <button
                      onClick={() => handleDelete('coating', coating.id)}
                      className="p-2 text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Base Settings */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="font-semibold text-xl mb-6 flex items-center gap-2">
                <DollarSign className="w-6 h-6 text-green-400" />
                Base Settings
              </h3>
              <div className="space-y-4">
                {laborSettings.map((setting) => (
                  <div key={setting.id} className="flex justify-between items-center">
                    <div>
                      <span className="text-lg text-gray-300">{setting.description}:</span>
                      <div className="text-sm text-gray-500">{setting.unit}</div>
                    </div>
                    <div className="w-32">
                      {renderEditableField(setting.id, 'setting_value', setting.setting_value, 'setting')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add New Operation Modal */}
      {showAddOperation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 w-full max-w-md">
            <h3 className="text-2xl font-semibold mb-6">Add New Labor Operation</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Operation Name
                </label>
                <input
                  type="text"
                  value={newOperation.name}
                  onChange={(e) => setNewOperation({...newOperation, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Welding"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Rate (hours per piece)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={newOperation.rate}
                  onChange={(e) => setNewOperation({...newOperation, rate: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 0.25"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={newOperation.description}
                  onChange={(e) => setNewOperation({...newOperation, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of the operation"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <button
                onClick={handleAddOperation}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg text-lg font-medium transition-colors"
              >
                Add Operation
              </button>
              <button
                onClick={() => setShowAddOperation(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-lg text-lg font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add New Coating Modal */}
      {showAddCoating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 w-full max-w-md">
            <h3 className="text-2xl font-semibold mb-6">Add New Coating System</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Coating Name
                </label>
                <input
                  type="text"
                  value={newCoating.name}
                  onChange={(e) => setNewCoating({...newCoating, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g., Zinc Plating"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Coating Type
                </label>
                <select
                  value={newCoating.coating_type}
                  onChange={(e) => handleCoatingTypeChange(e.target.value as 'area' | 'weight' | 'none')}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="area">Area-based (per sq ft)</option>
                  <option value="weight">Weight-based (per lb)</option>
                  <option value="none">No coating</option>
                </select>
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Rate ({newCoating.unit_display})
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newCoating.rate}
                  onChange={(e) => setNewCoating({...newCoating, rate: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g., 3.50"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={newCoating.description}
                  onChange={(e) => setNewCoating({...newCoating, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Brief description of the coating"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <button
                onClick={handleAddCoating}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg text-lg font-medium transition-colors"
              >
                Add Coating
              </button>
              <button
                onClick={() => setShowAddCoating(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-lg text-lg font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}