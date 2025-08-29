import React, { useState, useEffect, useCallback, useMemo, memo, useRef } from 'react'
import { Plus, Calculator, Trash2, Copy, Save, CheckCircle, AlertTriangle, Lock, Loader } from 'lucide-react'
import { buildApiUrl, API_ENDPOINTS } from '../config/api'

// Debounce utility function
const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout | null = null
  return (...args: any[]) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// Enums matching backend
enum Operation {
  PRESSBRAKE_FORMING = "Pressbrake Forming",
  ROLL_FORMING = "Roll Forming",
  SAW_CUTTING = "Saw Cutting",
  DRILL_PUNCH = "Drill & Punch",
  DRAGON_PLASMA_CUTTING = "Dragon Plasma Cutting",
  BEAM_LINE_CUTTING = "Beam Line Cutting",
  SHEARING = "Shearing"
}

enum CoatingSystem {
  SHOP_COATING = "Shop Coating",
  EPOXY = "Epoxy",
  POWDER_COAT = "Powder Coat",
  GALVANIZED = "Galvanized",
  NONE = "None"
}

// Labor operation rates (from backend takeoff_service.py)
const LABOR_OPERATION_RATES: Record<Operation, { rate: number, unit: string }> = {
  [Operation.PRESSBRAKE_FORMING]: { rate: 0.5, unit: "/ft" },
  [Operation.ROLL_FORMING]: { rate: 0.5, unit: "/ft" },
  [Operation.SAW_CUTTING]: { rate: 0.18, unit: "/ft" },
  [Operation.DRILL_PUNCH]: { rate: 0.24, unit: "/ft" },
  [Operation.DRAGON_PLASMA_CUTTING]: { rate: 0.18, unit: "/ft" },
  [Operation.BEAM_LINE_CUTTING]: { rate: 1.0, unit: "/pc" },
  [Operation.SHEARING]: { rate: 0.0667, unit: "/ft" },
}

// Coating system rates (from backend takeoff_service.py)
const COATING_SYSTEM_RATES: Record<CoatingSystem, { rate: number, unit: string }> = {
  [CoatingSystem.SHOP_COATING]: { rate: 2.85, unit: "$/sqft" },
  [CoatingSystem.EPOXY]: { rate: 4.85, unit: "$/sqft" },
  [CoatingSystem.POWDER_COAT]: { rate: 4.85, unit: "$/sqft" },
  [CoatingSystem.GALVANIZED]: { rate: 0.67, unit: "$/lb" },
  [CoatingSystem.NONE]: { rate: 0, unit: "" },
}

interface TakeoffEntry {
  id?: string
  qty: number
  shape_key: string
  description: string
  length_ft: number
  length_in?: number  // For plates - length in inches
  width_in?: number  // For plates - width in inches
  thickness_in?: number  // For plates - thickness in inches
  weight_per_ft: number
  total_length_ft: number
  total_weight_lbs: number
  total_weight_tons: number
  unit_price_per_cwt: number
  total_price: number
  labor_hours?: number
  labor_cost?: number
  operations?: Operation[]
  coatings_selected?: CoatingSystem[]
  primary_coating?: string
  coating_cost?: number
  notes?: string  // Added notes field
  
}

interface TakeoffGridProps {
  projectId: string
  laborMode: 'manual' // Fixed to manual only
  onTotalsChange?: (totals: any) => void
  onSaveFunctionReady?: (saveFunction: () => Promise<void>) => void
}

const TakeoffGrid = memo(function TakeoffGrid({ projectId, laborMode, onTotalsChange, onSaveFunctionReady }: TakeoffGridProps) {
  const [entries, setEntries] = useState<TakeoffEntry[]>([])
  const [newEntry, setNewEntry] = useState<Partial<TakeoffEntry>>({
    qty: undefined, // Start empty
    shape_key: '',
    description: '',
    length_ft: 0,
    length_in: 0,
    width_in: 0,
    thickness_in: 0,
    labor_hours: 0,
    labor_cost: 0,
    operations: [],
    coatings_selected: [],
    primary_coating: '',
    notes: '',
  })
  const [isCalculating, setIsCalculating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [materialSuggestions, setMaterialSuggestions] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [descriptionSuggestions, setDescriptionSuggestions] = useState<string[]>([])
  const [showDescriptionSuggestions, setShowDescriptionSuggestions] = useState(false)
  const [isCurrentShapePlate, setIsCurrentShapePlate] = useState(false)
  
  // Material validation states
  const [materialValidationState, setMaterialValidationState] = useState<'none' | 'pending' | 'confirmed' | 'unconfirmed'>('none')
  const [confirmedMaterialData, setConfirmedMaterialData] = useState<any>(null)
  
  // Enhanced client-side material cache with LRU behavior
  const [materialCache, setMaterialCache] = useState<Map<string, any>>(new Map())
  const [searchCache, setSearchCache] = useState<Map<string, any[]>>(new Map())
  const [isInitializing, setIsInitializing] = useState(true)
  const [isLoadingEntries, setIsLoadingEntries] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Helper function to detect if shape is a plate
  const isPlate = (shapeKey: string): boolean => {
    return shapeKey.toUpperCase().startsWith('PL') || 
           shapeKey.toUpperCase().includes('PLATE') ||
           shapeKey.toUpperCase().startsWith('PL-')
  }

  // Common materials database for instant validation (synchronized with backend database)
  const commonMaterials = useMemo(() => ({
    // W-Beams (accurate weights and pricing from capitol_takeoff.db)
    'W6X9': { shape_key: 'W6X9', description: 'Wide Flange Beam W6X9 - 9.0 lb/ft', weight_per_ft: 9.0, unit_price_per_cwt: 85.9, category: 'Wide Flange' },
    'W6X12': { shape_key: 'W6X12', description: 'Wide Flange Beam W6X12 - 12.0 lb/ft', weight_per_ft: 12.0, unit_price_per_cwt: 86.2, category: 'Wide Flange' },
    'W6X15': { shape_key: 'W6X15', description: 'Wide Flange Beam W6X15 - 15.0 lb/ft', weight_per_ft: 15.0, unit_price_per_cwt: 86.5, category: 'Wide Flange' },
    'W6X16': { shape_key: 'W6X16', description: 'Wide Flange Beam W6X16 - 16.0 lb/ft', weight_per_ft: 16.0, unit_price_per_cwt: 86.6, category: 'Wide Flange' },
    'W6X20': { shape_key: 'W6X20', description: 'Wide Flange Beam W6X20 - 20.0 lb/ft', weight_per_ft: 20.0, unit_price_per_cwt: 87.0, category: 'Wide Flange' },
    'W6X25': { shape_key: 'W6X25', description: 'Wide Flange Beam W6X25 - 25.0 lb/ft', weight_per_ft: 25.0, unit_price_per_cwt: 87.5, category: 'Wide Flange' },
    'W8X10': { shape_key: 'W8X10', description: 'Wide Flange Beam W8X10 - 10.0 lb/ft', weight_per_ft: 10.0, unit_price_per_cwt: 85.9, category: 'Wide Flange' },
    'W8X13': { shape_key: 'W8X13', description: 'Wide Flange Beam W8X13 - 13.0 lb/ft', weight_per_ft: 13.0, unit_price_per_cwt: 86.3, category: 'Wide Flange' },
    'W8X15': { shape_key: 'W8X15', description: 'Wide Flange Beam W8X15 - 15.0 lb/ft', weight_per_ft: 15.0, unit_price_per_cwt: 86.5, category: 'Wide Flange' },
    'W8X18': { shape_key: 'W8X18', description: 'Wide Flange Beam W8X18 - 18.0 lb/ft', weight_per_ft: 18.0, unit_price_per_cwt: 86.8, category: 'Wide Flange' },
    'W10X12': { shape_key: 'W10X12', description: 'Wide Flange Beam W10X12 - 12.0 lb/ft', weight_per_ft: 12.0, unit_price_per_cwt: 86.2, category: 'Wide Flange' },
    'W10X15': { shape_key: 'W10X15', description: 'Wide Flange Beam W10X15 - 15.0 lb/ft', weight_per_ft: 15.0, unit_price_per_cwt: 86.5, category: 'Wide Flange' },
    'W12X14': { shape_key: 'W12X14', description: 'Wide Flange Beam W12X14 - 14.0 lb/ft', weight_per_ft: 14.0, unit_price_per_cwt: 86.4, category: 'Wide Flange' },
    'W12X16': { shape_key: 'W12X16', description: 'Wide Flange Beam W12X16 - 16.0 lb/ft', weight_per_ft: 16.0, unit_price_per_cwt: 86.6, category: 'Wide Flange' },
    'W12X19': { shape_key: 'W12X19', description: 'Wide Flange Beam W12X19 - 19.0 lb/ft', weight_per_ft: 19.0, unit_price_per_cwt: 86.9, category: 'Wide Flange' },
    'W12X22': { shape_key: 'W12X22', description: 'Wide Flange Beam W12X22 - 22.0 lb/ft', weight_per_ft: 22.0, unit_price_per_cwt: 87.2, category: 'Wide Flange' },
    'W12X26': { shape_key: 'W12X26', description: 'Wide Flange Beam W12X26 - 26.0 lb/ft', weight_per_ft: 26.0, unit_price_per_cwt: 87.6, category: 'Wide Flange' },
    
    // Plates  
    'PL1/4': { shape_key: 'PL1/4', description: 'PLATE 1/4" THICK', weight_per_ft: 10.2, unit_price_per_cwt: 75, category: 'Plate' },
    'PL3/16': { shape_key: 'PL3/16', description: 'PLATE 3/16" THICK', weight_per_ft: 7.65, unit_price_per_cwt: 75, category: 'Plate' },
    'PL1/2': { shape_key: 'PL1/2', description: 'PLATE 1/2" THICK', weight_per_ft: 20.4, unit_price_per_cwt: 75, category: 'Plate' },
    'PL3/4': { shape_key: 'PL3/4', description: 'PLATE 3/4" THICK', weight_per_ft: 30.6, unit_price_per_cwt: 75, category: 'Plate' },
    'PL.250': { shape_key: 'PL.250', description: 'PLATE .250" THICK', weight_per_ft: 10.2, unit_price_per_cwt: 75, category: 'Plate' },
    'PL.500': { shape_key: 'PL.500', description: 'PLATE .500" THICK', weight_per_ft: 20.4, unit_price_per_cwt: 75, category: 'Plate' },
    'PL.750': { shape_key: 'PL.750', description: 'PLATE .750" THICK', weight_per_ft: 30.6, unit_price_per_cwt: 75, category: 'Plate' },
    
    // Channels
    'C6X8.2': { shape_key: 'C6X8.2', description: 'C6x8.2 CHANNEL', weight_per_ft: 8.2, unit_price_per_cwt: 90, category: 'Channel' },
    'C6X10.5': { shape_key: 'C6X10.5', description: 'C6x10.5 CHANNEL', weight_per_ft: 10.5, unit_price_per_cwt: 90, category: 'Channel' },
    
    // Angles  
    'L3X3X1/4': { shape_key: 'L3X3X1/4', description: 'L3x3x1/4 ANGLE', weight_per_ft: 4.9, unit_price_per_cwt: 95, category: 'Angle' },
    'L3X3X3/8': { shape_key: 'L3X3X3/8', description: 'L3x3x3/8 ANGLE', weight_per_ft: 7.2, unit_price_per_cwt: 95, category: 'Angle' },
  }), [])

  // Smart pattern matching for material suggestions - memoized for performance
  const getSmartSuggestions = useCallback((input: string): any[] => {
    const inputUpper = input.toUpperCase().trim()
    if (inputUpper.length < 2) return []
    
    const suggestions: any[] = []
    
    // Pattern matching for W-beams: "W6" should show W6X9, W6X12, etc.
    if (inputUpper.startsWith('W') && !inputUpper.includes('X')) {
      const sizeMatch = inputUpper.match(/^W(\d+)/)
      if (sizeMatch) {
        const size = sizeMatch[1]
        Object.values(commonMaterials).forEach(material => {
          if (material.shape_key.startsWith(`W${size}X`)) {
            suggestions.push(material)
          }
        })
      }
    }
    
    // Pattern matching for plates: "PL" should show common thicknesses
    else if (inputUpper === 'PL' || inputUpper === 'PLATE') {
      Object.values(commonMaterials).forEach(material => {
        if (material.shape_key.startsWith('PL')) {
          suggestions.push(material)
        }
      })
    }
    
    // Exact and prefix matching
    else {
      Object.values(commonMaterials).forEach(material => {
        if (material.shape_key.startsWith(inputUpper) || 
            material.description.includes(inputUpper)) {
          suggestions.push(material)
        }
      })
    }
    
    // Sort by relevance: exact match first, then by weight
    return suggestions.sort((a, b) => {
      if (a.shape_key === inputUpper) return -1
      if (b.shape_key === inputUpper) return 1
      if (a.shape_key.startsWith(inputUpper) && !b.shape_key.startsWith(inputUpper)) return -1
      if (b.shape_key.startsWith(inputUpper) && !a.shape_key.startsWith(inputUpper)) return 1
      return a.shape_key.localeCompare(b.shape_key)
    }).slice(0, 8)
  }, [commonMaterials])

  // Fast material validation with fallback
  const validateAndConfirmMaterial = useCallback(async (shapeKey: string) => {
    if (!shapeKey || shapeKey.length < 2) {
      setMaterialValidationState('none')
      setConfirmedMaterialData(null)
      return
    }

    const shapeKeyUpper = shapeKey.toUpperCase()
    
    // Check local materials first (instant validation)
    const localMaterial = commonMaterials[shapeKeyUpper as keyof typeof commonMaterials]
    if (localMaterial) {
      // Validated from local cache
      setMaterialValidationState('confirmed')
      setConfirmedMaterialData(localMaterial)
      
      // Auto-populate confirmed data
      setNewEntry(prev => ({
        ...prev,
        description: localMaterial.description,
        weight_per_ft: localMaterial.weight_per_ft,
        unit_price_per_cwt: localMaterial.unit_price_per_cwt,
      }))
      return
    }

    // Try API as fallback (with short timeout)
    setMaterialValidationState('pending')
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 1000) // 1 second timeout
      
      const response = await fetch(buildApiUrl(API_ENDPOINTS.TAKEOFF_MATERIALS_SEARCH, { q: shapeKey, limit: 10 }), {
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const materials = await response.json()
        const exactMatch = materials.find((m: any) => 
          m.shape_key.toUpperCase() === shapeKeyUpper
        )
        
        if (exactMatch) {
          // Validated from database
          setMaterialValidationState('confirmed')
          setConfirmedMaterialData(exactMatch)
          
          // Auto-populate and cache for future use
          setNewEntry(prev => ({
            ...prev,
            description: exactMatch.description,
            weight_per_ft: exactMatch.weight_per_ft,
            unit_price_per_cwt: exactMatch.unit_price_per_cwt,
          }))
          
          // Add to cache for next time
          setMaterialCache(prev => new Map(prev.set(shapeKeyUpper, exactMatch)))
        } else {
          // Custom material allowed
          setMaterialValidationState('unconfirmed')
          setConfirmedMaterialData(null)
        }
      } else {
        throw new Error(`API error: ${response.status}`)
      }
    } catch (error) {
      // API validation failed, allowing custom material
      // API failed - allow as custom material instead of blocking user
      setMaterialValidationState('unconfirmed')
      setConfirmedMaterialData(null)
    }
  }, [])

  // Real-time calculation function
  const calculateEntry = useCallback(async (entryData: Partial<TakeoffEntry>) => {
    if (!entryData.shape_key || !entryData.qty || entryData.qty <= 0 || !entryData.length_ft) {
      return null
    }

    setIsCalculating(true)
    try {
      const isPlateShape = isPlate(entryData.shape_key)
      
      // For plates: send width_in and thickness_in
      // For linear materials: no width needed (shape key contains all dimensions)
      const requestBody = {
        qty: entryData.qty,
        shape_key: entryData.shape_key,
        length_ft: entryData.length_ft,
        calculate_labor: true,
        labor_mode: laborMode,
        operations: entryData.operations || [],
        coatings_selected: entryData.coatings_selected || [],
        primary_coating: entryData.primary_coating || null,
        ...(isPlateShape ? {
          width_in: entryData.width_in || 0,
          length_in: entryData.length_in || 0,
          thickness_in: entryData.thickness_in || 0
        } : {})
      }
      
      const response = await fetch(buildApiUrl(API_ENDPOINTS.TAKEOFF_CALCULATE), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        throw new Error('Calculation failed')
      }

      const calculation = await response.json()
      return calculation
    } catch (error) {
      // Calculation error occurred
      return null
    } finally {
      setIsCalculating(false)
    }
  }, [laborMode])

  // Search materials for autocomplete with caching and debouncing
  const searchMaterials = useCallback(async (query: string) => {
    if (query.length < 2) {
      setMaterialSuggestions([])
      return
    }

    const queryKey = query.toUpperCase()
    
    // Check cache first
    if (searchCache.has(queryKey)) {
      setMaterialSuggestions(searchCache.get(queryKey) || [])
      return
    }

    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.TAKEOFF_MATERIALS_SEARCH, { q: query, limit: 8 }))
      if (response.ok) {
        const materials = await response.json()
        
        // Cache the results
        setSearchCache(prev => {
          const newCache = new Map(prev)
          // Simple LRU: if cache is too large, clear it
          if (newCache.size > 50) {
            newCache.clear()
          }
          newCache.set(queryKey, materials)
          return newCache
        })
        
        setMaterialSuggestions(materials)
      }
    } catch (error) {
      console.error('Material search error:', error)
    }
  }, [searchCache])

  // Search descriptions for independent autocomplete with debouncing
  const searchDescriptions = useCallback(async (query: string) => {
    if (query.length < 3) {
      setDescriptionSuggestions([])
      return
    }

    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.TAKEOFF_DESCRIPTIONS_SEARCH, { q: query, limit: 8 }))
      if (response.ok) {
        const descriptions = await response.json()
        setDescriptionSuggestions(descriptions)
      }
    } catch (error) {
      console.error('Description search error:', error)
    }
  }, [])

  // Debounced search function for materials
  const debouncedSearchMaterials = useCallback(
    debounce((query: string) => {
      searchMaterials(query)
    }, 250),
    [searchMaterials]
  )

  // Debounced validation function
  const debouncedValidateMaterial = useCallback(
    debounce((shapeKey: string) => {
      validateAndConfirmMaterial(shapeKey)
    }, 500), // Slightly longer delay for validation
    [validateAndConfirmMaterial]
  )

  // Handle shape key input with smart pattern matching and validation
  const handleShapeKeyChange = (value: string) => {
    setNewEntry({ ...newEntry, shape_key: value })
    setIsCurrentShapePlate(isPlate(value))
    
    // Reset validation state when user starts typing
    if (materialValidationState !== 'pending') {
      setMaterialValidationState('none')
      setConfirmedMaterialData(null)
    }
    
    if (value.length >= 2) {
      // Use smart pattern matching for instant suggestions
      const smartSuggestions = getSmartSuggestions(value)
      setMaterialSuggestions(smartSuggestions)
      
      // Also do API search as fallback for materials not in local cache
      if (smartSuggestions.length === 0) {
        debouncedSearchMaterials(value)
      }
      
      debouncedValidateMaterial(value) // Keep validation
      setShowSuggestions(true)
    } else {
      setMaterialSuggestions([])
      setShowSuggestions(false)
    }
  }

  // Debounced search function for descriptions
  const debouncedSearchDescriptions = useCallback(
    debounce((query: string) => {
      searchDescriptions(query)
    }, 300),
    [searchDescriptions]
  )

  // Handle description input with debounced autocomplete
  const handleDescriptionChange = (value: string) => {
    setNewEntry({ ...newEntry, description: value })
    if (value.length >= 3) {
      debouncedSearchDescriptions(value)
      setShowDescriptionSuggestions(true)
    } else {
      setDescriptionSuggestions([])
      setShowDescriptionSuggestions(false)
    }
  }

  // Select material from suggestions - immediately confirm
  const selectMaterial = (material: any) => {
    setNewEntry({
      ...newEntry,
      shape_key: material.shape_key,
      description: material.description,
      weight_per_ft: material.weight_per_ft,
      unit_price_per_cwt: material.unit_price_per_cwt,
    })
    setIsCurrentShapePlate(isPlate(material.shape_key))
    
    // Immediately confirm the material since it's from our database
    setMaterialValidationState('confirmed')
    setConfirmedMaterialData(material)
    
    setShowSuggestions(false)
    setMaterialSuggestions([])
  }

  // Select description from suggestions
  const selectDescription = (description: string) => {
    setNewEntry({
      ...newEntry,
      description: description
    })
    setShowDescriptionSuggestions(false)
    setDescriptionSuggestions([])
  }

  // Handle operations checkbox changes
  const toggleOperation = (operation: Operation) => {
    const currentOperations = newEntry.operations || []
    const updatedOperations = currentOperations.includes(operation)
      ? currentOperations.filter(op => op !== operation)
      : [...currentOperations, operation]
    
    setNewEntry({
      ...newEntry,
      operations: updatedOperations
    })
  }

  // Handle coatings checkbox changes
  const toggleCoating = (coating: CoatingSystem) => {
    const currentCoatings = newEntry.coatings_selected || []
    const updatedCoatings = currentCoatings.includes(coating)
      ? currentCoatings.filter(c => c !== coating)
      : [...currentCoatings, coating]
    
    setNewEntry({
      ...newEntry,
      coatings_selected: updatedCoatings
    })
  }

  // Add new entry with calculation - optimized for speed
  const addEntry = async () => {
    // Quick validation before expensive calculation
    if (!newEntry.shape_key?.trim() || !newEntry.qty || newEntry.qty <= 0 || !newEntry.length_ft) {
      return
    }

    // Show warning for unconfirmed shapes but allow saving
    if (materialValidationState === 'unconfirmed') {
      console.warn(`Adding unconfirmed shape: ${newEntry.shape_key}`)
    }

    setIsCalculating(true)
    try {
      const calculation = await calculateEntry(newEntry)
      if (!calculation) return

      const entry: TakeoffEntry = {
        id: Date.now().toString(),
        qty: newEntry.qty || 1,
        shape_key: newEntry.shape_key || '',
        description: newEntry.description || calculation.description,
        length_ft: newEntry.length_ft || 0,
        length_in: newEntry.length_in || 0,
        width_in: newEntry.width_in || 0,
        thickness_in: newEntry.thickness_in || 0,
        weight_per_ft: calculation.weight_per_ft,
        total_length_ft: calculation.total_length_ft,
        total_weight_lbs: calculation.total_weight_lbs,
        total_weight_tons: calculation.total_weight_tons,
        unit_price_per_cwt: calculation.unit_price_per_cwt,
        total_price: calculation.total_price,
        // Always use manual labor inputs (manual mode only)
        labor_hours: newEntry.labor_hours || 0,
        labor_cost: newEntry.labor_cost || 0,
        operations: newEntry.operations || [],
        coatings_selected: newEntry.coatings_selected || [],
        primary_coating: newEntry.primary_coating || '',
        coating_cost: calculation.coating_cost || 0,
        notes: newEntry.notes || '',
      }

      setEntries([...entries, entry])
      
      // Reset form quickly
      setNewEntry({
        qty: undefined, // Start empty
        shape_key: '',
        description: '',
        length_ft: 0,
        length_in: 0,
        width_in: 0,
        thickness_in: 0,
        labor_hours: 0,
        labor_cost: 0,
        operations: [],
        coatings_selected: [],
        primary_coating: '',
        notes: '',
      })
      setIsCurrentShapePlate(false)
      setMaterialSuggestions([])
      
      // Reset validation state
      setMaterialValidationState('none')
      setConfirmedMaterialData(null)
      setDescriptionSuggestions([])
      setShowSuggestions(false)
      setShowDescriptionSuggestions(false)
      
      // Focus back to qty field for quick next entry (proper tab order)
      setTimeout(() => {
        const qtyInput = document.getElementById('qty-input') as HTMLInputElement
        if (qtyInput) qtyInput.focus()
      }, 100)
      
    } finally {
      setIsCalculating(false)
    }
  }

  // Update entry with recalculation
  const updateEntry = async (index: number, field: keyof TakeoffEntry, value: any) => {
    const updatedEntries = [...entries]
    updatedEntries[index] = { ...updatedEntries[index], [field]: value }

    // Recalculate if key fields changed
    if (['qty', 'shape_key', 'length_ft', 'length_in', 'width_in', 'thickness_in'].includes(field)) {
      const calculation = await calculateEntry(updatedEntries[index])
      if (calculation) {
        updatedEntries[index] = {
          ...updatedEntries[index],
          description: calculation.description,
          weight_per_ft: calculation.weight_per_ft,
          total_length_ft: calculation.total_length_ft,
          total_weight_lbs: calculation.total_weight_lbs,
          total_weight_tons: calculation.total_weight_tons,
          unit_price_per_cwt: calculation.unit_price_per_cwt,
          total_price: calculation.total_price,
          labor_hours: calculation.labor_hours,
          labor_cost: calculation.labor_cost,
        }
      }
    }

    setEntries(updatedEntries)
  }

  // Remove entry
  const removeEntry = (index: number) => {
    setEntries(entries.filter((_, i) => i !== index))
  }

  // Duplicate entry
  const duplicateEntry = (index: number) => {
    const originalEntry = entries[index]
    const duplicatedEntry = {
      ...originalEntry,
      id: Date.now().toString(),
    }
    setEntries([...entries, duplicatedEntry])
  }

  // Simple project save - ONE API call, no loops, no chaos
  const saveProject = useCallback(async () => {
    if (!projectId) return
    if (entries.length === 0) {
      console.log('⚠️ No entries to save')
      return
    }

    // Prevent concurrent saves
    if (isSaving) {
      console.log('⏳ Save already in progress, skipping...')
      return
    }

    setIsSaving(true)
    console.log(`💾 Saving project with ${entries.length} entries in ONE API call...`)
    
    try {
      // Convert entries to the format the backend expects
      const entriesData = entries.map(entry => ({
        qty: entry.qty,
        shape_key: entry.shape_key,
        description: entry.description,
        length_ft: entry.length_ft,
        width_ft: (entry.width_in || 0) / 12, // Convert inches to feet
        thickness_in: entry.thickness_in || 0,
        weight_per_ft: entry.weight_per_ft || 0,
        total_length_ft: entry.total_length_ft || 0,
        total_weight_lbs: entry.total_weight_lbs || 0,
        total_weight_tons: entry.total_weight_tons || 0,
        unit_price_per_cwt: entry.unit_price_per_cwt || 0,
        total_price: entry.total_price || 0,
        labor_hours: entry.labor_hours || 0,
        labor_rate: entry.labor_rate || 0,
        labor_cost: entry.labor_cost || 0,
        labor_mode: 'manual',
        operations: entry.operations || [],
        coatings_selected: entry.coatings_selected || [],
        primary_coating: entry.primary_coating || '',
        coating_cost: entry.coating_cost || 0,
        notes: entry.notes || ''
      }))

      // Single API call to save entire project
      const response = await fetch(buildApiUrl(`${API_ENDPOINTS.TAKEOFF_SAVE}/${projectId}/save`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entries: entriesData })
      })

      if (response.ok) {
        const result = await response.json()
        setLastSaved(new Date())
        console.log(`✅ Project saved successfully! Deleted ${result.entries_deleted}, created ${result.entries_created}`)
      } else {
        const errorText = await response.text()
        throw new Error(`Save failed: ${response.status} - ${errorText}`)
      }

    } catch (error) {
      console.error('❌ Error saving project:', error)
      alert(`Save failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsSaving(false)
    }
  }, [projectId, laborMode]) // Remove entries and isSaving to prevent infinite re-renders

  // Calculate totals
  useEffect(() => {
    const totals = entries.reduce(
      (acc, entry) => ({
        total_weight_tons: acc.total_weight_tons + entry.total_weight_tons,
        total_price: acc.total_price + entry.total_price,
        total_length_ft: acc.total_length_ft + entry.total_length_ft,
        total_labor_hours: acc.total_labor_hours + (entry.labor_hours || 0),
        total_labor_cost: acc.total_labor_cost + (entry.labor_cost || 0),
      }),
      { 
        total_weight_tons: 0, 
        total_price: 0, 
        total_length_ft: 0,
        total_labor_hours: 0,
        total_labor_cost: 0
      }
    )

    if (onTotalsChange) {
      onTotalsChange(totals)
    }
  }, [entries, onTotalsChange])


  // Load existing takeoff entries when project opens - with retry logic
  useEffect(() => {
    const loadProjectEntries = async (retryCount = 0) => {
      if (!projectId) return
      
      setIsLoadingEntries(true)
      setLoadError(null)
      
      try {
        console.log(`📖 Loading entries for project ${projectId}${retryCount > 0 ? ` (retry ${retryCount})` : ''}...`)
        
        const response = await fetch(buildApiUrl(`${API_ENDPOINTS.TAKEOFF_SAVE}/${projectId}/entries`))
        if (response.ok) {
          const existingEntries = await response.json()
          setEntries(existingEntries)
          console.log(`✅ Loaded ${existingEntries.length} existing entries`)
          setLoadError(null)
        } else if (response.status === 404) {
          // Project exists but no entries yet - this is normal
          console.log('📝 No existing entries found - starting fresh')
          setEntries([])
          setLoadError(null)
        } else {
          throw new Error(`Failed to load takeoff entries: ${response.status}`)
        }
      } catch (error) {
        console.error('❌ Error loading takeoff entries:', error)
        
        // Retry logic for network errors
        if (retryCount < 2 && error instanceof TypeError) {
          console.log(`🔄 Retrying load (attempt ${retryCount + 1}/3)...`)
          setTimeout(() => loadProjectEntries(retryCount + 1), 1000 * (retryCount + 1))
          return
        }
        
        setLoadError(`Failed to load existing entries: ${error instanceof Error ? error.message : 'Unknown error'}`)
        // Start with empty entries to allow user to work
        setEntries([])
      } finally {
        setIsLoadingEntries(false)
      }
    }

    loadProjectEntries()
  }, [projectId])

  // No auto-save - user controls when to save manually

  // Expose save function to parent component
  useEffect(() => {
    if (onSaveFunctionReady) {
      onSaveFunctionReady(saveProject)
    }
  }, [onSaveFunctionReady]) // Remove saveProject from dependencies to prevent infinite loop

  // Enhanced keyboard shortcuts for faster entry and navigation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ctrl+Enter or Cmd+Enter to add entry quickly
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault()
        if (!isCalculating && newEntry.shape_key && newEntry.qty && newEntry.length_ft) {
          addEntry()
        }
      }
      // Ctrl+S to save project
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (entries.length > 0 && !isSaving) {
          saveProject()
        }
      }
      // F2 to focus qty field for quick entry
      if (e.key === 'F2') {
        e.preventDefault()
        const qtyInput = document.getElementById('qty-input') as HTMLInputElement
        if (qtyInput) qtyInput.focus()
      }
      // Escape to clear current entry
      if (e.key === 'Escape') {
        e.preventDefault()
        setNewEntry({
          qty: undefined,
          shape_key: '',
          description: '',
          length_ft: 0,
          width_in: 0,
          thickness_in: 0,
          labor_hours: 0,
          labor_cost: 0,
          operations: [],
          coatings_selected: [],
          primary_coating: '',
        })
        setMaterialValidationState('none')
        setConfirmedMaterialData(null)
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [addEntry, saveProject, isCalculating, isSaving, newEntry, entries.length])

  return (
    <div className="flex flex-col h-full">
      {/* Quick Entry Panel */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-4">
        <h3 className="text-2xl font-semibold text-white mb-4">
          Quick Entry
          <span className="ml-2 text-lg text-yellow-400">(Manual Labor)</span>
        </h3>
        <div className="space-y-4">
        <div className={`grid gap-3 ${isCurrentShapePlate ? 'grid-cols-8' : 'grid-cols-6'}`}>
          <div>
            <label className="block text-lg font-medium text-gray-300 mb-1">Qty</label>
            <input
              type="number"
              value={newEntry.qty || ''}
              onChange={(e) => setNewEntry({ ...newEntry, qty: Number(e.target.value) })}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder=""
              min="1"
              tabIndex={1}
              id="qty-input"
            />
          </div>

          <div className="relative">
            <label className="block text-lg font-medium text-gray-300 mb-1 flex items-center gap-2">
              Shape
              {materialValidationState === 'pending' && <Loader className="w-4 h-4 animate-spin text-yellow-500" />}
              {materialValidationState === 'confirmed' && <CheckCircle className="w-4 h-4 text-green-500" />}
              {materialValidationState === 'unconfirmed' && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
            </label>
            <input
              type="text"
              value={newEntry.shape_key || ''}
              onChange={(e) => handleShapeKeyChange(e.target.value)}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              className={`w-full px-4 py-3 bg-gray-700 border rounded text-xl text-white focus:outline-none focus:ring-2 ${
                materialValidationState === 'confirmed' 
                  ? 'border-green-500 focus:ring-green-500' 
                  : materialValidationState === 'unconfirmed'
                  ? 'border-yellow-500 focus:ring-yellow-500'
                  : 'border-gray-600 focus:ring-blue-500'
              }`}
              placeholder="W12X26"
              tabIndex={2}
              id="shape-input"
            />
            
            {/* Material Suggestions Dropdown */}
            {showSuggestions && materialSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-lg shadow-lg max-h-48 overflow-auto">
                {materialSuggestions.map((material, index) => (
                  <button
                    key={index}
                    onClick={() => selectMaterial(material)}
                    className="w-full text-left px-4 py-3 hover:bg-gray-600 text-white text-lg"
                  >
                    <div className="font-medium text-lg">{material.shape_key}</div>
                    <div className="text-gray-400 text-base">{material.description}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="relative">
            <label className="block text-lg font-medium text-gray-300 mb-1">
              Description {materialValidationState === 'confirmed' && '🔒'}
            </label>
            <input
              type="text"
              value={newEntry.description || ''}
              onChange={(e) => materialValidationState === 'confirmed' ? null : handleDescriptionChange(e.target.value)}
              onBlur={() => setTimeout(() => setShowDescriptionSuggestions(false), 150)}
              readOnly={materialValidationState === 'confirmed'}
              className={`w-full px-4 py-3 border border-gray-600 rounded text-xl text-white focus:outline-none ${
                materialValidationState === 'confirmed' 
                  ? 'bg-gray-600 cursor-not-allowed focus:ring-gray-500' 
                  : 'bg-gray-700 focus:ring-2 focus:ring-blue-500'
              }`}
              placeholder={materialValidationState === 'confirmed' ? 'Auto-filled from database' : 'Type to search descriptions...'}
              tabIndex={3}
              id="description-input"
            />
            
            {showDescriptionSuggestions && descriptionSuggestions.length > 0 && materialValidationState !== 'confirmed' && (
              <div className="absolute z-10 mt-1 w-full bg-gray-800 border border-gray-600 rounded max-h-48 overflow-y-auto">
                {descriptionSuggestions.map((description, index) => (
                  <button
                    key={index}
                    onClick={() => selectDescription(description)}
                    className="w-full text-left px-3 py-2 hover:bg-gray-600 text-white text-sm border-b border-gray-700 last:border-b-0"
                  >
                    <div className="truncate">{description}</div>
                  </button>
                ))}
              </div>
            )}
            
            {/* Validation Status Message */}
            {materialValidationState !== 'none' && newEntry.shape_key && (
              <div className="mt-2 text-sm">
                {materialValidationState === 'pending' && (
                  <div className="flex items-center gap-2 text-yellow-500">
                    <Loader className="w-3 h-3 animate-spin" />
                    Validating shape...
                  </div>
                )}
                {materialValidationState === 'confirmed' && (
                  <div className="flex items-center gap-2 text-green-500">
                    <CheckCircle className="w-3 h-3" />
                    Shape confirmed from database
                  </div>
                )}
                {materialValidationState === 'unconfirmed' && (
                  <div className="flex items-center gap-2 text-yellow-500">
                    <AlertTriangle className="w-3 h-3" />
                    Custom shape - not in database
                  </div>
                )}
              </div>
            )}
          </div>

          {/* For plates: Width(in), Length(Ft), Length(IN) */}
          {isCurrentShapePlate ? (
            <>
              <div>
                <label className="block text-lg font-medium text-gray-300 mb-1">Width (in)</label>
                <input
                  type="number"
                  step="0.125"
                  value={newEntry.width_in || ''}
                  onChange={(e) => setNewEntry({ ...newEntry, width_in: Number(e.target.value) })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Width in inches"
                  tabIndex={4}
                  id="width-input"
                />
              </div>
              
              <div>
                <label className="block text-lg font-medium text-gray-300 mb-1">Length (Ft)</label>
                <input
                  type="number"
                  step="0.1"
                  value={newEntry.length_ft || ''}
                  onChange={(e) => setNewEntry({ ...newEntry, length_ft: Number(e.target.value) })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.0"
                  tabIndex={5}
                  id="length-ft-input"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-1">Length (IN)</label>
                <input
                  type="number"
                  step="0.125"
                  value={newEntry.length_in || ''}
                  onChange={(e) => setNewEntry({ ...newEntry, length_in: Number(e.target.value) })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Length in inches"
                  tabIndex={6}
                  id="length-in-input"
                />
              </div>
            </>
          ) : (
            /* For non-plates: just Length (ft) */
            <div>
              <label className="block text-lg font-medium text-gray-300 mb-1">Length (ft)</label>
              <input
                type="number"
                step="0.1"
                value={newEntry.length_ft || ''}
                onChange={(e) => setNewEntry({ ...newEntry, length_ft: Number(e.target.value) })}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.0"
                tabIndex={4}
                id="length-input"
              />
            </div>
          )}


          {/* Labor Fields - Manual Mode */}
          <div>
            <label className="block text-lg font-medium text-gray-300 mb-1">Labor Hrs</label>
                <input
                  type="number"
                  step="0.1"
                  value={newEntry.labor_hours || ''}
                  onChange={(e) => setNewEntry({ ...newEntry, labor_hours: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="0.0"
                  tabIndex={isCurrentShapePlate ? 7 : 5}
                  id="labor-hours-input"
                />
              </div>

              <div>
                <label className="block text-lg font-medium text-gray-300 mb-1">Labor $</label>
                <input
                  type="number"
                  step="0.01"
                  value={newEntry.labor_cost || ''}
                  onChange={(e) => setNewEntry({ ...newEntry, labor_cost: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="0.00"
                  tabIndex={isCurrentShapePlate ? 8 : 6}
                  id="labor-cost-input"
                />
          </div>

          {/* Notes Field */}
          <div>
            <label className="block text-lg font-medium text-gray-300 mb-1">Notes</label>
            <textarea
              value={newEntry.notes || ''}
              onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded text-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
              placeholder="Optional notes for this entry..."
              rows={2}
              tabIndex={isCurrentShapePlate ? 9 : 7}
              id="notes-input"
            />
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={addEntry}
              disabled={isCalculating || !newEntry.shape_key || !newEntry.qty || !newEntry.length_ft}
              className={`flex-1 flex items-center justify-center gap-2 text-white px-6 py-3 text-xl rounded transition-colors ${
                materialValidationState === 'confirmed'
                  ? 'bg-green-600 hover:bg-green-700 disabled:bg-green-800'
                  : materialValidationState === 'unconfirmed'
                  ? 'bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-800'
                  : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800'
              } disabled:opacity-50`}
              tabIndex={isCurrentShapePlate ? 9 : 7}
              id="add-button"
            >
              {isCalculating ? (
                <Calculator className="w-4 h-4 animate-spin" />
              ) : materialValidationState === 'confirmed' ? (
                <CheckCircle className="w-4 h-4" />
              ) : materialValidationState === 'unconfirmed' ? (
                <AlertTriangle className="w-4 h-4" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              {isCalculating ? 'Calculating...' : 
               materialValidationState === 'confirmed' ? 'Add ✓' :
               materialValidationState === 'unconfirmed' ? 'Add ⚠' :
               'Add'}
            </button>
            
            {/* Save status and manual save button */}
            <div className="flex items-center gap-3">
              {/* Save status */}
              <div className="flex items-center gap-2 text-sm">
                {isSaving ? (
                  <div className="flex items-center gap-2 text-blue-400">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-400"></div>
                    Saving...
                  </div>
                ) : lastSaved ? (
                  <div className="flex items-center gap-2 text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Saved {lastSaved.toLocaleTimeString()}
                  </div>
                ) : entries.length > 0 ? (
                  <div className="flex items-center gap-2 text-yellow-400">
                    <AlertTriangle className="w-3 h-3" />
                    Unsaved changes
                  </div>
                ) : null}
              </div>
              
              {/* Simple project save button */}
              {entries.length > 0 && (
                <button
                  onClick={saveProject}
                  disabled={isSaving}
                  className="flex items-center gap-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded transition-colors"
                  title="Save project with one API call"
                >
                  {isSaving ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  {isSaving ? 'Saving...' : 'Save Project'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Operations Checkboxes */}
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-lg font-medium text-gray-300 mb-3">Labor Operations</h4>
          <div className="grid grid-cols-3 gap-2">
            {Object.values(Operation).map((operation) => (
              <label key={operation} className="flex items-center space-x-2 text-lg">
                <input
                  type="checkbox"
                  checked={(newEntry.operations || []).includes(operation)}
                  onChange={() => toggleOperation(operation)}
                  className="rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500 focus:ring-2"
                />
                <span className="text-lg text-gray-300">
                  {operation} <span className="text-sm text-blue-300">(${LABOR_OPERATION_RATES[operation].rate.toFixed(2)}{LABOR_OPERATION_RATES[operation].unit})</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Coatings Checkboxes */}
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-lg font-medium text-gray-300 mb-3">Coating Systems</h4>
          <div className="grid grid-cols-3 gap-2">
            {Object.values(CoatingSystem).map((coating) => (
              <label key={coating} className="flex items-center space-x-2 text-lg">
                <input
                  type="checkbox"
                  checked={(newEntry.coatings_selected || []).includes(coating)}
                  onChange={() => toggleCoating(coating)}
                  className="rounded border-gray-600 bg-gray-700 text-green-600 focus:ring-green-500 focus:ring-2"
                />
                <span className="text-lg text-gray-300">
                  {coating} {COATING_SYSTEM_RATES[coating].rate > 0 && 
                    <span className="text-sm text-green-300">(${COATING_SYSTEM_RATES[coating].rate.toFixed(2)} {COATING_SYSTEM_RATES[coating].unit})</span>
                  }
                </span>
              </label>
            ))}
          </div>
        </div>
        </div>
      </div>

      {/* Takeoff Table */}
      <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg overflow-hidden flex flex-col">
        <div className="bg-gray-700 border-b border-gray-600 px-4 py-3">
          <h3 className="text-2xl font-semibold text-white">
            Takeoff Entries ({entries.length})
            {isCalculating && (
              <span className="ml-2 text-lg text-blue-400">
                <Calculator className="w-4 h-4 inline animate-spin mr-1" />
                Calculating...
              </span>
            )}
          </h3>
        </div>
        
        <div className="flex-1 overflow-auto">
          <table className="w-full text-lg">
            <thead className="bg-gray-700 sticky top-0">
              <tr>
                <th className="text-left p-4 text-xl text-gray-300 min-w-16">Qty</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Shape</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-40">Description</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Width (in)</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Length (Ft)</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Length (IN)</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Wt/Ft</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Total Length</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Total Lbs</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Total Tons</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Price/CWT</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Total Price</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Labor Hrs</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-24">Labor Cost</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-40">Notes</th>
                <th className="text-left p-4 text-xl text-gray-300 min-w-20">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoadingEntries ? (
                <tr>
                  <td colSpan={14} className="p-8 text-center">
                    <div className="flex items-center justify-center gap-3 text-gray-400">
                      <Loader className="w-6 h-6 animate-spin" />
                      <span className="text-xl">Loading takeoff entries...</span>
                    </div>
                  </td>
                </tr>
              ) : loadError ? (
                <tr>
                  <td colSpan={14} className="p-8 text-center">
                    <div className="flex items-center justify-center gap-3 text-red-400">
                      <AlertTriangle className="w-6 h-6" />
                      <span className="text-xl">{loadError}</span>
                    </div>
                  </td>
                </tr>
              ) : (
                entries.map((entry, index) => (
                <tr key={entry.id} className="border-b border-gray-700 hover:bg-gray-750">
                  <td className="p-4">
                    <input
                      type="number"
                      value={entry.qty}
                      onChange={(e) => updateEntry(index, 'qty', Number(e.target.value))}
                      className="w-full bg-transparent text-xl text-white text-center"
                      min="1"
                    />
                  </td>
                  <td className="p-4">
                    <input
                      type="text"
                      value={entry.shape_key}
                      onChange={(e) => updateEntry(index, 'shape_key', e.target.value)}
                      className="w-full bg-transparent text-xl text-white font-medium"
                    />
                  </td>
                  <td className="p-3 text-xl text-gray-300">{entry.description}</td>
                  {/* Width (in) - Only for plates */}
                  <td className="p-4">
                    {isPlate(entry.shape_key) ? (
                      <input
                        type="number"
                        step="0.125"
                        value={entry.width_in || 0}
                        onChange={(e) => updateEntry(index, 'width_in', Number(e.target.value))}
                        className="w-full bg-transparent text-xl text-white text-center"
                        placeholder="in"
                      />
                    ) : (
                      <span className="text-xl text-gray-500">-</span>
                    )}
                  </td>
                  
                  {/* Length (Ft) */}
                  <td className="p-4">
                    <input
                      type="number"
                      step="0.1"
                      value={entry.length_ft}
                      onChange={(e) => updateEntry(index, 'length_ft', Number(e.target.value))}
                      className="w-full bg-transparent text-xl text-white text-center"
                    />
                  </td>
                  
                  {/* Length (IN) - Only for plates */}
                  <td className="p-4">
                    {isPlate(entry.shape_key) ? (
                      <input
                        type="number"
                        step="0.125"
                        value={entry.length_in || 0}
                        onChange={(e) => updateEntry(index, 'length_in', Number(e.target.value))}
                        className="w-full bg-transparent text-xl text-white text-center"
                        placeholder="in"
                      />
                    ) : (
                      <span className="text-xl text-gray-500">-</span>
                    )}
                  </td>
                  <td className="p-3 text-white">{entry.weight_per_ft.toFixed(1)}</td>
                  <td className="p-3 text-white">{entry.total_length_ft.toFixed(1)}</td>
                  <td className="p-3 text-white">{entry.total_weight_lbs.toFixed(0)}</td>
                  <td className="p-3 text-white font-medium">{entry.total_weight_tons.toFixed(2)}</td>
                  <td className="p-3 text-green-400">${entry.unit_price_per_cwt.toFixed(2)}</td>
                  <td className="p-3 text-green-400 font-medium">${entry.total_price.toFixed(2)}</td>
                  <td className="p-4">
                    <input
                      type="number"
                      step="0.1"
                      value={entry.labor_hours || 0}
                      onChange={(e) => updateEntry(index, 'labor_hours', Number(e.target.value))}
                      className="w-full bg-transparent text-xl text-yellow-400 text-center"
                      placeholder="0.0"
                    />
                  </td>
                  <td className="p-4">
                    <input
                      type="number"
                      step="0.01"
                      value={entry.labor_cost || 0}
                      onChange={(e) => updateEntry(index, 'labor_cost', Number(e.target.value))}
                      className="w-full bg-transparent text-xl text-yellow-400 text-center"
                      placeholder="0.00"
                    />
                  </td>
                  <td className="p-4">
                    <span className="text-lg text-gray-300 truncate max-w-40" title={entry.notes || ''}>
                      {entry.notes || '-'}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => duplicateEntry(index)}
                        className="p-1 text-blue-400 hover:text-blue-300 hover:bg-blue-900 rounded"
                        title="Duplicate"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => removeEntry(index)}
                        className="p-1 text-red-400 hover:text-red-300 hover:bg-red-900 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
              )}
            </tbody>
          </table>

          {entries.length === 0 && !isLoadingEntries && !loadError && (
            <div className="flex flex-col items-center justify-center h-32 text-gray-400">
              <Calculator className="w-12 h-12 mb-2" />
              <p className="text-xl">No takeoff entries yet</p>
              <p className="text-lg">Use the quick entry panel to add materials</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

export default TakeoffGrid