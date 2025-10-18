/**
 * Custom hook for database statistics
 */
import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import type { DatabaseStats } from '../types';

export const useStats = () => {
  const [stats, setStats] = useState<DatabaseStats>({
    total_manuals: 0,
    total_chunks: 0,
    manufacturers: [],
    instrument_types: [],
    section_types: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load stats
  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load stats on mount
  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // Reset database
  const resetDatabase = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await api.resetDatabase();
      await loadStats(); // Reload stats
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to reset database';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [loadStats]);

  return {
    stats,
    loading,
    error,
    manufacturers: stats.manufacturers,
    instrumentTypes: stats.instrument_types,
    reloadStats: loadStats,
    resetDatabase,
  };
};
