/**
 * API Configuration - Capitol Engineering Company
 * Handles dynamic API base URL for development and production
 */

// Get API base URL from environment or default to current origin in production
const getApiBaseUrl = (): string => {
  // In development, use environment variable or default
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_API_URL || 'http://localhost:7000';
  }
  
  // In production, use current domain (Railway will serve both frontend and backend)
  return window.location.origin;
};

export const API_BASE_URL = getApiBaseUrl();

// API endpoints configuration
export const API_ENDPOINTS = {
  // Takeoff endpoints
  TAKEOFF_MATERIALS_SEARCH: '/api/v1/takeoff/materials/search',
  TAKEOFF_CALCULATE: '/api/v1/takeoff/calculate',
  TAKEOFF_DESCRIPTIONS_SEARCH: '/api/v1/takeoff/descriptions/search',
  TAKEOFF_SAVE: '/api/v1/takeoff/projects',
  
  // Project endpoints
  PROJECTS: '/api/v1/projects',
  
  // Labor management endpoints
  LABOR_OPERATIONS: '/api/v1/labor-mgmt/operations',
  LABOR_COATINGS: '/api/v1/labor-mgmt/coatings',
  LABOR_SETTINGS: '/api/v1/labor-mgmt/settings',
  
  // Settings endpoints
  SETTINGS: '/api/v1/settings',
  
  // Materials endpoints
  MATERIALS: '/api/v1/materials',
  
  // Nesting endpoints
  NESTING: '/api/v1/nesting',
  
  // Proposals endpoints
  PROPOSALS: '/api/v1/proposals',
  
  // Templates endpoints
  TEMPLATES: '/api/v1/templates'
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string, params?: Record<string, string | number>): string => {
  let url = `${API_BASE_URL}${endpoint}`;
  
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      searchParams.append(key, String(value));
    });
    url += `?${searchParams.toString()}`;
  }
  
  return url;
};