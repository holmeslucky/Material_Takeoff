/**
 * Branding Configuration - Indolent Designs
 * Easy logo and branding management
 */

export const BRANDING_CONFIG = {
  // Logo settings - easily changeable
  logo: {
    src: '/assets/indolent-designs-logo.png',
    alt: 'Indolent Designs Logo',
    width: 80,  // Larger for better visibility
    height: 80, // Larger for better visibility
    className: 'object-contain' // Maintains aspect ratio
  },
  
  // Company information
  company: {
    name: 'INDOLENT DESIGNS',
    tagline: 'Indolent Forge - Professional Steel Estimating',
    fullName: 'Indolent Designs'
  },
  
  // Fallback icon (if logo fails to load)
  fallbackIcon: {
    name: 'Building2',
    size: 'w-8 h-8',
    color: 'text-blue-500'
  }
} as const;

// Easy logo replacement function
export const updateLogo = (newLogoPath: string, width?: number, height?: number) => {
  return {
    ...BRANDING_CONFIG.logo,
    src: newLogoPath,
    ...(width && { width }),
    ...(height && { height })
  };
};