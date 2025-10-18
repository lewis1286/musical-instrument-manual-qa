/**
 * Custom hook for manual management
 */
import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import type { ManualListItem, PendingManual, ManualSaveRequest } from '../types';

export const useManuals = () => {
  const [manuals, setManuals] = useState<ManualListItem[]>([]);
  const [pendingManual, setPendingManual] = useState<PendingManual | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load manuals
  const loadManuals = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.listManuals();
      setManuals(response.manuals);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load manuals');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load manuals on mount
  useEffect(() => {
    loadManuals();
  }, [loadManuals]);

  // Process uploaded file
  const processManual = useCallback(async (file: File) => {
    try {
      setLoading(true);
      setError(null);
      const pending = await api.processManual(file);
      setPendingManual(pending);
      return pending;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to process manual';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save manual with metadata
  const saveManual = useCallback(async (request: ManualSaveRequest) => {
    try {
      setLoading(true);
      setError(null);
      await api.saveManual(request);
      setPendingManual(null);
      await loadManuals(); // Reload list
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to save manual';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [loadManuals]);

  // Cancel upload
  const cancelUpload = useCallback(async () => {
    if (!pendingManual) return;

    try {
      setLoading(true);
      setError(null);
      await api.cancelUpload(pendingManual.original_filename);
      setPendingManual(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to cancel upload');
    } finally {
      setLoading(false);
    }
  }, [pendingManual]);

  // Delete manual
  const deleteManual = useCallback(async (filename: string) => {
    try {
      setLoading(true);
      setError(null);
      await api.deleteManual(filename);
      await loadManuals(); // Reload list
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete manual';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [loadManuals]);

  return {
    manuals,
    pendingManual,
    loading,
    error,
    processManual,
    saveManual,
    cancelUpload,
    deleteManual,
    reloadManuals: loadManuals,
  };
};
