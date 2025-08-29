import React, { useState, useEffect, useCallback } from 'react'
import { Search, Filter, Download, Upload, Plus, Edit, Trash2, RefreshCw, AlertCircle } from 'lucide-react'

interface Material {
  id: number
  shape_key: string
  category: string
  subcategory?: string
  description: string
  specs_standard?: string
  size_dimensions?: string
  finish_coating?: string
  
  // Pricing - enhanced to handle both systems
  price?: number  // Effective price from backend
  unit_price_per_cwt?: number  // Legacy CWT pricing
  base_price_usd?: number  // Blake's USD pricing
  price_confidence?: string
  
  // Weight - enhanced
  weight?: number  // Effective weight from backend
  weight_per_ft?: number  // Legacy per-foot weight
  weight_per_uom?: number  // Blake's weight per unit
  unit_of_measure?: string
  
  // Legacy dimensions
  thickness_inches?: number
  width_inches?: number
  depth_inches?: number
  flange_width_inches?: number
  web_thickness_inches?: number
  flange_thickness_inches?: number
  
  // Metadata
  supplier?: string
  source_system?: string
  commonly_used?: boolean
  
  created_at?: string
  updated_at?: string
  last_updated?: string
}

export default function MaterialDatabase() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [subcategoryFilter, setSubcategoryFilter] = useState<string>('all')
  const [specsFilter, setSpecsFilter] = useState('')
  const [isAddingMaterial, setIsAddingMaterial] = useState(false)
  
  // Real database state
  const [materials, setMaterials] = useState<Material[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalCount, setTotalCount] = useState(0)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [allCategories, setAllCategories] = useState<string[]>(['Wide Flange', 'Plate', 'Angle', 'HSS/Tube', 'Channel', 'Other'])
  const [allSubcategories, setAllSubcategories] = useState<string[]>([])
  const [allSpecifications, setAllSpecifications] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(100) // Show 100 items per page for better performance

  // Enhanced API Functions for Blake's comprehensive database
  const loadMaterials = useCallback(async (
    searchQuery?: string, 
    categoryQuery?: string, 
    subcategoryQuery?: string,
    specsQuery?: string,
    page: number = 1
  ) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Build API URL with search parameters
      const params = new URLSearchParams()
      
      // For search/filter operations, load more results; for browsing, use pagination
      const isSearching = (searchQuery && searchQuery.trim()) || 
                         (categoryQuery && categoryQuery !== 'all') ||
                         (subcategoryQuery && subcategoryQuery !== 'all') ||
                         (specsQuery && specsQuery.trim())
      const limit = isSearching ? 500 : itemsPerPage
      
      params.append('limit', limit.toString())
      
      // Add pagination for browsing (not searching)
      if (!isSearching && page > 1) {
        const skip = (page - 1) * itemsPerPage
        params.append('skip', skip.toString())
      }
      
      if (searchQuery && searchQuery.trim()) {
        params.append('q', searchQuery.trim())
      }
      
      if (categoryQuery && categoryQuery !== 'all') {
        params.append('category', categoryQuery)
      }
      
      if (subcategoryQuery && subcategoryQuery !== 'all') {
        params.append('subcategory', subcategoryQuery)
      }
      
      if (specsQuery && specsQuery.trim()) {
        params.append('specs', specsQuery.trim())
      }
      
      const url = `http://localhost:7010/api/v1/materials/?${params.toString()}`
      console.log(`Loading materials from: ${url}`)
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to load materials`)
      }
      
      const data = await response.json()
      console.log(`✅ Loaded ${data.length} materials from comprehensive database`)
      
      setMaterials(data)
      setTotalCount(data.length)
      
      // Reset to page 1 when searching/filtering
      if (isSearching) {
        setCurrentPage(1)
      }
    } catch (error) {
      console.error('Materials loading error:', error)
      setError(error instanceof Error ? error.message : 'Failed to load materials')
      setMaterials([])
    } finally {
      setIsLoading(false)
    }
  }, [itemsPerPage])

  // Load available categories from API
  const loadCategories = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:7010/api/v1/materials/categories')
      if (response.ok) {
        const categories = await response.json()
        setAllCategories(categories.sort())
        console.log(`✅ Loaded ${categories.length} material categories`)
      }
    } catch (error) {
      console.warn('Failed to load categories, using defaults:', error)
    }
  }, [])

  // Load available subcategories from API
  const loadSubcategories = useCallback(async (category?: string) => {
    try {
      const url = category && category !== 'all' 
        ? `http://localhost:7010/api/v1/materials/subcategories?category=${category}`
        : 'http://localhost:7010/api/v1/materials/subcategories'
      
      const response = await fetch(url)
      if (response.ok) {
        const subcategories = await response.json()
        setAllSubcategories(subcategories.sort())
        console.log(`✅ Loaded ${subcategories.length} subcategories`)
      }
    } catch (error) {
      console.warn('Failed to load subcategories:', error)
    }
  }, [])

  // Load available ASTM specifications from API
  const loadSpecifications = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:7010/api/v1/materials/specifications')
      if (response.ok) {
        const specifications = await response.json()
        setAllSpecifications(specifications.sort())
        console.log(`✅ Loaded ${specifications.length} ASTM specifications`)
      }
    } catch (error) {
      console.warn('Failed to load specifications:', error)
    }
  }, [])

  const refreshMaterials = useCallback(async () => {
    setIsRefreshing(true)
    await loadMaterials(searchTerm, categoryFilter, subcategoryFilter, specsFilter)
    setIsRefreshing(false)
  }, [loadMaterials, searchTerm, categoryFilter, subcategoryFilter, specsFilter])

  // Search function with debouncing
  const performSearch = useCallback(async () => {
    await loadMaterials(searchTerm, categoryFilter, subcategoryFilter, specsFilter)
  }, [loadMaterials, searchTerm, categoryFilter, subcategoryFilter, specsFilter])

  // Export functionality
  const exportMaterials = useCallback(async () => {
    try {
      // Export current filtered results
      const exportData = materials.map(material => ({
        shape_key: material.shape_key,
        category: material.category,
        subcategory: material.subcategory || '',
        description: material.description,
        specs_standard: material.specs_standard || '',
        size_dimensions: material.size_dimensions || '',
        finish_coating: material.finish_coating || '',
        price: material.price || '',
        unit_price_per_cwt: material.unit_price_per_cwt || '',
        base_price_usd: material.base_price_usd || '',
        weight: material.weight || '',
        unit_of_measure: material.unit_of_measure || '',
        supplier: material.supplier || '',
        source_system: material.source_system || '',
        commonly_used: material.commonly_used || false
      }))

      // Create CSV content
      const headers = Object.keys(exportData[0]).join(',')
      const csvContent = [
        headers,
        ...exportData.map(row => Object.values(row).map(val => 
          typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val
        ).join(','))
      ].join('\n')

      // Download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `materials_export_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      
      console.log(`✅ Exported ${exportData.length} materials to CSV`)
    } catch (error) {
      console.error('Export failed:', error)
      setError('Failed to export materials')
    }
  }, [materials])

  // Import functionality placeholder
  const importMaterials = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.csv,.xlsx,.xls'
    input.onchange = (event) => {
      const file = (event.target as HTMLInputElement).files?.[0]
      if (file) {
        console.log('Selected file for import:', file.name)
        // TODO: Implement CSV/Excel parsing and bulk material creation
        alert('Import functionality will be implemented - this will parse CSV/Excel files and bulk import materials')
      }
    }
    input.click()
  }, [])

  // Load materials and categories on component mount
  useEffect(() => {
    loadMaterials()
    loadCategories()
    loadSubcategories()
    loadSpecifications()
  }, [loadMaterials, loadCategories, loadSubcategories, loadSpecifications])

  // Load subcategories when category changes
  useEffect(() => {
    loadSubcategories(categoryFilter)
    // Reset subcategory filter when category changes
    if (categoryFilter !== 'all') {
      setSubcategoryFilter('all')
    }
  }, [categoryFilter, loadSubcategories])

  // Trigger search when filters change (with debouncing)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm || categoryFilter !== 'all' || subcategoryFilter !== 'all' || specsFilter) {
        performSearch()
      } else {
        loadMaterials() // Load all if no filters
      }
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [searchTerm, categoryFilter, subcategoryFilter, specsFilter, performSearch, loadMaterials])

  // Use categories from API
  const categories = allCategories

  // Use materials directly since filtering is now done server-side
  const filteredMaterials = materials

  const getCategoryColor = (category: string, subcategory?: string) => {
    // Use subcategory for better categorization if available
    const displayCategory = subcategory || category
    
    switch (displayCategory) {
      case 'Wide Flange':
      case 'Structural':
        return 'bg-blue-900 text-blue-300 border-blue-700'
      case 'Plate':
        return 'bg-green-900 text-green-300 border-green-700'
      case 'Angle':
        return 'bg-yellow-900 text-yellow-300 border-yellow-700'
      case 'HSS':
      case 'HSS/Tube':
        return 'bg-purple-900 text-purple-300 border-purple-700'
      case 'Channel':
        return 'bg-red-900 text-red-300 border-red-700'
      case 'Fitting':
        return 'bg-orange-900 text-orange-300 border-orange-700'
      case 'Pipe':
        return 'bg-indigo-900 text-indigo-300 border-indigo-700'
      case 'Valve':
        return 'bg-pink-900 text-pink-300 border-pink-700'
      case 'Flange':
        return 'bg-teal-900 text-teal-300 border-teal-700'
      case 'Component':
        return 'bg-cyan-900 text-cyan-300 border-cyan-700'
      default:
        return 'bg-gray-900 text-gray-300 border-gray-700'
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white">Material Database</h1>
            <p className="text-xl text-gray-400">Comprehensive materials: Steel, Pipes, Fittings, Valves, Components</p>
            <p className="text-lg text-gray-500">{totalCount.toLocaleString()} materials from multiple sources</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={refreshMaterials}
              disabled={isRefreshing}
              className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 text-white px-6 py-3 rounded-lg text-xl font-medium transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button 
              onClick={importMaterials}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg text-xl font-medium transition-colors"
            >
              <Upload className="w-4 h-4" />
              Import
            </button>
            <button 
              onClick={exportMaterials}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-xl font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => setIsAddingMaterial(true)}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg text-xl font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Material
            </button>
          </div>
        </div>

        {/* Enhanced Filters */}
        <div className="flex items-center gap-4 mt-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search materials, specs, dimensions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-6 py-3 bg-gray-800 border border-gray-700 rounded-lg text-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-xl text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          {/* Subcategory Filter */}
          {allSubcategories.length > 0 && (
            <select
              value={subcategoryFilter}
              onChange={(e) => setSubcategoryFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-xl text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              {allSubcategories.map(subcategory => (
                <option key={subcategory} value={subcategory}>{subcategory}</option>
              ))}
            </select>
          )}

          {/* ASTM Specs Dropdown */}
          {allSpecifications.length > 0 && (
            <select
              value={specsFilter}
              onChange={(e) => setSpecsFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-xl text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
            >
              <option value="">All ASTM Specs</option>
              {allSpecifications.map(spec => (
                <option key={spec} value={spec}>{spec}</option>
              ))}
            </select>
          )}
          
          {/* Fallback search if specs haven't loaded */}
          {allSpecifications.length === 0 && (
            <input
              type="text"
              placeholder="ASTM Specs..."
              value={specsFilter}
              onChange={(e) => setSpecsFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg text-xl text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 w-40"
            />
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-900 border border-red-700 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <div>
            <p className="text-xl text-red-300 font-medium">Database Connection Error</p>
            <p className="text-red-400 text-lg">{error}</p>
          </div>
          <button
            onClick={refreshMaterials}
            className="ml-auto px-4 py-2 bg-red-800 hover:bg-red-700 text-red-200 rounded text-lg"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3 text-gray-400">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <span className="text-xl">Loading {totalCount > 0 ? `${totalCount} ` : ''}materials...</span>
          </div>
        </div>
      )}

      {/* Materials Table */}
      {!isLoading && (
        <div className="flex-1 overflow-auto">
          <div className="bg-gray-800 m-4 rounded-lg border border-gray-700">
            <div className="overflow-x-auto">
              <table className="w-full text-lg">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="text-left p-4 text-lg text-gray-300">Material</th>
                  <th className="text-left p-4 text-lg text-gray-300">Category/Type</th>
                  <th className="text-left p-4 text-lg text-gray-300">Specs/Standard</th>
                  <th className="text-left p-4 text-lg text-gray-300">Size/Dimensions</th>
                  <th className="text-left p-4 text-lg text-gray-300">Weight</th>
                  <th className="text-left p-4 text-lg text-gray-300">Price</th>
                  <th className="text-left p-4 text-lg text-gray-300">Supplier</th>
                  <th className="text-left p-4 text-lg text-gray-300">Source</th>
                  <th className="text-left p-4 text-lg text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredMaterials.map((material) => (
                  <tr key={material.id} className="border-b border-gray-700 hover:bg-gray-750">
                    {/* Material Designation */}
                    <td className="p-4">
                      <div className="font-mono text-lg text-white font-semibold">
                        {material.shape_key}
                      </div>
                      {material.description && (
                        <div className="text-sm text-gray-400 mt-1">
                          {material.description}
                        </div>
                      )}
                    </td>
                    
                    {/* Category/Type */}
                    <td className="p-4">
                      <span className={`px-3 py-1 text-sm rounded-full border ${getCategoryColor(material.category, material.subcategory)}`}>
                        {material.subcategory || material.category}
                      </span>
                      {material.finish_coating && (
                        <div className="text-xs text-gray-500 mt-1">{material.finish_coating}</div>
                      )}
                    </td>
                    
                    {/* Specs/Standard */}
                    <td className="p-4 text-lg text-gray-300">
                      {material.specs_standard || '-'}
                    </td>
                    
                    {/* Size/Dimensions */}
                    <td className="p-4 text-gray-300 font-mono text-sm">
                      {material.size_dimensions || 
                       (material.thickness_inches || material.width_inches || material.depth_inches ? (
                         <>
                           {material.thickness_inches ? `${material.thickness_inches}"` : ''} 
                           {material.width_inches ? ` × ${material.width_inches}"` : ''}
                           {material.depth_inches ? ` × ${material.depth_inches}"` : ''}
                         </>
                       ) : '-')}
                    </td>
                    
                    {/* Weight */}
                    <td className="p-4 text-lg text-white">
                      {material.weight ? `${material.weight} ${material.unit_of_measure || 'lbs'}` :
                       material.weight_per_ft ? `${material.weight_per_ft} lbs/ft` : '-'}
                    </td>
                    
                    {/* Price */}
                    <td className="p-4">
                      {material.price ? (
                        <div className="text-lg text-green-400 font-semibold">
                          ${material.price.toFixed(2)}
                          {material.unit_of_measure && material.unit_of_measure !== 'each' && (
                            <span className="text-sm text-gray-400">/{material.unit_of_measure}</span>
                          )}
                        </div>
                      ) : material.unit_price_per_cwt ? (
                        <div className="text-lg text-green-400 font-semibold">
                          ${material.unit_price_per_cwt.toFixed(2)}/cwt
                        </div>
                      ) : (
                        <span className="text-gray-500">No price</span>
                      )}
                      {material.price_confidence && material.price_confidence !== 'high' && (
                        <div className="text-xs text-yellow-400">{material.price_confidence} confidence</div>
                      )}
                    </td>
                    
                    {/* Supplier */}
                    <td className="p-4 text-lg text-gray-300">
                      {material.supplier || 'Unknown'}
                    </td>
                    
                    {/* Source */}
                    <td className="p-4">
                      <span className={`px-2 py-1 text-xs rounded ${
                        material.source_system === 'blake' 
                          ? 'bg-purple-900 text-purple-300' 
                          : 'bg-gray-800 text-gray-400'
                      }`}>
                        {material.source_system === 'blake' ? 'Comprehensive' : 'Legacy'}
                      </span>
                    </td>
                    
                    {/* Actions */}
                    <td className="p-4">
                      <div className="flex items-center gap-1">
                        <button className="p-1 text-blue-400 hover:text-blue-300 hover:bg-blue-900 rounded">
                          <Edit className="w-3 h-3" />
                        </button>
                        <button className="p-1 text-red-400 hover:text-red-300 hover:bg-red-900 rounded">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredMaterials.length === 0 && (
              <div className="flex flex-col items-center justify-center h-32 text-gray-400">
                <Search className="w-12 h-12 mb-2" />
                <p className="text-xl">No materials found</p>
                <p className="text-lg">Try adjusting your search or filters</p>
              </div>
            )}
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Stats Bar - Comprehensive Database */}
      <div className="bg-gray-900 border-t border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between text-lg">
          <div className="flex items-center gap-6">
            <span className="text-xl text-gray-300 font-semibold">
              {filteredMaterials.length.toLocaleString()} materials shown
            </span>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-purple-400">
                Blake's: {materials.filter(m => m.source_system === 'blake').length.toLocaleString()}
              </span>
              <span className="text-gray-400">
                Legacy: {materials.filter(m => m.source_system === 'legacy').length.toLocaleString()}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-400">
            {/* Show comprehensive subcategory counts */}
            {[
              { key: 'Fitting', color: 'text-orange-400' },
              { key: 'Pipe', color: 'text-indigo-400' },
              { key: 'Valve', color: 'text-pink-400' },
              { key: 'Flange', color: 'text-teal-400' },
              { key: 'Component', color: 'text-cyan-400' },
              { key: 'Wide Flange', color: 'text-blue-400' },
              { key: 'Plate', color: 'text-green-400' }
            ].map(({ key, color }) => {
              const count = materials.filter(m => m.subcategory === key || m.category === key).length
              return count > 0 ? (
                <span key={key} className={color}>
                  {key}: {count.toLocaleString()}
                </span>
              ) : null
            })}
          </div>
        </div>
      </div>

      {/* Add Material Modal (Phase 3) */}
      {isAddingMaterial && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 max-w-md w-full">
            <h3 className="text-2xl font-semibold text-white mb-4">Add New Material</h3>
            <p className="text-gray-400 text-lg mb-4">
              Material addition functionality will be implemented in Phase 3
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setIsAddingMaterial(false)}
                className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-xl text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}