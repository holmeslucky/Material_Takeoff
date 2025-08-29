import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>('dark') // Default to dark theme

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('indolent-forge-theme') as Theme
    
    if (savedTheme) {
      setThemeState(savedTheme)
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setThemeState(prefersDark ? 'dark' : 'light')
    }
  }, [])

  // Apply theme class to document
  useEffect(() => {
    const root = document.documentElement
    const body = document.body
    
    // Apply to HTML root for Tailwind dark mode
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    
    // Update body classes
    body.classList.remove('light', 'dark', 'bg-gray-950', 'text-gray-100', 'bg-gray-50', 'text-gray-900')
    body.classList.add(theme)
    
    if (theme === 'dark') {
      body.classList.add('bg-gray-950', 'text-gray-100')
    } else {
      body.classList.add('bg-gray-50', 'text-gray-900')
    }
    
    // Update AG Grid theme class
    body.className = body.className
      .replace(/ag-theme-alpine(-dark)?/g, '')
      .trim()
    
    body.classList.add(theme === 'dark' ? 'ag-theme-alpine-dark' : 'ag-theme-alpine')
    
    // Save to localStorage
    localStorage.setItem('indolent-forge-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light')
  }

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}