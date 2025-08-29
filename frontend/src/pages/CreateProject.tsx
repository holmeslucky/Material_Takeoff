import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Plus } from 'lucide-react'
import { buildApiUrl, API_ENDPOINTS } from '../config/api'

type TakeoffType = {
  id: string;
  name: string;
  description: string;
  items: any[];
  calculator_settings: any;
}

type ProjectFormData = {
  project_id: string;  // Manual entry by estimator
  name: string;
  client: string;
  quote_number: string;
  date: string;
  estimator: string;
  location: string;
  description?: string;
  takeoff_type?: TakeoffType;
}

type Field = keyof ProjectFormData
type ErrorMap = Partial<Record<Field, string>>

function getLocalISODate(): string {
  // Produces yyyy-mm-dd in the user's local tz (works for <input type="date">)
  return new Date().toLocaleDateString('en-CA')
}

const TAKEOFF_TYPES: TakeoffType[] = [
  {
    id: 'main',
    name: 'Main Takeoff',
    description: 'Standard takeoff for structural steel and miscellaneous items',
    items: [
      { type: 'beam', description: 'W12x35 Beam', quantity: 0, unit: 'LF' },
      { type: 'column', description: 'W8x31 Column', quantity: 0, unit: 'LF' },
      { type: 'plate', description: '1/2" Base Plate', quantity: 0, unit: 'SF' }
    ],
    calculator_settings: {}
  },
  {
    id: 'ductwork',
    name: 'Ductwork Takeoff',
    description: 'Complete ductwork takeoff including welding calculations',
    items: [
      { type: 'duct', description: 'Rectangular Duct 12x8', quantity: 0, unit: 'LF' },
      { type: 'elbow', description: '90° Elbow 12x8', quantity: 0, unit: 'EA' },
      { type: 'transition', description: 'Transition 12x8 to 10x6', quantity: 0, unit: 'EA' }
    ],
    calculator_settings: {
      weld_calculator: {
        seam_type: 'circumferential',
        stitch_pattern: 'standard'
      }
    }
  },
  {
    id: 'pipe',
    name: 'Pipe Takeoff',
    description: 'Industrial piping with fitting calculations',
    items: [
      { type: 'pipe', description: '6" Schedule 40 Pipe', quantity: 0, unit: 'LF' },
      { type: 'elbow', description: '6" 90° Elbow', quantity: 0, unit: 'EA' },
      { type: 'tee', description: '6" Tee', quantity: 0, unit: 'EA' },
      { type: 'flange', description: '6" 150# RF Flange', quantity: 0, unit: 'EA' }
    ],
    calculator_settings: {
      pipe_calculator: {
        nps_size: '6',
        schedule: '40',
        weld_type: 'butt'
      }
    }
  }
]

export default function CreateProject() {
  const navigate = useNavigate()
  const [selectedTakeoffType, setSelectedTakeoffType] = useState<TakeoffType | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<ProjectFormData>({
    project_id: '',
    name: '',
    client: '',
    quote_number: '',
    date: getLocalISODate(),
    estimator: '',
    location: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<ErrorMap>({})
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    return () => {
      // Cancel in-flight request if user navigates away
      abortRef.current?.abort()
    }
  }, [])

  const setField = (field: Field, value: string) => {
    const next = value
    setFormData(prev => ({ ...prev, [field]: next }))
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: undefined }))
  }

  // Trim & normalize some fields
  const handleInputChange = (field: Field, raw: string) => {
    let value = raw
    if (field === 'project_id') value = raw.toUpperCase()
    // prevent long accidental spaces
    value = value.replace(/\s{2,}/g, ' ')
    setField(field, value)
  }

  const validate = (data: ProjectFormData): ErrorMap => {
    const e: ErrorMap = {}
    const req = (v: string) => v && v.trim().length > 0

    if (!req(data.project_id)) e.project_id = 'Project ID is required'
    if (!req(data.name)) e.name = 'Project name is required'
    if (!req(data.client)) e.client = 'Customer is required'
    if (!req(data.quote_number)) e.quote_number = 'Quote number is required'
    if (!req(data.date)) e.date = 'Date is required'
    if (!req(data.estimator)) e.estimator = 'Estimator is required'
    // optional: lightweight patterns
    // if (!/^\\d{2}-\\d{4}$/.test(data.project_id)) e.project_id = 'Format: 25-0001'
    return e
  }

  const isValid = useMemo(() => Object.keys(validate(formData)).length === 0, [formData])

  const handleSubmit: React.FormEventHandler = async (evt) => {
    evt.preventDefault()

    const v = validate(formData)
    setErrors(v)
    if (Object.keys(v).length) return

    if (loading) return
    setLoading(true)

    abortRef.current?.abort()
    abortRef.current = new AbortController()

    try {
      const res = await fetch(buildApiUrl(API_ENDPOINTS.PROJECTS), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          // ensure strings are trimmed on the way out
          project_id: formData.project_id.trim(),
          name: formData.name.trim(),
          client: formData.client.trim(),
          quote_number: formData.quote_number.trim(),
          estimator: formData.estimator.trim(),
          location: formData.location.trim(),
          description: (formData.description || '').trim(),
          // Include takeoff type for pre-populating items
          takeoff_type: selectedTakeoffType?.id || 'main',
          initial_items: selectedTakeoffType?.items || []
        }),
        signal: abortRef.current.signal
      })

      if (res.ok) {
        const project = await safeJson(res)
        console.log('✅ Project created successfully:', project)
        console.log(`🚀 ULTRATHINK: Navigating to /projects/${project.id}`)
        
        // ULTRATHINK: Jump directly to takeoff interface
        navigate(`/projects/${project.id}`)
        return
      }

      // Try to parse JSON error; fall back to text/status
      const errorPayload = await safeJson(res).catch(async () => ({ error: await res.text() }))
      // Friendly cases
      if (res.status === 409) {
        // Conflict: typically unique constraint (e.g., duplicate project_id)
        alert(errorPayload?.detail || 'A project with this Project ID already exists.')
      } else if (res.status === 422 || res.status === 400) {
        const msg = errorPayload?.detail || errorPayload?.error || 'Validation error creating project.'
        alert(msg)
      } else {
        alert(`Failed to create project (${res.status} ${res.statusText})`)
      }
    } catch (err: any) {
      if (err?.name === 'AbortError') {
        // Swallow aborts from unmount/double submit
      } else {
        console.error('Network error:', err)
        alert('Network error: Unable to reach the server. Is the backend running?')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleTakeoffTypeSelect = (type: TakeoffType) => {
    setSelectedTakeoffType(type)
    setShowForm(true)
    setFormData(prev => ({ ...prev, takeoff_type: type }))
  }

  const handleBackToTypes = () => {
    setShowForm(false)
    setSelectedTakeoffType(null)
    setFormData(prev => ({ ...prev, takeoff_type: undefined }))
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {showForm ? (
              <button
                onClick={handleBackToTypes}
                className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
            ) : (
              <Link
                to="/projects"
                className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
            )}
            <div>
              <h1 className="text-2xl font-bold text-white">
                {showForm ? `Create ${selectedTakeoffType?.name}` : 'Choose Takeoff Type'}
              </h1>
              <p className="text-gray-400">
                {showForm ? 'Enter project details' : 'Select the type of takeoff you want to create'}
              </p>
            </div>
          </div>

          {showForm && (
            <button
              type="submit"
              form="create-project-form"
              disabled={loading || !isValid}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              aria-disabled={loading || !isValid}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Create Project
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {!showForm ? (
        /* Takeoff Type Selection */
        <div className="flex-1 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {TAKEOFF_TYPES.map((type) => (
                <div
                  key={type.id}
                  onClick={() => handleTakeoffTypeSelect(type)}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-blue-500 hover:bg-gray-750 cursor-pointer transition-all group"
                >
                  <div className="flex flex-col h-full">
                    <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-blue-300">
                      {type.name}
                    </h3>
                    <p className="text-gray-400 mb-4 flex-1">
                      {type.description}
                    </p>
                    <div className="text-sm text-gray-500">
                      <div className="mb-2">Includes:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {type.items.slice(0, 3).map((item, index) => (
                          <li key={index}>{item.description}</li>
                        ))}
                        {type.items.length > 3 && <li>...and more</li>}
                      </ul>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <span className="text-blue-400 font-medium">Select this type →</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
      {/* Project Header Fields */}
      <form id="create-project-form" onSubmit={handleSubmit} className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center gap-6 text-sm flex-wrap">
          {/* Project ID */}
          <div className="flex items-center gap-2">
            <label htmlFor="project_id" className="text-gray-300 font-medium min-w-[80px]">Project ID:</label>
            <input
              id="project_id"
              type="text"
              value={formData.project_id}
              onChange={(e) => handleInputChange('project_id', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.project_id ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '120px' }}
              placeholder="25-0001"
              aria-invalid={!!errors.project_id}
              aria-describedby={errors.project_id ? 'project_id_error' : undefined}
            />
            {errors.project_id && <span id="project_id_error" className="text-red-400 text-xs">{errors.project_id}</span>}
          </div>

          {/* Project Name */}
          <div className="flex items-center gap-2">
            <label htmlFor="name" className="text-gray-300 font-medium min-w-[70px]">Project:</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.name ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '200px' }}
              placeholder="Enter project name..."
              aria-invalid={!!errors.name}
              aria-describedby={errors.name ? 'name_error' : undefined}
            />
            {errors.name && <span id="name_error" className="text-red-400 text-xs">{errors.name}</span>}
          </div>

          {/* Customer */}
          <div className="flex items-center gap-2">
            <label htmlFor="client" className="text-gray-300 font-medium min-w-[70px]">Customer:</label>
            <input
              id="client"
              type="text"
              value={formData.client}
              onChange={(e) => handleInputChange('client', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.client ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '200px' }}
              placeholder="Enter customer name..."
              aria-invalid={!!errors.client}
              aria-describedby={errors.client ? 'client_error' : undefined}
            />
            {errors.client && <span id="client_error" className="text-red-400 text-xs">{errors.client}</span>}
          </div>

          {/* Quote # */}
          <div className="flex items-center gap-2">
            <label htmlFor="quote_number" className="text-gray-300 font-medium min-w-[60px]">Quote #:</label>
            <input
              id="quote_number"
              type="text"
              value={formData.quote_number}
              onChange={(e) => handleInputChange('quote_number', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.quote_number ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '120px' }}
              placeholder="25-0001"
              aria-invalid={!!errors.quote_number}
              aria-describedby={errors.quote_number ? 'quote_error' : undefined}
            />
            {errors.quote_number && <span id="quote_error" className="text-red-400 text-xs">{errors.quote_number}</span>}
          </div>

          {/* Date */}
          <div className="flex items-center gap-2">
            <label htmlFor="date" className="text-gray-300 font-medium min-w-[40px]">Date:</label>
            <input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) => handleInputChange('date', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.date ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '140px' }}
              aria-invalid={!!errors.date}
              aria-describedby={errors.date ? 'date_error' : undefined}
            />
            {errors.date && <span id="date_error" className="text-red-400 text-xs">{errors.date}</span>}
          </div>

          {/* Estimator */}
          <div className="flex items-center gap-2">
            <label htmlFor="estimator" className="text-gray-300 font-medium min-w-[70px]">Estimator:</label>
            <input
              id="estimator"
              type="text"
              value={formData.estimator}
              onChange={(e) => handleInputChange('estimator', e.target.value)}
              className={`px-3 py-2 bg-gray-900 border rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 ${errors.estimator ? 'border-red-500' : 'border-gray-600'}`}
              style={{ width: '150px' }}
              placeholder="Enter estimator name..."
              aria-invalid={!!errors.estimator}
              aria-describedby={errors.estimator ? 'estimator_error' : undefined}
            />
            {errors.estimator && <span id="estimator_error" className="text-red-400 text-xs">{errors.estimator}</span>}
          </div>
        </div>
      </form>

      {/* Form Content */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Additional Project Information */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Additional Information</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-300 mb-2">Location</label>
                <input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Project location (e.g., Phoenix, AZ)"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Brief description of the project scope..."
                />
              </div>
            </div>
          </div>

          {/* Project Summary */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Project Summary</h2>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <KV label="Project ID" value={formData.project_id} mono />
                <KV label="Project Name" value={formData.name} />
                <KV label="Customer" value={formData.client} />
                <KV label="Quote Number" value={formData.quote_number} />
              </div>
              <div className="space-y-2">
                <KV label="Date" value={formData.date} />
                <KV label="Estimator" value={formData.estimator} />
                <KV label="Location" value={formData.location} />
              </div>
            </div>
          </div>
        </div>
      </div>
        </>
      )}
    </div>
  )
}

function KV({ label, value, mono = false }: { label: string; value?: string; mono?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}:</span>
      <span className={mono ? 'text-white font-mono' : 'text-white'}>
        {value?.trim() ? value : 'Not set'}
      </span>
    </div>
  )
}

async function safeJson(res: Response): Promise<any> {
  const text = await res.text()
  try { return text ? JSON.parse(text) : {} } catch { return { error: text } }
}