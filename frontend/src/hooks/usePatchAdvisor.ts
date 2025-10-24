import { useState } from 'react';
import axios from 'axios';
import type { PatchDesignRequest, PatchDesignResponse, ModuleInventoryResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export function usePatchAdvisor() {
  const [patchDesign, setPatchDesign] = useState<PatchDesignResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const designPatch = async (query: string, preferences?: Record<string, any>) => {
    setLoading(true);
    setError(null);
    setPatchDesign(null);

    try {
      const request: PatchDesignRequest = { query, preferences };
      const response = await axios.post<PatchDesignResponse>(
        `${API_BASE_URL}/api/patch/design`,
        request
      );

      setPatchDesign(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to design patch';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearPatch = () => {
    setPatchDesign(null);
    setError(null);
  };

  return {
    patchDesign,
    loading,
    error,
    designPatch,
    clearPatch,
  };
}

export function useModuleInventory() {
  const [inventory, setInventory] = useState<ModuleInventoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<ModuleInventoryResponse>(
        `${API_BASE_URL}/api/patch/module-inventory`
      );

      setInventory(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch inventory';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    inventory,
    loading,
    error,
    fetchInventory,
  };
}
