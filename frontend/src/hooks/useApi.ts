/**
 * React Hooks for Women Safety AI API
 * 
 * Custom hooks that provide loading states, error handling,
 * and data fetching for all API endpoints.
 * 
 * Usage:
 * import { useSafetyScore, useSimulation } from '@/hooks/useApi';
 */

import { useState, useCallback } from 'react';
import {
  getSafetyScore,
  simulateSafety,
  getCrimeTrends,
  getLeaderboard,
  healthCheck,
  SafetyResponse,
  SimulateRequest,
  SimulateResponse,
  TrendResponse,
  LeaderboardEntry,
} from '@/services/api';

// ============================================
// TYPES
// ============================================

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiActions {
  clearError: () => void;
}

// ============================================
// HOOKS
// ============================================

/**
 * Hook for checking API health
 */
export function useHealthCheck() {
  const [state, setState] = useState<UseApiState<{ status: string }>>({
    data: null,
    loading: false,
    error: null,
  });

  const check = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await healthCheck();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    check,
    clearError,
  };
}

/**
 * Hook for getting safety scores
 * 
 * @example
 * const { data, loading, error, checkSafety } = useSafetyScore();
 * 
 * const handleCheck = async () => {
 *   const result = await checkSafety("Tamil Nadu", 2021);
 *   if (result) {
 *     console.log(result.safety_score);
 *   }
 * };
 */
export function useSafetyScore() {
  const [state, setState] = useState<UseApiState<SafetyResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const checkSafety = useCallback(async (stateName: string, year: number) => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await getSafetyScore(stateName, year);
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    checkSafety,
    clearError,
  };
}

/**
 * Hook for crime simulation
 * 
 * @example
 * const { data, loading, error, simulate } = useSimulation();
 * 
 * const handleSimulate = async () => {
 *   const result = await simulate({
 *     year: 2021,
 *     rape: 100,
 *     kidnapping: 50,
 *     dowry_deaths: 20,
 *     assault_on_women: 150,
 *     assault_on_minors: 30,
 *     domestic_violence: 80,
 *     trafficking: 10
 *   });
 * };
 */
export function useSimulation() {
  const [state, setState] = useState<UseApiState<SimulateResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const simulate = useCallback(async (data: SimulateRequest) => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await simulateSafety(data);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    simulate,
    clearError,
  };
}

/**
 * Hook for getting crime trends
 * 
 * @example
 * const { data, loading, error, fetchTrends } = useCrimeTrends();
 * 
 * const handleFetch = async () => {
 *   const trends = await fetchTrends("Andhra Pradesh", "Rape");
 *   if (trends) {
 *     console.log(trends.data); // Array of year-value pairs
 *   }
 * };
 */
export function useCrimeTrends() {
  const [state, setState] = useState<UseApiState<TrendResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchTrends = useCallback(async (stateName: string, crime: string) => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await getCrimeTrends(stateName, crime);
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchTrends,
    clearError,
  };
}

/**
 * Hook for getting leaderboard
 * 
 * @example
 * const { data, loading, error, fetchLeaderboard } = useLeaderboard();
 * 
 * // Get all-time leaderboard
 * const handleFetchAll = async () => {
 *   const leaderboard = await fetchLeaderboard();
 * };
 * 
 * // Get leaderboard for specific year
 * const handleFetchYear = async () => {
 *   const leaderboard = await fetchLeaderboard(2021);
 * };
 */
export function useLeaderboard() {
  const [state, setState] = useState<UseApiState<LeaderboardEntry[]>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchLeaderboard = useCallback(async (year?: number) => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await getLeaderboard(year);
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchLeaderboard,
    clearError,
  };
}
