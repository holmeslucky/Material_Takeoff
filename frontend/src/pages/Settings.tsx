import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save, Database, Calculator, Building, User, FileText, Monitor, ChevronDown, ChevronRight, Mail, Phone, Globe, MapPin } from 'lucide-react'

interface CompanySettings {
  name: string
  address: string
  phone: string
  mobile: string
  website: string
  email: string
  contact: string
}

interface LaborSettings {
  base_rate: number
  markup_percent: number
  handling_percent: number
  mode: string
}

interface UserPreferences {
  auto_save: boolean
  default_project_template: string
  recent_materials_count: number
  date_format: string
  show_grid_lines: boolean
  show_tooltips: boolean
}

interface CalculationPreferences {
  material_cost_rounding: number
  labor_cost_rounding: number
  default_units: string
  steel_density: number
}

interface ExportSettings {
  excel_template: string
  report_format: string
  page_orientation: string
  auto_backup_frequency: string
}

interface SystemConfig {
  cache_enabled: boolean
  search_result_limit: number
  session_timeout_minutes: number
  enable_notifications: boolean
}

export default function Settings() {
  const [companySettings, setCompanySettings] = useState<CompanySettings>({
    name: 'Capitol Engineering Company',
    address: '724 E Southern Pacific Dr, Phoenix AZ 85034',
    phone: '602-281-6517',
    mobile: '951-732-1514',
    website: 'www.capitolaz.com',
    email: 'sales@capitolaz.com',
    contact: 'Blake Holmes'
  })
  
  const [laborSettings, setLaborSettings] = useState<LaborSettings>({
    base_rate: 120.00,
    markup_percent: 35.0,
    handling_percent: 20.0,
    mode: 'auto'
  })
  
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    auto_save: true,
    default_project_template: 'Standard Steel',
    recent_materials_count: 20,
    date_format: 'MM/DD/YYYY',
    show_grid_lines: true,
    show_tooltips: true
  })
  
  const [calculationPreferences, setCalculationPreferences] = useState<CalculationPreferences>({
    material_cost_rounding: 0.01,
    labor_cost_rounding: 0.01,
    default_units: 'Imperial',
    steel_density: 40.8
  })
  
  const [exportSettings, setExportSettings] = useState<ExportSettings>({
    excel_template: 'Standard',
    report_format: 'Detailed',
    page_orientation: 'Portrait',
    auto_backup_frequency: 'Weekly'
  })
  
  const [systemConfig, setSystemConfig] = useState<SystemConfig>({
    cache_enabled: true,
    search_result_limit: 100,
    session_timeout_minutes: 480,
    enable_notifications: true
  })

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  
  // Collapsible section states
  const [expandedSections, setExpandedSections] = useState({
    company: true,
    labor: true,
    user: false,
    calculation: false,
    export: false,
    system: false,
    database: false
  })
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section as keyof typeof prev] }))
  }

  useEffect(() => {
    // Load settings from API
    const loadSettings = async () => {
      try {
        // Load company settings
        const companyResponse = await fetch('http://localhost:7000/api/v1/settings/company')
        if (companyResponse.ok) {
          const companyData = await companyResponse.json()
          setCompanySettings(companyData)
        }

        // Load labor settings
        const laborResponse = await fetch('http://localhost:7000/api/v1/settings/labor')
        if (laborResponse.ok) {
          const laborData = await laborResponse.json()
          setLaborSettings(laborData)
        }
        
        // Load user preferences
        const userResponse = await fetch('http://localhost:7000/api/v1/settings/user-preferences')
        if (userResponse.ok) {
          const userData = await userResponse.json()
          setUserPreferences(userData)
        }
        
        // Load calculation preferences
        const calcResponse = await fetch('http://localhost:7000/api/v1/settings/calculation-preferences')
        if (calcResponse.ok) {
          const calcData = await calcResponse.json()
          setCalculationPreferences(calcData)
        }
        
        // Load export settings
        const exportResponse = await fetch('http://localhost:7000/api/v1/settings/export-settings')
        if (exportResponse.ok) {
          const exportData = await exportResponse.json()
          setExportSettings(exportData)
        }
        
        // Load system config
        const systemResponse = await fetch('http://localhost:7000/api/v1/settings/system-config')
        if (systemResponse.ok) {
          const systemData = await systemResponse.json()
          setSystemConfig(systemData)
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      } finally {
        setLoading(false)
      }
    }

    loadSettings()
  }, [])

  const saveSettings = async () => {
    setSaving(true)
    setSaved(false)

    try {
      // Save all settings sections
      const responses = await Promise.all([
        fetch('http://localhost:7000/api/v1/settings/company', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(companySettings)
        }),
        fetch('http://localhost:7000/api/v1/settings/labor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(laborSettings)
        }),
        fetch('http://localhost:7000/api/v1/settings/user-preferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userPreferences)
        }),
        fetch('http://localhost:7000/api/v1/settings/calculation-preferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(calculationPreferences)
        }),
        fetch('http://localhost:7000/api/v1/settings/export-settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(exportSettings)
        }),
        fetch('http://localhost:7000/api/v1/settings/system-config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(systemConfig)
        })
      ])

      if (responses.every(response => response.ok)) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="h-full bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading settings...</p>
        </div>
      </div>
    )
  }
  
  // Reusable collapsible section component
  const SettingsSection: React.FC<{
    title: string;
    icon: React.ReactNode;
    sectionKey: keyof typeof expandedSections;
    children: React.ReactNode;
    description?: string;
  }> = ({ title, icon, sectionKey, children, description }) => (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div 
        className="flex items-center justify-between p-6 cursor-pointer hover:bg-gray-850 transition-colors"
        onClick={() => toggleSection(sectionKey)}
      >
        <div className="flex items-center gap-3">
          {icon}
          <div>
            <h2 className="text-xl font-semibold text-white">{title}</h2>
            {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
          </div>
        </div>
        {expandedSections[sectionKey] ? 
          <ChevronDown className="w-5 h-5 text-gray-400" /> : 
          <ChevronRight className="w-5 h-5 text-gray-400" />
        }
      </div>
      {expandedSections[sectionKey] && (
        <div className="px-6 pb-6 border-t border-gray-800">
          {children}
        </div>
      )}
    </div>
  )

  return (
    <div className="h-full bg-gray-950 overflow-auto">
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-white">Capitol Takeoff Settings</h1>
          </div>
          <p className="text-gray-400">Configure company information, preferences, and system behavior</p>
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Company Information */}
          <SettingsSection 
            title="Company Information"
            icon={<Building className="w-5 h-5 text-blue-400" />}
            sectionKey="company"
            description="Capitol Engineering Company profile and contact details"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Company Name</label>
                <input
                  type="text"
                  value={companySettings.name}
                  onChange={(e) => setCompanySettings({...companySettings, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Contact Person</label>
                <input
                  type="text"
                  value={companySettings.contact}
                  onChange={(e) => setCompanySettings({...companySettings, contact: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  Address
                </label>
                <input
                  type="text"
                  value={companySettings.address}
                  onChange={(e) => setCompanySettings({...companySettings, address: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
                  <Phone className="w-4 h-4" />
                  Phone
                </label>
                <input
                  type="text"
                  value={companySettings.phone}
                  onChange={(e) => setCompanySettings({...companySettings, phone: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Mobile</label>
                <input
                  type="text"
                  value={companySettings.mobile}
                  onChange={(e) => setCompanySettings({...companySettings, mobile: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  Website
                </label>
                <input
                  type="text"
                  value={companySettings.website}
                  onChange={(e) => setCompanySettings({...companySettings, website: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
                  <Mail className="w-4 h-4" />
                  Email
                </label>
                <input
                  type="email"
                  value={companySettings.email}
                  onChange={(e) => setCompanySettings({...companySettings, email: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </SettingsSection>

          {/* Labor Rate Settings */}
          <SettingsSection 
            title="Labor Rate Configuration"
            icon={<Calculator className="w-5 h-5 text-green-400" />}
            sectionKey="labor"
            description="Base rates and calculation settings for labor costs"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Base Hourly Rate ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={laborSettings.base_rate}
                  onChange={(e) => setLaborSettings({...laborSettings, base_rate: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">From master takeoff labor chart</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Markup (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={laborSettings.markup_percent}
                  onChange={(e) => setLaborSettings({...laborSettings, markup_percent: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Company markup percentage</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Handling (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={laborSettings.handling_percent}
                  onChange={(e) => setLaborSettings({...laborSettings, handling_percent: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Material handling percentage</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Labor Mode</label>
                <select
                  value={laborSettings.mode}
                  onChange={(e) => setLaborSettings({...laborSettings, mode: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="auto">Auto Calculation</option>
                  <option value="manual">Manual Override</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">Labor calculation method</p>
              </div>
            </div>
          </SettingsSection>

          {/* User Preferences */}
          <SettingsSection 
            title="User Preferences"
            icon={<User className="w-5 h-5 text-purple-400" />}
            sectionKey="user"
            description="Personal settings and interface preferences"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-300">Auto-save Settings</label>
                  <p className="text-xs text-gray-500">Automatically save changes</p>
                </div>
                <input
                  type="checkbox"
                  checked={userPreferences.auto_save}
                  onChange={(e) => setUserPreferences({...userPreferences, auto_save: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Default Project Template</label>
                <select
                  value={userPreferences.default_project_template}
                  onChange={(e) => setUserPreferences({...userPreferences, default_project_template: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Standard Steel">Standard Steel</option>
                  <option value="Heavy Industrial">Heavy Industrial</option>
                  <option value="Light Commercial">Light Commercial</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Recent Materials Count</label>
                <input
                  type="number"
                  min="5"
                  max="50"
                  value={userPreferences.recent_materials_count}
                  onChange={(e) => setUserPreferences({...userPreferences, recent_materials_count: parseInt(e.target.value) || 20})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Date Format</label>
                <select
                  value={userPreferences.date_format}
                  onChange={(e) => setUserPreferences({...userPreferences, date_format: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-300">Show Grid Lines</label>
                  <p className="text-xs text-gray-500">Display grid lines in tables</p>
                </div>
                <input
                  type="checkbox"
                  checked={userPreferences.show_grid_lines}
                  onChange={(e) => setUserPreferences({...userPreferences, show_grid_lines: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-300">Show Tooltips</label>
                  <p className="text-xs text-gray-500">Enable helpful tooltips</p>
                </div>
                <input
                  type="checkbox"
                  checked={userPreferences.show_tooltips}
                  onChange={(e) => setUserPreferences({...userPreferences, show_tooltips: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
              </div>
            </div>
          </SettingsSection>

          {/* Calculation Preferences */}
          <SettingsSection 
            title="Calculation Preferences"
            icon={<Calculator className="w-5 h-5 text-orange-400" />}
            sectionKey="calculation"
            description="Rounding rules and calculation standards"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Material Cost Rounding</label>
                <select
                  value={calculationPreferences.material_cost_rounding}
                  onChange={(e) => setCalculationPreferences({...calculationPreferences, material_cost_rounding: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0.01}>Nearest $0.01</option>
                  <option value={0.05}>Nearest $0.05</option>
                  <option value={1.00}>Nearest $1.00</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Labor Cost Rounding</label>
                <select
                  value={calculationPreferences.labor_cost_rounding}
                  onChange={(e) => setCalculationPreferences({...calculationPreferences, labor_cost_rounding: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0.01}>Nearest $0.01</option>
                  <option value={0.05}>Nearest $0.05</option>
                  <option value={1.00}>Nearest $1.00</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Default Units</label>
                <select
                  value={calculationPreferences.default_units}
                  onChange={(e) => setCalculationPreferences({...calculationPreferences, default_units: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Imperial">Imperial (ft, in, lbs)</option>
                  <option value="Metric">Metric (m, cm, kg)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Steel Density (lb/ft³)</label>
                <input
                  type="number"
                  step="0.1"
                  value={calculationPreferences.steel_density}
                  onChange={(e) => setCalculationPreferences({...calculationPreferences, steel_density: parseFloat(e.target.value) || 40.8})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Standard steel density for calculations</p>
              </div>
            </div>
          </SettingsSection>

          {/* Export Settings */}
          <SettingsSection 
            title="Export & Reports"
            icon={<FileText className="w-5 h-5 text-cyan-400" />}
            sectionKey="export"
            description="Export templates and report formatting options"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Excel Template</label>
                <select
                  value={exportSettings.excel_template}
                  onChange={(e) => setExportSettings({...exportSettings, excel_template: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Standard">Standard Layout</option>
                  <option value="Professional">Professional Letterhead</option>
                  <option value="Custom">Custom Template</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Report Format</label>
                <select
                  value={exportSettings.report_format}
                  onChange={(e) => setExportSettings({...exportSettings, report_format: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Detailed">Detailed Breakdown</option>
                  <option value="Summary">Summary Only</option>
                  <option value="Both">Both Summary & Detail</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Page Orientation</label>
                <select
                  value={exportSettings.page_orientation}
                  onChange={(e) => setExportSettings({...exportSettings, page_orientation: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Portrait">Portrait</option>
                  <option value="Landscape">Landscape</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Auto-Backup</label>
                <select
                  value={exportSettings.auto_backup_frequency}
                  onChange={(e) => setExportSettings({...exportSettings, auto_backup_frequency: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Daily">Daily</option>
                  <option value="Weekly">Weekly</option>
                  <option value="Monthly">Monthly</option>
                  <option value="Manual">Manual Only</option>
                </select>
              </div>
            </div>
          </SettingsSection>

          {/* System Configuration */}
          <SettingsSection 
            title="System Configuration"
            icon={<Monitor className="w-5 h-5 text-red-400" />}
            sectionKey="system"
            description="Performance and system-level settings"
          >
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-300">Enable Caching</label>
                  <p className="text-xs text-gray-500">Improve performance with caching</p>
                </div>
                <input
                  type="checkbox"
                  checked={systemConfig.cache_enabled}
                  onChange={(e) => setSystemConfig({...systemConfig, cache_enabled: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Search Result Limit</label>
                <input
                  type="number"
                  min="10"
                  max="1000"
                  value={systemConfig.search_result_limit}
                  onChange={(e) => setSystemConfig({...systemConfig, search_result_limit: parseInt(e.target.value) || 100})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Session Timeout (minutes)</label>
                <select
                  value={systemConfig.session_timeout_minutes}
                  onChange={(e) => setSystemConfig({...systemConfig, session_timeout_minutes: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={60}>1 Hour</option>
                  <option value={240}>4 Hours</option>
                  <option value={480}>8 Hours</option>
                  <option value={1440}>24 Hours</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-300">Enable Notifications</label>
                  <p className="text-xs text-gray-500">System alerts and reminders</p>
                </div>
                <input
                  type="checkbox"
                  checked={systemConfig.enable_notifications}
                  onChange={(e) => setSystemConfig({...systemConfig, enable_notifications: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
              </div>
            </div>
          </SettingsSection>

          {/* Database Status */}
          <SettingsSection 
            title="Database Status"
            icon={<Database className="w-5 h-5 text-green-400" />}
            sectionKey="database"
            description="Current database connection status"
          >
            <div className="mt-4 space-y-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-medium">Material Database</h3>
                    <p className="text-sm text-gray-400">1,918+ steel shapes and pricing data</p>
                  </div>
                  <span className="text-green-400 text-sm">● Connected</span>
                </div>
              </div>

              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-medium">Project Storage</h3>
                    <p className="text-sm text-gray-400">SQLite database for projects and settings</p>
                  </div>
                  <span className="text-green-400 text-sm">● Connected</span>
                </div>
              </div>

              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-medium">Labor Management</h3>
                    <p className="text-sm text-gray-400">Dynamic rates and coating systems</p>
                  </div>
                  <span className="text-green-400 text-sm">● Active</span>
                </div>
              </div>
            </div>
          </SettingsSection>
        </div>

        {/* Save Button */}
        <div className="mt-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {saved && (
              <span className="text-green-400 text-sm">Settings saved successfully!</span>
            )}
          </div>
          
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}