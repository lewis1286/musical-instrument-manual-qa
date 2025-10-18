import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useStats } from './useStats';
import { api } from '../services/api';

// Mock the API
vi.mock('../services/api');

describe('useStats Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should load stats on mount', async () => {
    const mockStats = {
      total_manuals: 5,
      total_chunks: 100,
      manufacturers: ['Moog', 'Roland'],
      instrument_types: ['synthesizer', 'mixer'],
      section_types: ['specifications', 'operation'],
    };

    vi.mocked(api.getStats).mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useStats());

    // Initially loading
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Check stats loaded correctly
    expect(result.current.stats).toEqual(mockStats);
    expect(result.current.manufacturers).toEqual(['Moog', 'Roland']);
    expect(result.current.instrumentTypes).toEqual(['synthesizer', 'mixer']);
  });

  it('should handle stats loading error', async () => {
    const mockError = { response: { data: { detail: 'Failed to load stats' } } };
    vi.mocked(api.getStats).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useStats());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load stats');
  });

  it('should reset database', async () => {
    const initialStats = {
      total_manuals: 5,
      total_chunks: 100,
      manufacturers: ['Moog'],
      instrument_types: ['synthesizer'],
      section_types: ['specifications'],
    };

    const emptyStats = {
      total_manuals: 0,
      total_chunks: 0,
      manufacturers: [],
      instrument_types: [],
      section_types: [],
    };

    vi.mocked(api.getStats)
      .mockResolvedValueOnce(initialStats)
      .mockResolvedValueOnce(emptyStats);
    vi.mocked(api.resetDatabase).mockResolvedValueOnce({ success: true, message: 'Reset successful' });

    const { result } = renderHook(() => useStats());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Initial state
    expect(result.current.stats.total_manuals).toBe(5);

    // Reset database
    await result.current.resetDatabase();

    await waitFor(() => {
      expect(result.current.stats.total_manuals).toBe(0);
    });
  });

  it('should have correct initial state', () => {
    vi.mocked(api.getStats).mockResolvedValueOnce({
      total_manuals: 0,
      total_chunks: 0,
      manufacturers: [],
      instrument_types: [],
      section_types: [],
    });

    const { result } = renderHook(() => useStats());

    expect(result.current.stats.total_manuals).toBe(0);
    expect(result.current.stats.total_chunks).toBe(0);
    expect(result.current.manufacturers).toEqual([]);
    expect(result.current.instrumentTypes).toEqual([]);
  });
});
