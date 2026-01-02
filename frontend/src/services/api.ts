/**
 * Women Safety AI - API Service
 * 
 * This file provides a clean interface to interact with the backend API.
 * Import and use these functions in your React components.
 * 
 * Usage:
 * import { getSafetyScore, simulateSafety } from '@/services/api';
 */

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface SafetyRequest {
  state: string;
  year: number;
}

export interface SafetyResponse {
  state: string;
  year: number;
  safety_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
}

export interface SimulateRequest {
  year: number;
  rape: number;
  kidnapping: number;
  dowry_deaths: number;
  assault_on_women: number;
  assault_on_minors: number;
  domestic_violence: number;
  trafficking: number;
}

export interface SimulateResponse {
  safety_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
}

export interface TrendDataPoint {
  year: number;
  value: number;
}

export interface TrendResponse {
  state: string;
  crime: string;
  data: TrendDataPoint[];
}

export interface LeaderboardEntry {
  state: string;
  score: number;
}

export interface ApiError {
  detail: string;
}

// ============================================
// CONFIGURATION
// ============================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unknown error occurred');
  }
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Check if the API server is healthy
 */
export async function healthCheck(): Promise<{ status: string }> {
  return apiFetch('/health');
}

/**
 * Get safety score for a specific state and year
 * 
 * @param state - State name (e.g., "Tamil Nadu")
 * @param year - Year (2001-2025)
 * @returns Safety prediction with score and risk level
 * 
 * @example
 * const result = await getSafetyScore("Tamil Nadu", 2021);
 * console.log(result.safety_score); // 41.3
 * console.log(result.risk_level);   // "Medium"
 */
export async function getSafetyScore(
  state: string,
  year: number
): Promise<SafetyResponse> {
  return apiFetch<SafetyResponse>('/predict/safety', {
    method: 'POST',
    body: JSON.stringify({ state, year }),
  });
}

/**
 * Simulate safety score based on custom crime statistics
 * 
 * @param data - Crime statistics for simulation
 * @returns Predicted safety score and risk level
 * 
 * @example
 * const result = await simulateSafety({
 *   year: 2021,
 *   rape: 100,
 *   kidnapping: 50,
 *   dowry_deaths: 20,
 *   assault_on_women: 150,
 *   assault_on_minors: 30,
 *   domestic_violence: 80,
 *   trafficking: 10
 * });
 * console.log(result.safety_score); // 38.6
 */
export async function simulateSafety(
  data: SimulateRequest
): Promise<SimulateResponse> {
  return apiFetch<SimulateResponse>('/predict/simulate', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get historical crime trends for a state and crime type
 * 
 * @param state - State name
 * @param crime - Crime type (Rape, K&A, DD, AoW, AoM, DV, WT)
 * @returns Trend data over years
 * 
 * @example
 * const trends = await getCrimeTrends("Andhra Pradesh", "Rape");
 * trends.data.forEach(point => {
 *   console.log(`${point.year}: ${point.value}`);
 * });
 */
export async function getCrimeTrends(
  state: string,
  crime: string
): Promise<TrendResponse> {
  const params = new URLSearchParams({ state, crime });
  return apiFetch<TrendResponse>(`/trends?${params}`);
}

/**
 * Get leaderboard of states ranked by safety
 * 
 * @param year - Optional year filter
 * @returns Array of states with scores (lower = safer)
 * 
 * @example
 * const leaderboard = await getLeaderboard();
 * console.log(leaderboard[0]); // { state: "Tripura", score: 2.24 }
 * 
 * const leaderboard2021 = await getLeaderboard(2021);
 */
export async function getLeaderboard(
  year?: number
): Promise<LeaderboardEntry[]> {
  const params = year ? `?year=${year}` : '';
  return apiFetch<LeaderboardEntry[]>(`/leaderboard${params}`);
}

// ============================================
// CONSTANTS
// ============================================

/**
 * Available states in the dataset
 */
export const AVAILABLE_STATES = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jammu & Kashmir',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
] as const;

/**
 * Available crime types for trend analysis
 */
export const CRIME_TYPES = {
  Rape: 'Rape',
  'K&A': 'Kidnapping & Abduction',
  DD: 'Dowry Deaths',
  AoW: 'Assault on Women',
  AoM: 'Assault on Minors',
  DV: 'Domestic Violence',
  WT: 'Women Trafficking',
} as const;

/**
 * Year range in dataset
 */
export const YEAR_RANGE = {
  min: 2001,
  max: 2025,
} as const;

/**
 * Risk level colors for UI
 */
export const RISK_COLORS = {
  Low: '#10b981',   // green
  Medium: '#f59e0b', // orange
  High: '#ef4444',   // red
} as const;

/**
 * Get color for risk level
 */
export function getRiskColor(riskLevel: 'Low' | 'Medium' | 'High'): string {
  return RISK_COLORS[riskLevel];
}

/**
 * Get description for risk level
 */
export function getRiskDescription(riskLevel: 'Low' | 'Medium' | 'High'): string {
  const descriptions = {
    Low: 'Relatively safer region. Standard safety practices recommended.',
    Medium: 'Moderate risk area. Be cautious and prefer travelling with company.',
    High: 'High risk area. Avoid travelling alone, especially at night. Share live location.',
  };
  return descriptions[riskLevel];
}
