import React, { useState } from 'react'
import { Building2 } from 'lucide-react'
import { BRANDING_CONFIG } from '../config/branding'

interface LogoProps {
  className?: string
  showFallback?: boolean
  width?: number
  height?: number
}

export default function Logo({ 
  className = '', 
  showFallback = true, 
  width = BRANDING_CONFIG.logo.width,
  height = BRANDING_CONFIG.logo.height 
}: LogoProps) {
  const [imageError, setImageError] = useState(false)
  
  const handleImageError = () => {
    setImageError(true)
  }

  // If image failed to load and fallback is enabled, show icon
  if (imageError && showFallback) {
    return (
      <Building2 
        className={`${BRANDING_CONFIG.fallbackIcon.size} ${BRANDING_CONFIG.fallbackIcon.color} ${className}`} 
      />
    )
  }

  // If image failed and no fallback, don't render anything
  if (imageError && !showFallback) {
    return null
  }

  return (
    <img
      src={BRANDING_CONFIG.logo.src}
      alt={BRANDING_CONFIG.logo.alt}
      width={width}
      height={height}
      className={`${BRANDING_CONFIG.logo.className} ${className}`}
      onError={handleImageError}
      style={{ 
        maxWidth: `${width}px`, 
        maxHeight: `${height}px` 
      }}
    />
  )
}