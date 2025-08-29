import React from 'react'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

interface ThemeToggleProps {
  className?: string
  size?: number
}

export default function ThemeToggle({ className = '', size = 20 }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme()

  const handleClick = () => {
    console.log('Theme toggle clicked, current theme:', theme)
    console.log('HTML classes:', document.documentElement.className)
    console.log('Body classes:', document.body.className)
    toggleTheme()
  }

  return (
    <button
      onClick={handleClick}
      className={`
        p-2 rounded-lg transition-colors duration-200 
        text-gray-600 hover:text-gray-900 hover:bg-gray-200
        dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800
        ${className}
      `}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <Moon size={size} className="transition-transform duration-200 hover:scale-110" />
      ) : (
        <Sun size={size} className="transition-transform duration-200 hover:scale-110" />
      )}
    </button>
  )
}