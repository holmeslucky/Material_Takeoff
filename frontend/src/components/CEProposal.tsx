import React, { useState, useEffect } from 'react'
import { 
  FileText, 
  DollarSign, 
  Package, 
  Download, 
  Edit, 
  Save, 
  Calculator,
  Scissors,
  BarChart3,
  AlertCircle,
  CheckCircle,
  Printer,
  Mail,
  Settings
} from 'lucide-react'

interface CEProposalProps {
  projectId: string
  projectName: string
  onProposalGenerated?: (proposal: any) => void
}

interface MaterialPrice {
  shape_key: string
  description: string
  category: string
  price_per_lb: number
  price_per_ft: number
  total_qty: number
  total_weight_lbs: number
  total_cost: number
  is_edited: boolean
}

interface NestingOptimization {
  material_purchases: MaterialPurchase[]
  total_waste_percentage: number
  total_cost: number
  cost_savings: number
  optimization_summary: string
}

interface MaterialPurchase {
  shape_key: string
  size_description: string
  pieces_needed: number
  total_cost: number
  waste_percentage: number
  waste_cost: number
  cuts_count: number
}

interface ProposalData {
  proposal_content: string
  project_info: any
  totals: {
    material_cost: number
    labor_cost: number
    markup_percentage: number
    material_with_markup: number
    labor_with_markup: number
    total_cost: number
    total_weight_tons: number
    total_entries: number
  }
  generated_at: string
  template_type: string
}

export default function CEProposal({ 
  projectId, 
  projectName, 
  onProposalGenerated 
}: CEProposalProps) {
  const [activeTab, setActiveTab] = useState<'pricing' | 'nesting' | 'summary' | 'proposal'>('pricing')
  const [materialPrices, setMaterialPrices] = useState<MaterialPrice[]>([])
  const [nestingData, setNestingData] = useState<NestingOptimization | null>(null)
  const [proposalData, setProposalData] = useState<ProposalData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [markupPercentage, setMarkupPercentage] = useState(35)
  const [includeLabor, setIncludeLabor] = useState(true)
  const [templateType, setTemplateType] = useState('standard')
  const [editingPrices, setEditingPrices] = useState(false)
  const [hasUnsavedPrices, setHasUnsavedPrices] = useState(false)
  const [bulkPercentage, setBulkPercentage] = useState<string>('')
  const [bulkBasePrice, setBulkBasePrice] = useState<string>('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [editingNesting, setEditingNesting] = useState(false)
  const [hasUnsavedNesting, setHasUnsavedNesting] = useState(false)
  const [isSavingNesting, setIsSavingNesting] = useState(false)
  const [nestingSaveStatus, setNestingSaveStatus] = useState<'saved' | 'error' | null>(null)
  const [autoOptimizeOnPriceChange, setAutoOptimizeOnPriceChange] = useState(true)
  const [workflowStep, setWorkflowStep] = useState<'pricing' | 'nesting' | 'summary' | 'proposal' | 'complete'>('pricing')
  
  // Bid Summary state
  const [bidSummaryData, setBidSummaryData] = useState(null)
  const [indirectExpenses, setIndirectExpenses] = useState({
    consumables_percentage: 6.0,
    misc_percentage: 1.0,
    fuel_surcharge_percentage: 1.3,
    total_indirect_percentage: 8.3,
    custom_categories: []
  })

  const tabConfig = [
    {
      id: 'pricing',
      name: 'Material Pricing',
      description: 'Review and confirm material prices',
      icon: DollarSign,
      color: 'bg-green-600'
    },
    {
      id: 'nesting',
      name: 'Material Optimization',
      description: 'View nesting and waste analysis',
      icon: Scissors,
      color: 'bg-blue-600'
    },
    {
      id: 'summary',
      name: 'Bid Summary',
      description: 'Review costs and indirect expenses',
      icon: Calculator,
      color: 'bg-orange-600'
    },
    {
      id: 'proposal',
      name: 'PDF Generation',
      description: 'Generate professional proposal PDF',
      icon: FileText,
      color: 'bg-purple-600'
    }
  ]

  // Load initial material data from takeoff entries
  useEffect(() => {
    loadMaterialPrices()
    loadSavedNestingResults()
    loadIndirectExpenses()
  }, [projectId])

  const loadSavedNestingResults = async () => {
    try {
      const response = await fetch(`http://localhost:7000/api/v1/nesting/results/${projectId}`)
      
      if (response.ok) {
        const result = await response.json()
        
        if (result.has_saved_results) {
          console.log('📁 Loaded saved nesting results:', result)
          setNestingData({
            project_id: result.project_id,
            material_purchases: result.material_purchases || [],
            total_waste_percentage: result.total_waste_percentage || 0,
            total_cost: result.total_cost || 0,
            cost_savings: result.cost_savings || 0,
            optimization_summary: result.optimization_summary || '',
            recommendations: result.recommendations || []
          })
          setNestingSaveStatus('saved')
        } else {
          console.log('📁 No saved nesting results found for this project')
        }
      }
    } catch (error) {
      console.error('❌ Failed to load saved nesting results:', error)
      // Don't show error to user since this is optional background loading
    }
  }

  const loadMaterialPrices = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:7000/api/v1/proposals/material-prices/${projectId}`)
      if (response.ok) {
        const data = await response.json()
        setMaterialPrices(data.material_prices || [])
      } else {
        throw new Error('Failed to load material prices')
      }
    } catch (error) {
      console.error('Failed to load material prices:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const runNestingOptimization = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:7000/api/v1/nesting/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          include_waste_costs: true,
          optimization_level: 'standard'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setNestingData(result)
        setEditingNesting(false)
        setHasUnsavedNesting(false)
        
        // Auto-switch to nesting tab if optimization shows significant savings
        if (result.cost_savings > 100 && activeTab !== 'nesting') {
          setTimeout(() => {
            const shouldSwitch = window.confirm(
              `Nesting optimization found $${result.cost_savings.toFixed(0)} in potential savings! ` +
              'Would you like to review the nesting recommendations?'
            )
            if (shouldSwitch) {
              setActiveTab('nesting')
            }
          }, 1000)
        }
      } else {
        throw new Error('Nesting optimization failed')
      }
    } catch (error) {
      console.error('Nesting optimization error:', error)
      alert('Nesting optimization failed. Please check your project data and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const generateFinalProposal = async () => {
    // Must have nesting optimization completed first
    if (!nestingData || !nestingData.total_cost) {
      alert('Please run nesting optimization first to generate an accurate final proposal.')
      return
    }
    
    setIsLoading(true)
    try {
      const proposalPayload = {
        project_id: projectId,
        nesting_cost: nestingData.total_cost,
        material_markup: 35.0,
        coating_markup: 35.0,
        labor_rate: 120.0
      }
      
      const response = await fetch('http://localhost:7000/api/v1/proposals/generate-final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proposalPayload)
      })
      
      if (response.ok) {
        const result = await response.json()
        const newProposalData = {
          proposal_content: result.summary,
          project_info: { id: projectId, name: projectName },
          totals: {
            material_cost: result.material_cost_base,
            material_with_markup: result.material_cost_with_markup,
            labor_cost: result.labor_cost,
            coating_cost: result.coating_cost,
            total_cost: result.total_cost,
            total_weight_tons: result.total_weight_tons || 0,
            markup_percentage: result.breakdown.material_markup_percent || 35,
            total_entries: result.breakdown.entry_count || 0
          },
          generated_at: new Date().toISOString(),
          success: true
        }
        
        setProposalData(newProposalData)
        
        // Calculate bid summary with indirect expenses
        await calculateBidSummary(newProposalData)
        
        // Switch to summary tab to review bid
        setActiveTab('summary')
        
        if (onProposalGenerated) {
          onProposalGenerated(result)
        }
      } else {
        const errorText = await response.text()
        throw new Error(`Final proposal generation failed: ${errorText}`)
      }
    } catch (error) {
      console.error('Final proposal generation error:', error)
      alert(`Failed to generate final proposal: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const downloadProposalPDF = async () => {
    if (!proposalData) {
      alert('No proposal data available for PDF generation')
      return
    }

    try {
      const pdfPayload = {
        project_info: {
          name: projectName,
          client_name: 'Valued Client',
          project_location: 'Project Location', 
          id: projectId
        },
        totals: proposalData.totals
      }

      console.log('PDF Payload:', pdfPayload) // Debug log

      const response = await fetch('http://localhost:7000/api/v1/proposals/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pdfPayload)
      })

      console.log('PDF Response status:', response.status) // Debug log
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${projectName.replace(/[^a-zA-Z0-9]/g, '_')}_Proposal.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        console.log('PDF download initiated successfully')
      } else {
        const errorText = await response.text()
        console.error('PDF generation failed:', response.status, errorText)
        throw new Error(`PDF generation failed: ${response.status} ${errorText}`)
      }
    } catch (error) {
      console.error('PDF download error:', error)
      alert(`Failed to download PDF: ${error.message}`)
    }
  }

  // Bid Summary Functions
  const loadIndirectExpenses = async () => {
    try {
      const response = await fetch(`http://localhost:7000/api/v1/proposals/indirect-settings/${projectId}`)
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.indirect_expenses) {
          setIndirectExpenses(data.indirect_expenses)
        }
      }
    } catch (error) {
      console.error('Failed to load indirect expenses:', error)
      // Use defaults if loading fails
    }
  }

  const calculateBidSummary = async (proposalData = null) => {
    try {
      // If no proposalData provided, generate it first
      let dataToUse = proposalData
      if (!dataToUse) {
        // Generate proposal data if not provided
        const generateRequest = {
          project_id: projectId,
          template_type: "standard",
          markup_percentage: markupPercentage,
          include_labor: true,
          material_prices: [],
          notes: null
        }

        const response = await fetch('http://localhost:7000/api/v1/proposals/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(generateRequest)
        })
        
        if (response.ok) {
          dataToUse = await response.json()
          console.log('Generated proposal data:', dataToUse)
        } else {
          const errorText = await response.text()
          console.error('Failed to generate proposal data:', errorText)
          throw new Error(`Failed to get proposal data for bid calculation: ${errorText}`)
        }
      }

      console.log('Data to use for bid calculation:', dataToUse)
      console.log('Has totals?', dataToUse?.totals)

      if (!dataToUse || !dataToUse.totals) {
        console.error('Missing proposal data structure:', {
          dataToUse: !!dataToUse,
          totals: !!dataToUse?.totals,
          dataKeys: dataToUse ? Object.keys(dataToUse) : []
        })
        throw new Error('No proposal data available for bid calculation')
      }

      const requestPayload = {
        project_id: projectId,
        material_cost_base: dataToUse.totals.material_cost || 0,
        material_cost_with_markup: dataToUse.totals.material_with_markup || 0,
        labor_cost: dataToUse.totals.labor_cost || 0,
        coating_cost: dataToUse.totals.coating_cost || 0,
        indirect_expenses: {
          ...indirectExpenses,
          project_id: projectId
        }
      }

      console.log('Bid Summary Request Payload:', requestPayload)
      
      const response = await fetch('http://localhost:7000/api/v1/proposals/calculate-with-indirects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload)
      })

      if (response.ok) {
        const bidData = await response.json()
        console.log('Bid Summary Response:', bidData)
        setBidSummaryData(bidData)
        return bidData
      } else {
        const errorText = await response.text()
        console.error('Bid Summary API Error:', response.status, errorText)
        throw new Error(`Failed to calculate bid summary: ${errorText}`)
      }
    } catch (error) {
      console.error('Bid summary calculation error:', error)
      alert(`Failed to calculate bid summary: ${error.message}`)
      setBidSummaryData(null)
    }
  }

  const updateIndirectExpense = (field, value) => {
    setIndirectExpenses(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const saveIndirectSettings = async () => {
    try {
      const response = await fetch('http://localhost:7000/api/v1/proposals/save-indirect-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...indirectExpenses,
          project_id: projectId
        })
      })

      if (response.ok) {
        console.log('Indirect settings saved successfully')
        // Recalculate bid summary with new values
        if (proposalData) {
          await calculateBidSummary(proposalData)
        }
      } else {
        throw new Error('Failed to save indirect settings')
      }
    } catch (error) {
      console.error('Save indirect settings error:', error)
      alert('Failed to save indirect settings')
    }
  }

  const generateProposal = async () => {
    // Check if user should run optimization first
    if (!nestingData && materialPrices.length > 0) {
      const shouldOptimize = window.confirm(
        'You haven\'t run material nesting optimization yet. This could result in higher costs. ' +
        'Would you like to run optimization first for better pricing?'
      )
      if (shouldOptimize) {
        await runNestingOptimization()
        return // Let user review nesting results first
      }
    }
    
    setIsLoading(true)
    try {
      // Include nesting data if available for more accurate proposals
      const proposalPayload = {
        project_id: projectId,
        template_type: templateType,
        markup_percentage: markupPercentage,
        include_labor: includeLabor,
        material_prices: materialPrices,
        nesting_data: nestingData // Include optimized purchasing data
      }
      
      const response = await fetch('http://localhost:7000/api/v1/proposals/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proposalPayload)
      })
      
      if (response.ok) {
        const result = await response.json()
        setProposalData(result)
        
        if (onProposalGenerated) {
          onProposalGenerated(result)
        }
      } else {
        const errorText = await response.text()
        throw new Error(`Proposal generation failed: ${errorText}`)
      }
    } catch (error) {
      console.error('Proposal generation error:', error)
      alert(`Failed to generate proposal: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const updateMaterialPrice = (shapeKey: string, field: 'price_per_lb' | 'price_per_ft', value: number) => {
    setMaterialPrices(prev => prev.map(material => {
      if (material.shape_key === shapeKey) {
        const updated = { ...material, [field]: value, is_edited: true }
        // Recalculate total cost based on weight and new price per lb
        if (field === 'price_per_lb') {
          updated.total_cost = updated.total_weight_lbs * value
        }
        return updated
      }
      return material
    }))
    setHasUnsavedPrices(true)
  }

  // Bulk price adjustment functions
  const applyPercentageIncrease = () => {
    const percentage = parseFloat(bulkPercentage)
    if (isNaN(percentage) || percentage <= 0) {
      alert('Please enter a valid percentage greater than 0')
      return
    }

    setMaterialPrices(prev => prev.map(material => {
      // Apply filter by category if not 'all'
      if (selectedCategory !== 'all' && material.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return material
      }
      
      const multiplier = 1 + (percentage / 100)
      return {
        ...material,
        price_per_lb: material.price_per_lb * multiplier,
        price_per_ft: material.price_per_ft * multiplier,
        total_cost: material.total_weight_lbs * (material.price_per_lb * multiplier),
        is_edited: true
      }
    }))
    setHasUnsavedPrices(true)
    setBulkPercentage('')
  }

  const setBasePrice = () => {
    const basePrice = parseFloat(bulkBasePrice)
    if (isNaN(basePrice) || basePrice <= 0) {
      alert('Please enter a valid base price greater than 0')
      return
    }

    setMaterialPrices(prev => prev.map(material => {
      // Apply filter by category if not 'all'
      if (selectedCategory !== 'all' && material.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return material
      }
      
      // Calculate price_per_ft based on weight per foot if available
      const price_per_ft = material.price_per_ft > 0 ? 
        basePrice * (material.price_per_ft / material.price_per_lb) : basePrice
      
      return {
        ...material,
        price_per_lb: basePrice,
        price_per_ft: price_per_ft,
        total_cost: material.total_weight_lbs * basePrice,
        is_edited: true
      }
    }))
    setHasUnsavedPrices(true)
    setBulkBasePrice('')
  }

  const getUniqueCategories = () => {
    const categories = [...new Set(materialPrices.map(m => m.category))]
    return categories.sort()
  }

  // Enhanced nesting table edit functions
  const updateNestingValue = (index: number, field: string, value: number | string) => {
    if (!nestingData) return
    
    setNestingData(prev => {
      if (!prev) return prev
      const updated = {...prev}
      const updatedPurchases = [...prev.material_purchases]
      const purchase = updatedPurchases[index]
      
      // Handle different field types
      let processedValue: number | string
      
      if (field === 'size_description') {
        // Handle string fields
        processedValue = typeof value === 'string' ? value : String(value)
      } else {
        // Handle numeric fields
        let numericValue: number
        if (typeof value === 'string') {
          numericValue = field.includes('percentage') ? parseFloat(value) || 0 : parseInt(value) || 0
        } else {
          numericValue = value
        }
        
        // Validate input ranges
        if (field === 'pieces_needed' && numericValue < 1) numericValue = 1
        if (field === 'cuts_count' && numericValue < 1) numericValue = 1
        if (field === 'waste_percentage' && (numericValue < 0 || numericValue > 100)) {
          numericValue = Math.max(0, Math.min(100, numericValue))
        }
        if ((field === 'total_cost' || field === 'waste_cost') && numericValue < 0) {
          numericValue = 0
        }
        
        processedValue = numericValue
      }
      
      // Update the field
      updatedPurchases[index] = {
        ...purchase,
        [field]: processedValue
      }
      
      // Recalculate dependent values based on what field changed (only for numeric fields)
      if (field !== 'size_description') {
        const updatedPurchase = updatedPurchases[index]
        const numericValue = processedValue as number
        const originalUnitCost = purchase.total_cost / (purchase.pieces_needed || 1)
        
        if (field === 'pieces_needed') {
          // Recalculate total cost and waste cost based on new piece count
          updatedPurchase.total_cost = originalUnitCost * numericValue
          updatedPurchase.waste_cost = (updatedPurchase.total_cost * updatedPurchase.waste_percentage) / 100
        } else if (field === 'waste_percentage') {
          // Recalculate waste cost based on new waste percentage
          updatedPurchase.waste_cost = (updatedPurchase.total_cost * numericValue) / 100
        } else if (field === 'total_cost') {
          // Recalculate waste cost and update unit cost
          updatedPurchase.waste_cost = (numericValue * updatedPurchase.waste_percentage) / 100
        } else if (field === 'waste_cost') {
          // Recalculate waste percentage based on new waste cost
          if (updatedPurchase.total_cost > 0) {
            updatedPurchase.waste_percentage = (numericValue / updatedPurchase.total_cost) * 100
          }
        }
      }
      
      updated.material_purchases = updatedPurchases
      
      // Recalculate overall totals
      const totalCost = updatedPurchases.reduce((sum, p) => sum + p.total_cost, 0)
      const totalWasteCost = updatedPurchases.reduce((sum, p) => sum + p.waste_cost, 0)
      
      updated.total_cost = totalCost
      updated.total_waste_percentage = totalCost > 0 ? (totalWasteCost / totalCost) * 100 : 0
      
      // Recalculate cost savings (compared to original material cost)
      const originalCost = materialPrices.reduce((sum, m) => sum + m.total_cost, 0)
      updated.cost_savings = Math.max(0, originalCost - totalCost)
      
      return updated
    })
    setHasUnsavedNesting(true)
  }

  const saveNestingChanges = async () => {
    if (!nestingData) return
    
    setIsSavingNesting(true)
    try {
      const response = await fetch(`http://localhost:7000/api/v1/nesting/save-results/${projectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nestingData)
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Nesting changes saved successfully:', result)
        setHasUnsavedNesting(false)
        setEditingNesting(false)
        setNestingSaveStatus('saved')
        
        // Auto-clear status after 3 seconds
        setTimeout(() => setNestingSaveStatus(null), 3000)
      } else {
        throw new Error(`Save failed: ${response.status}`)
      }
    } catch (error) {
      console.error('❌ Failed to save nesting changes:', error)
      setNestingSaveStatus('error')
      alert('Failed to save nesting changes. Please try again.')
    } finally {
      setIsSavingNesting(false)
    }
  }

  const cancelNestingEdit = () => {
    setEditingNesting(false)
    setHasUnsavedNesting(false)
    // Re-run nesting optimization to restore original values
    runNestingOptimization()
  }

  // Bulk editing functions for nesting table
  const bulkUpdateNesting = (field: string, adjustment: number) => {
    if (!nestingData) return

    setNestingData(prev => {
      if (!prev) return prev
      const updated = {...prev}
      const updatedPurchases = prev.material_purchases.map((purchase, index) => {
        const currentValue = purchase[field as keyof typeof purchase] as number
        let newValue: number

        if (field === 'waste_percentage') {
          newValue = Math.max(0, Math.min(100, currentValue + adjustment))
        } else if (field === 'pieces_needed' || field === 'cuts_count') {
          newValue = Math.max(1, currentValue + adjustment)
        } else {
          newValue = Math.max(0, currentValue + adjustment)
        }

        // Create updated purchase with recalculated values
        const updatedPurchase = {...purchase, [field]: newValue}
        const originalUnitCost = purchase.total_cost / (purchase.pieces_needed || 1)

        if (field === 'pieces_needed') {
          updatedPurchase.total_cost = originalUnitCost * newValue
          updatedPurchase.waste_cost = (updatedPurchase.total_cost * updatedPurchase.waste_percentage) / 100
        } else if (field === 'waste_percentage') {
          updatedPurchase.waste_cost = (updatedPurchase.total_cost * newValue) / 100
        }

        return updatedPurchase
      })

      updated.material_purchases = updatedPurchases

      // Recalculate overall totals
      const totalCost = updatedPurchases.reduce((sum, p) => sum + p.total_cost, 0)
      const totalWasteCost = updatedPurchases.reduce((sum, p) => sum + p.waste_cost, 0)
      
      updated.total_cost = totalCost
      updated.total_waste_percentage = totalCost > 0 ? (totalWasteCost / totalCost) * 100 : 0

      // Recalculate cost savings
      const originalCost = materialPrices.reduce((sum, m) => sum + m.total_cost, 0)
      updated.cost_savings = Math.max(0, originalCost - totalCost)

      return updated
    })

    setHasUnsavedNesting(true)
  }

  // Function to reset all waste percentages to optimal values
  const optimizeAllWastePercentages = () => {
    if (!nestingData) return

    setNestingData(prev => {
      if (!prev) return prev
      const updated = {...prev}
      const updatedPurchases = prev.material_purchases.map(purchase => {
        // Set optimal waste percentage (10% for excellent efficiency)
        const optimizedPurchase = {...purchase, waste_percentage: 10}
        optimizedPurchase.waste_cost = (purchase.total_cost * 10) / 100
        return optimizedPurchase
      })

      updated.material_purchases = updatedPurchases

      // Recalculate totals
      const totalCost = updatedPurchases.reduce((sum, p) => sum + p.total_cost, 0)
      const totalWasteCost = updatedPurchases.reduce((sum, p) => sum + p.waste_cost, 0)
      
      updated.total_cost = totalCost
      updated.total_waste_percentage = totalCost > 0 ? (totalWasteCost / totalCost) * 100 : 0
      updated.cost_savings = Math.max(0, materialPrices.reduce((sum, m) => sum + m.total_cost, 0) - totalCost)

      return updated
    })

    setHasUnsavedNesting(true)
  }

  // Enhanced utility functions
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  // Workflow guidance functions
  const getWorkflowStepStatus = (step: string) => {
    const steps = ['pricing', 'nesting', 'proposal']
    const currentIndex = steps.indexOf(workflowStep)
    const stepIndex = steps.indexOf(step)
    
    if (stepIndex < currentIndex) return 'completed'
    if (stepIndex === currentIndex) return 'active'
    return 'upcoming'
  }

  const updateWorkflowStep = () => {
    // Determine current workflow step based on data state
    if (proposalData) {
      setWorkflowStep('complete')
    } else if (nestingData && nestingData.material_purchases.length > 0) {
      setWorkflowStep('proposal')
    } else if (materialPrices.length > 0 && materialPrices.some(p => p.price_per_lb > 0 || p.price_per_ft > 0)) {
      setWorkflowStep('nesting')
    } else {
      setWorkflowStep('pricing')
    }
  }

  const getWorkflowGuidance = () => {
    switch (workflowStep) {
      case 'pricing':
        return {
          title: "Step 1: Review & Adjust Material Prices",
          description: "Review material prices from your takeoff entries. Edit prices to match current market rates for accurate cost analysis.",
          nextAction: "After saving prices, nesting optimization will run automatically.",
          tips: ["Use bulk pricing tools for efficiency", "Focus on high-cost materials first", "Enable auto-optimization for seamless workflow"]
        }
      case 'nesting':
        return {
          title: "Step 2: Optimize Material Nesting",
          description: "Review and optimize material purchase recommendations to minimize waste and reduce costs.",
          nextAction: "Fine-tune the nesting recommendations, then proceed to bid summary review.",
          tips: ["Look for items with >20% waste", "Use bulk editing for multiple adjustments", "Save your optimization settings"]
        }
      case 'summary':
        return {
          title: "Step 3: Review Bid Summary",
          description: "Review all costs including indirect expenses (8.3%) before generating the final proposal.",
          nextAction: "Verify indirect expenses, adjust if needed, then proceed to PDF generation.",
          tips: ["Default indirects: Consumables $3.64, Misc 1%, Fuel $13.26", "Adjust percentages as needed", "Save settings for future projects"]
        }
      case 'proposal':
        return {
          title: "Step 4: Generate Professional Proposal", 
          description: "Create a polished proposal document with your optimized pricing and complete cost breakdown.",
          nextAction: "Configure final settings and generate your professional PDF document.",
          tips: ["Review all totals are correct", "Download and save for records", "Share with client when ready"]
        }
      case 'complete':
        return {
          title: "✅ Proposal Complete!",
          description: "Your professional proposal has been generated with optimized material costs and recommendations.",
          nextAction: "Review, download, or share your proposal with the client.",
          tips: ["Save a copy for your records", "Track client response", "Use this as a template for similar projects"]
        }
      default:
        return null
    }
  }

  // Update workflow step when data changes
  React.useEffect(() => {
    updateWorkflowStep()
  }, [materialPrices, nestingData, proposalData])

  const getEfficiencyColor = (wastePercentage: number) => {
    if (wastePercentage <= 10) return 'text-green-400'
    if (wastePercentage <= 20) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getEfficiencyGrade = (wastePercentage: number) => {
    if (wastePercentage <= 10) return 'A'
    if (wastePercentage <= 20) return 'B'
    if (wastePercentage <= 35) return 'C'
    return 'D'
  }

  // Auto-refresh nesting when material prices change significantly
  const checkForNestingRefresh = () => {
    if (nestingData && materialPrices.some(m => m.is_edited)) {
      return (
        <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-3 mb-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">
              Material prices have changed. Consider re-running nesting optimization for updated results.
            </span>
            <button
              onClick={runNestingOptimization}
              className="ml-auto bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
            >
              Update Nesting
            </button>
          </div>
        </div>
      )
    }
    return null
  }

  const savePriceChanges = async () => {
    setIsLoading(true)
    try {
      const changedPrices = materialPrices.filter(m => m.is_edited)
      
      if (changedPrices.length === 0) {
        setEditingPrices(false)
        return
      }

      const response = await fetch('http://localhost:7000/api/v1/proposals/update-prices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          price_updates: changedPrices.map(m => ({
            shape_key: m.shape_key,
            price_per_lb: m.price_per_lb,
            price_per_ft: m.price_per_ft,
            is_edited: m.is_edited
          }))
        })
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Price changes saved:', result)
        
        // Mark all prices as saved
        setMaterialPrices(prev => prev.map(m => ({ ...m, is_edited: false })))
        setHasUnsavedPrices(false)
        setEditingPrices(false)
        
        // Auto-run nesting optimization after significant price changes
        if (autoOptimizeOnPriceChange && changedPrices.length > 0) {
          // Check if changes are significant (>5% change in any price or >3 items changed)
          const significantChanges = changedPrices.length >= 3 || changedPrices.some(price => {
            // This is a simplified check - in production you'd compare with original values
            const priceValue = price.price_per_lb || price.price_per_ft || 0
            return priceValue > 0 // For now, any edited price is considered significant
          })
          
          if (significantChanges) {
            console.log(`🔄 Auto-running nesting optimization after ${changedPrices.length} significant price changes...`)
            
            // Show notification to user about auto-optimization
            const notification = document.createElement('div')
            notification.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center gap-2'
            notification.innerHTML = `
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Optimizing materials with updated prices...</span>
            `
            document.body.appendChild(notification)
            
            // Switch to nesting tab and run optimization after a brief delay
            setTimeout(() => {
              setActiveTab('nesting')
              setTimeout(() => {
                runNestingOptimization()
                // Update notification
                notification.innerHTML = '<span>✅ Material optimization complete!</span>'
                notification.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50'
                
                // Remove notification after showing success
                setTimeout(() => {
                  if (document.body.contains(notification)) {
                    document.body.removeChild(notification)
                  }
                }, 2000)
              }, 500) // Small delay to allow tab switch
            }, 1500) // 1.5 second delay to show price changes saved
          } else {
            console.log('ℹ️ Price changes not significant enough to trigger auto-optimization')
          }
        }
      } else {
        throw new Error('Failed to save price changes')
      }
    } catch (error) {
      console.error('Failed to save price changes:', error)
      alert('Failed to save price changes. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'pricing':
        return (
          <div className="space-y-6">
            {/* Pricing Header */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-3xl font-bold text-white">Material Price Review</h3>
                <p className="text-lg text-gray-400">Confirm and adjust material pricing before proposal generation</p>
              </div>
              <div className="flex items-center gap-3">
                {hasUnsavedPrices && (
                  <div className="flex items-center gap-2 text-orange-400">
                    <AlertCircle className="w-6 h-6" />
                    <span className="text-lg">Unsaved changes</span>
                  </div>
                )}
                {editingPrices ? (
                  <>
                    <button
                      onClick={savePriceChanges}
                      disabled={!hasUnsavedPrices || isLoading}
                      className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg text-lg font-medium"
                    >
                      <Save className="w-6 h-6" />
                      Save Changes
                    </button>
                    <button
                      onClick={() => {
                        setEditingPrices(false)
                        loadMaterialPrices() // Reset changes
                      }}
                      className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg text-lg"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setEditingPrices(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-lg font-medium"
                  >
                    <Edit className="w-6 h-6" />
                    Edit Prices
                  </button>
                )}
              </div>
            </div>

            {/* Bulk Adjustments */}
            {editingPrices && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h4 className="text-2xl font-semibold text-white mb-4">Bulk Price Adjustments</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-lg font-medium text-gray-300 mb-3">
                      Apply % Increase
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        step="0.5"
                        placeholder="5.0"
                        value={bulkPercentage}
                        onChange={(e) => setBulkPercentage(e.target.value)}
                        className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded text-white text-lg"
                        onKeyPress={(e) => e.key === 'Enter' && applyPercentageIncrease()}
                      />
                      <button 
                        onClick={applyPercentageIncrease}
                        disabled={!bulkPercentage.trim()}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:opacity-50 text-white px-4 py-3 rounded text-lg transition-colors"
                      >
                        Apply
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Set Base Price $/lb
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        step="0.01"
                        placeholder="0.67"
                        value={bulkBasePrice}
                        onChange={(e) => setBulkBasePrice(e.target.value)}
                        className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                        onKeyPress={(e) => e.key === 'Enter' && setBasePrice()}
                      />
                      <button 
                        onClick={setBasePrice}
                        disabled={!bulkBasePrice.trim()}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:opacity-50 text-white px-3 py-2 rounded text-sm transition-colors"
                      >
                        Apply
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Category Filter
                    </label>
                    <select 
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                    >
                      <option value="all">All Materials</option>
                      {getUniqueCategories().map(category => (
                        <option key={category} value={category}>{category}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Material Prices Table */}
            <div className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Material</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Category</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Qty</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Weight (lbs)</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Price/lb</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Price/ft</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Total Cost</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-300">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {materialPrices.map((material) => (
                      <tr key={material.shape_key} className="hover:bg-gray-700">
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium text-white">{material.shape_key}</div>
                            <div className="text-sm text-gray-400 truncate">{material.description}</div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-300">{material.category}</td>
                        <td className="px-4 py-3 text-right text-sm text-white">{material.total_qty}</td>
                        <td className="px-4 py-3 text-right text-sm text-white">{material.total_weight_lbs.toFixed(1)}</td>
                        <td className="px-4 py-3 text-right">
                          {editingPrices ? (
                            <input
                              type="number"
                              step="0.01"
                              value={material.price_per_lb}
                              onChange={(e) => updateMaterialPrice(material.shape_key, 'price_per_lb', Number(e.target.value))}
                              className="w-20 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm text-right"
                            />
                          ) : (
                            <span className="text-white">${material.price_per_lb.toFixed(2)}</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {editingPrices ? (
                            <input
                              type="number"
                              step="0.01"
                              value={material.price_per_ft}
                              onChange={(e) => updateMaterialPrice(material.shape_key, 'price_per_ft', Number(e.target.value))}
                              className="w-20 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm text-right"
                            />
                          ) : (
                            <span className="text-white">${material.price_per_ft.toFixed(2)}</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right text-green-400 font-medium">
                          {formatCurrency(material.total_cost)}
                        </td>
                        <td className="px-4 py-3 text-center">
                          {material.is_edited ? (
                            <div className="flex items-center justify-center">
                              <AlertCircle className="w-4 h-4 text-orange-400" />
                            </div>
                          ) : (
                            <div className="flex items-center justify-center">
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-700">
                    <tr>
                      <td colSpan={4} className="px-4 py-3 text-right font-medium text-gray-300">Total:</td>
                      <td className="px-4 py-3 text-right font-bold text-white">
                        {materialPrices.reduce((sum, m) => sum + m.total_weight_lbs, 0).toFixed(1)} lbs
                      </td>
                      <td className="px-4 py-3"></td>
                      <td className="px-4 py-3 text-right font-bold text-green-400">
                        {formatCurrency(materialPrices.reduce((sum, m) => sum + m.total_cost, 0))}
                      </td>
                      <td className="px-4 py-3"></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>
        )

      case 'nesting':
        return (
          <div className="space-y-6">
            {/* Nesting Header */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-3xl font-bold text-white">Material Nesting Optimization</h3>
                <p className="text-lg text-gray-400">Minimize waste and optimize material purchasing</p>
                {hasUnsavedNesting && (
                  <div className="flex items-center gap-2 text-orange-400 mt-1">
                    <AlertCircle className="w-4 h-4" />
                    <span className="text-sm">Unsaved nesting changes</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                {editingNesting && nestingData ? (
                  <>
                    <button
                      onClick={saveNestingChanges}
                      disabled={!hasUnsavedNesting || isSavingNesting}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        nestingSaveStatus === 'saved' ? 'bg-green-600 hover:bg-green-700 text-white' :
                        nestingSaveStatus === 'error' ? 'bg-red-600 hover:bg-red-700 text-white' :
                        hasUnsavedNesting ? 'bg-orange-600 hover:bg-orange-700 text-white' :
                        'bg-gray-600 text-gray-300 opacity-50'
                      }`}
                    >
                      {isSavingNesting ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : nestingSaveStatus === 'saved' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : nestingSaveStatus === 'error' ? (
                        <AlertTriangle className="w-4 h-4" />
                      ) : (
                        <Save className="w-4 h-4" />
                      )}
                      {isSavingNesting ? 'Saving...' :
                       nestingSaveStatus === 'saved' ? 'Saved ✓' :
                       nestingSaveStatus === 'error' ? 'Save Failed' :
                       hasUnsavedNesting ? 'Save Changes' : 'No Changes'}
                    </button>
                    <button
                      onClick={cancelNestingEdit}
                      className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    {nestingData && (
                      <button
                        onClick={() => setEditingNesting(true)}
                        className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                      >
                        <Edit className="w-4 h-4" />
                        Edit Nesting
                      </button>
                    )}
                    <button
                      onClick={runNestingOptimization}
                      disabled={isLoading}
                      className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-2 rounded-lg font-medium"
                    >
                      {isLoading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        <Calculator className="w-4 h-4" />
                      )}
                      {isLoading ? 'Optimizing...' : 'Run Optimization'}
                    </button>
                  </>
                )}
              </div>
            </div>

            {checkForNestingRefresh()}
            {nestingData ? (
              <>
                {/* Optimization Summary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-green-900 bg-opacity-30 border border-green-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-400">
                      {formatCurrency(nestingData.cost_savings || 0)}
                    </div>
                    <div className="text-sm text-gray-400">Cost Savings</div>
                  </div>
                  <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4">
                    <div className={`text-2xl font-bold ${getEfficiencyColor(nestingData.total_waste_percentage || 0)}`}>
                      {nestingData.total_waste_percentage?.toFixed(1) || '0'}%
                    </div>
                    <div className="text-sm text-gray-400">
                      Material Waste (Grade: {getEfficiencyGrade(nestingData.total_waste_percentage || 0)})
                    </div>
                  </div>
                  <div className="bg-purple-900 bg-opacity-30 border border-purple-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-400">
                      {formatCurrency(nestingData.total_cost || 0)}
                    </div>
                    <div className="text-sm text-gray-400">Total Cost</div>
                  </div>
                  <div className="bg-orange-900 bg-opacity-30 border border-orange-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-orange-400">
                      {nestingData.material_purchases?.length || 0}
                    </div>
                    <div className="text-sm text-gray-400">Purchase Items</div>
                  </div>
                </div>

                {/* Purchase Recommendations */}
                <div className="bg-gray-800 rounded-lg overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-semibold text-white">Material Purchase Recommendations</h4>
                      {editingNesting && (
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-2 text-sm">
                            <label className="text-gray-300">Bulk Actions:</label>
                            <button
                              onClick={() => bulkUpdateNesting('waste_percentage', -5)}
                              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded"
                              title="Reduce waste by 5% for all items"
                            >
                              -5% Waste
                            </button>
                            <button
                              onClick={() => bulkUpdateNesting('pieces_needed', 1)}
                              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded"
                              title="Add 1 piece to all items"
                            >
                              +1 Piece
                            </button>
                            <button
                              onClick={() => bulkUpdateNesting('cuts_count', 1)}
                              className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded"
                              title="Add 1 cut to all items"
                            >
                              +1 Cut
                            </button>
                            <button
                              onClick={optimizeAllWastePercentages}
                              className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded"
                              title="Set all waste percentages to optimal 10%"
                            >
                              Optimize All
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-700">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Material</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Size Description</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Pieces Needed</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Cuts Count</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Waste %</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Waste Cost</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Total Cost</th>
                          <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Efficiency</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {nestingData.material_purchases.map((purchase, index) => (
                          <tr key={index} className="hover:bg-gray-700">
                            <td className="px-4 py-3 font-medium text-white">{purchase.shape_key}</td>
                            <td className="px-4 py-3 text-sm">
                              {editingNesting ? (
                                <input
                                  type="text"
                                  value={purchase.size_description}
                                  onChange={(e) => updateNestingValue(index, 'size_description', e.target.value)}
                                  className="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                                />
                              ) : (
                                <span className="text-gray-300">{purchase.size_description}</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {editingNesting ? (
                                <input
                                  type="number"
                                  min="1"
                                  value={purchase.pieces_needed}
                                  onChange={(e) => updateNestingValue(index, 'pieces_needed', e.target.value)}
                                  className="w-20 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm text-right"
                                />
                              ) : (
                                <span className="text-white">{purchase.pieces_needed}</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {editingNesting ? (
                                <input
                                  type="number"
                                  min="1"
                                  value={purchase.cuts_count}
                                  onChange={(e) => updateNestingValue(index, 'cuts_count', e.target.value)}
                                  className="w-16 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm text-right"
                                />
                              ) : (
                                <span className="text-white">{purchase.cuts_count}</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {editingNesting ? (
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="0.1"
                                  value={purchase.waste_percentage.toFixed(1)}
                                  onChange={(e) => updateNestingValue(index, 'waste_percentage', e.target.value)}
                                  className={`w-20 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-sm text-right ${
                                    purchase.waste_percentage <= 10 ? 'text-green-400' :
                                    purchase.waste_percentage <= 20 ? 'text-yellow-400' :
                                    'text-red-400'
                                  }`}
                                />
                              ) : (
                                <span className={`font-medium ${
                                  purchase.waste_percentage <= 10 ? 'text-green-400' :
                                  purchase.waste_percentage <= 20 ? 'text-yellow-400' :
                                  'text-red-400'
                                }`}>
                                  {purchase.waste_percentage.toFixed(1)}%
                                </span>
                              )}
                              {editingNesting && hasUnsavedNesting && (
                                <AlertCircle className="w-3 h-3 text-orange-400 inline ml-1" />
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {editingNesting ? (
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={purchase.waste_cost.toFixed(2)}
                                  onChange={(e) => updateNestingValue(index, 'waste_cost', parseFloat(e.target.value) || 0)}
                                  className="w-24 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-red-400 text-sm text-right"
                                />
                              ) : (
                                <span className="text-red-400">{formatCurrency(purchase.waste_cost)}</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {editingNesting ? (
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={purchase.total_cost.toFixed(2)}
                                  onChange={(e) => updateNestingValue(index, 'total_cost', parseFloat(e.target.value) || 0)}
                                  className="w-24 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-green-400 text-sm text-right font-medium"
                                />
                              ) : (
                                <span className="text-green-400 font-medium">{formatCurrency(purchase.total_cost)}</span>
                              )}
                              {editingNesting && hasUnsavedNesting && (
                                <span className="ml-1 text-xs text-orange-400">(edited)</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              <div className="flex items-center justify-end gap-2">
                                <span className={`text-sm font-medium ${
                                  purchase.waste_percentage <= 10 ? 'text-green-400' :
                                  purchase.waste_percentage <= 20 ? 'text-yellow-400' :
                                  'text-red-400'
                                }`}>
                                  {(100 - purchase.waste_percentage).toFixed(1)}%
                                </span>
                                <span className={`px-2 py-1 text-xs font-bold rounded ${
                                  purchase.waste_percentage <= 10 ? 'bg-green-900 text-green-300' :
                                  purchase.waste_percentage <= 20 ? 'bg-yellow-900 text-yellow-300' :
                                  'bg-red-900 text-red-300'
                                }`}>
                                  {purchase.waste_percentage <= 10 ? 'A' :
                                   purchase.waste_percentage <= 20 ? 'B' :
                                   purchase.waste_percentage <= 35 ? 'C' : 'D'}
                                </span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      {editingNesting && (
                        <tfoot className="bg-gray-700">
                          <tr>
                            <td colSpan={7} className="px-4 py-2 text-center text-sm text-gray-300">
                              <div className="flex items-center justify-center gap-2">
                                <Edit className="w-4 h-4" />
                                Edit mode active - modify pieces needed and cuts count, then save changes
                              </div>
                            </td>
                          </tr>
                        </tfoot>
                      )}
                    </table>
                  </div>
                </div>

                {/* Optimization Summary */}
                <div className="bg-gray-800 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-3">Optimization Summary</h4>
                  <div className="text-gray-300 whitespace-pre-wrap">
                    {nestingData.optimization_summary}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-gray-800 rounded-lg p-12 text-center">
                <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-xl font-semibold text-white mb-2">No Optimization Data</h4>
                <p className="text-gray-400 mb-6">Run material optimization to view nesting analysis and purchase recommendations</p>
                <button
                  onClick={runNestingOptimization}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium mx-auto"
                >
                  <Calculator className="w-5 h-5" />
                  Run Optimization
                </button>
              </div>
            )}
          </div>
        )

      case 'proposal':
        return (
          <div className="space-y-6">
            {/* Proposal Header */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-3xl font-bold text-white">Capitol Engineering Proposal</h3>
                <p className="text-lg text-gray-400">Professional proposal generation with company branding</p>
              </div>
              {proposalData && (
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => downloadProposalPDF()}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                  >
                    <Download className="w-4 h-4" />
                    Download PDF
                  </button>
                  <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
                    <Printer className="w-4 h-4" />
                    Print
                  </button>
                  <button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
                    <Mail className="w-4 h-4" />
                    Email
                  </button>
                </div>
              )}
            </div>

            {!proposalData ? (
              <>
                {/* Proposal Configuration */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <h4 className="text-lg font-semibold text-white mb-4">Proposal Configuration</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Template Type
                      </label>
                      <select
                        value={templateType}
                        onChange={(e) => setTemplateType(e.target.value)}
                        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="standard">Standard Proposal</option>
                        <option value="detailed">Detailed Breakdown</option>
                        <option value="summary">Executive Summary</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Markup Percentage
                      </label>
                      <div className="relative">
                        <input
                          type="number"
                          min="0"
                          max="50"
                          step="0.5"
                          value={markupPercentage}
                          onChange={(e) => setMarkupPercentage(Number(e.target.value))}
                          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <span className="absolute right-3 top-2.5 text-gray-400">%</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={includeLabor}
                        onChange={(e) => setIncludeLabor(e.target.checked)}
                        className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="text-sm font-medium text-gray-300">Include Labor Costs in Proposal</span>
                    </label>
                  </div>
                </div>

                {/* Generate Proposal Button with Smart Recommendations */}
                <div className="space-y-3">
                  {!nestingData && materialPrices.length > 0 && (
                    <div className="bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-400" />
                        <span className="text-sm text-yellow-300">
                          Consider running nesting optimization first to potentially reduce material costs in your proposal.
                        </span>
                      </div>
                    </div>
                  )}
                  
                  <button
                    onClick={generateFinalProposal}
                    disabled={isLoading || !nestingData || !nestingData.total_cost}
                    className="w-full flex items-center justify-center gap-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white font-medium py-3 px-6 rounded-lg transition-colors"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Generating Proposal...
                      </>
                    ) : (
                      <>
                        <FileText className="w-5 h-5" />
                        Generate Final Proposal
                        {nestingData && (
                          <span className="text-xs bg-green-600 px-2 py-1 rounded">
                            35% Markup + Labor
                          </span>
                        )}
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              /* Generated Proposal Display */
              <div className="space-y-6">
                {/* Proposal Metadata */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-800 rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">
                      ${proposalData.totals.total_cost.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-400">Total Proposal Value</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {proposalData.totals.total_weight_tons.toFixed(1)}
                    </div>
                    <div className="text-xs text-gray-400">Total Tons</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">
                      {proposalData.totals.markup_percentage}%
                    </div>
                    <div className="text-xs text-gray-400">Markup Applied</div>
                  </div>
                </div>

                {/* Proposal Content */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <div className="text-sm text-gray-400 mb-3">
                    Generated: {new Date(proposalData.generated_at).toLocaleString()}
                  </div>
                  <div className="bg-white rounded p-6 max-h-96 overflow-auto">
                    <div className="text-black whitespace-pre-wrap font-mono text-sm leading-relaxed">
                      {proposalData.proposal_content}
                    </div>
                  </div>
                </div>

                {/* Generate New Proposal */}
                <button
                  onClick={() => setProposalData(null)}
                  className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium"
                >
                  <Settings className="w-4 h-4" />
                  Generate New Proposal
                </button>
              </div>
            )}
          </div>
        )

      case 'summary':
        return (
          <div className="space-y-6">
            {/* Bid Summary Header */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-3xl font-bold text-white">Bid Summary Review</h3>
                <p className="text-lg text-gray-400">Review all costs including indirect expenses before generating final proposal</p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => calculateBidSummary()}
                  disabled={isLoading}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  <Calculator className="w-4 h-4" />
                  {isLoading ? 'Calculating...' : 'Refresh Summary'}
                </button>
              </div>
            </div>

            {bidSummaryData ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Base Costs Section */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <h4 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Package className="w-8 h-8" />
                    Base Project Costs
                  </h4>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-gray-700">
                      <span className="text-xl text-gray-300">Materials (with 35% markup)</span>
                      <span className="text-xl text-white font-medium">${bidSummaryData.base_costs?.material_with_markup?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-700">
                      <span className="text-xl text-gray-300">Labor ($120/hr)</span>
                      <span className="text-xl text-white font-medium">${bidSummaryData.base_costs?.labor?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-700">
                      <span className="text-xl text-gray-300">Coatings (with 35% markup)</span>
                      <span className="text-xl text-white font-medium">${bidSummaryData.base_costs?.coating?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 font-semibold text-blue-300 border-t border-gray-600 pt-3">
                      <span className="text-xl">Subtotal for Indirects</span>
                      <span className="text-xl">${bidSummaryData.final_totals?.subtotal?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </div>

                {/* Indirect Expenses Section */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <h4 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Calculator className="w-8 h-8" />
                    Indirect Expenses (8.3%)
                  </h4>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xl text-gray-300">Consumables (6.0%)</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          step="0.1"
                          value={indirectExpenses.consumables_percentage}
                          onChange={(e) => updateIndirectExpense('consumables_percentage', parseFloat(e.target.value))}
                          className="w-20 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-lg text-right"
                        />
                        <span className="text-xl text-gray-300">%</span>
                        <span className="text-xl text-white font-medium">${bidSummaryData.indirect_expenses?.consumables?.toFixed(2) || '0.00'}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-xl text-gray-300">Misc (1.0%)</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          step="0.1"
                          value={indirectExpenses.misc_percentage}
                          onChange={(e) => updateIndirectExpense('misc_percentage', parseFloat(e.target.value))}
                          className="w-20 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-lg text-right"
                        />
                        <span className="text-xl text-gray-300">%</span>
                        <span className="text-xl text-white font-medium">${bidSummaryData.indirect_expenses?.misc?.toFixed(2) || '0.00'}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-xl text-gray-300">Fuel Surcharge (1.3%)</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          step="0.1"
                          value={indirectExpenses.fuel_surcharge_percentage}
                          onChange={(e) => updateIndirectExpense('fuel_surcharge_percentage', parseFloat(e.target.value))}
                          className="w-20 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-lg text-right"
                        />
                        <span className="text-xl text-gray-300">%</span>
                        <span className="text-xl text-white font-medium">${bidSummaryData.indirect_expenses?.fuel_surcharge?.toFixed(2) || '0.00'}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center py-2 font-semibold text-orange-300 border-t border-gray-600 pt-3">
                      <span className="text-xl">Total Indirects (8.3%)</span>
                      <span className="text-xl">${bidSummaryData.final_totals?.total_indirects?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </div>

                {/* Final Bid Total */}
                <div className="lg:col-span-2 bg-gradient-to-r from-green-900 to-blue-900 rounded-lg p-6">
                  <div className="text-center">
                    <h4 className="text-4xl font-bold text-white mb-4">Final Bid Total</h4>
                    <div className="text-6xl font-bold text-green-300 mb-6">
                      ${bidSummaryData.final_totals?.final_bid_total?.toFixed(2) || '0.00'}
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-lg">
                      <div className="bg-black bg-opacity-20 rounded p-4">
                        <div className="text-gray-300">Material Weight</div>
                        <div className="text-white font-medium text-xl">9.4 tons</div>
                      </div>
                      <div className="bg-black bg-opacity-20 rounded p-4">
                        <div className="text-gray-300">Base Subtotal</div>
                        <div className="text-white font-medium text-xl">${bidSummaryData.final_totals?.subtotal?.toFixed(2) || '0.00'}</div>
                      </div>
                      <div className="bg-black bg-opacity-20 rounded p-4">
                        <div className="text-gray-300">Total Indirects</div>
                        <div className="text-white font-medium text-xl">${bidSummaryData.final_totals?.total_indirects?.toFixed(2) || '0.00'}</div>
                      </div>
                      <div className="bg-black bg-opacity-20 rounded p-4">
                        <div className="text-gray-300">Cost per Ton</div>
                        <div className="text-white font-medium text-xl">
                          ${bidSummaryData.final_totals?.final_bid_total ? (bidSummaryData.final_totals.final_bid_total / 9.4).toFixed(2) : '0.00'}
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-center gap-4 mt-8">
                      <button
                        onClick={saveIndirectSettings}
                        disabled={isLoading}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-8 py-3 rounded-lg font-medium text-lg"
                      >
                        <Save className="w-6 h-6" />
                        Save Settings
                      </button>
                      <button
                        onClick={() => setActiveTab('proposal')}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-medium text-lg"
                      >
                        <FileText className="w-6 h-6" />
                        Generate PDF
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg p-8 text-center">
                <Calculator className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-white mb-2">Ready to Calculate</h4>
                <p className="text-gray-400 mb-4">
                  Click "Refresh Summary" to calculate your bid with indirect expenses
                </p>
                <button
                  onClick={() => calculateBidSummary()}
                  disabled={isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium"
                >
                  {isLoading ? 'Calculating...' : 'Calculate Bid Summary'}
                </button>
              </div>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-purple-600 rounded-lg">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">CE Proposal System</h2>
            <p className="text-gray-400">Capitol Engineering Company - Professional Takeoff Proposals</p>
          </div>
        </div>

        {/* Smart Workflow Progress Indicator */}
        <div className="mb-4 p-4 bg-gray-800 rounded-lg border border-gray-700">
          {/* Progress Steps */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-4">
              {tabConfig.map((tab, index) => {
                const status = getWorkflowStepStatus(tab.id)
                const isLast = index === tabConfig.length - 1
                
                return (
                  <div key={tab.id} className="flex items-center">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                      status === 'completed' ? 'bg-green-600 text-white' :
                      status === 'active' ? 'bg-blue-600 text-white' :
                      'bg-gray-600 text-gray-300'
                    }`}>
                      {status === 'completed' ? '✓' : index + 1}
                    </div>
                    <span className={`ml-2 text-sm font-medium ${
                      status === 'active' ? 'text-white' :
                      status === 'completed' ? 'text-green-400' :
                      'text-gray-400'
                    }`}>
                      {tab.label}
                    </span>
                    {!isLast && (
                      <div className={`w-8 h-0.5 mx-3 ${
                        status === 'completed' ? 'bg-green-600' : 'bg-gray-600'
                      }`} />
                    )}
                  </div>
                )
              })}
              {workflowStep === 'complete' && (
                <>
                  <div className="w-8 h-0.5 mx-3 bg-green-600" />
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white text-sm font-medium">
                    ✓
                  </div>
                  <span className="ml-2 text-sm font-medium text-green-400">Complete</span>
                </>
              )}
            </div>
            
            {/* Current Step Info */}
            {getWorkflowGuidance() && (
              <div className="text-right max-w-md">
                <div className="text-sm font-medium text-white">{getWorkflowGuidance()?.title}</div>
                <div className="text-xs text-gray-400 mt-1">{getWorkflowGuidance()?.nextAction}</div>
              </div>
            )}
          </div>
          
          {/* Detailed Guidance */}
          {getWorkflowGuidance() && (
            <div className="p-3 bg-gray-750 rounded border border-gray-600">
              <p className="text-sm text-gray-300 mb-2">{getWorkflowGuidance()?.description}</p>
              <div className="flex flex-wrap gap-2">
                {getWorkflowGuidance()?.tips.map((tip, index) => (
                  <span key={index} className="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">
                    💡 {tip}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Tab Navigation with Progress Indicators */}
        <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
          {tabConfig.map((tab) => {
            const Icon = tab.icon
            
            // Add completion indicators
            let indicator = null
            if (tab.id === 'pricing' && materialPrices.length > 0 && !materialPrices.some(m => m.is_edited)) {
              indicator = <CheckCircle className="w-3 h-3 text-green-400" />
            } else if (tab.id === 'nesting' && nestingData) {
              indicator = <CheckCircle className="w-3 h-3 text-green-400" />
            } else if (tab.id === 'summary' && bidSummaryData) {
              indicator = <CheckCircle className="w-3 h-3 text-green-400" />
            } else if (tab.id === 'proposal' && proposalData) {
              indicator = <CheckCircle className="w-3 h-3 text-green-400" />
            }
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 flex items-center gap-2 px-6 py-3 rounded-md text-lg font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? `${tab.color} text-white`
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <div className="text-left flex-1">
                  <div className="font-medium flex items-center gap-2">
                    {tab.name}
                    {indicator}
                  </div>
                  <div className="text-xs opacity-75">{tab.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {renderTabContent()}
      </div>
    </div>
  )
}