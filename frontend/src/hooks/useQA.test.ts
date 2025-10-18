import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useQA } from './useQA';
import { api } from '../services/api';

// Mock the API
vi.mock('../services/api');

describe('useQA Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should ask a question and get answer', async () => {
    const mockResponse = {
      answer: 'Connect the MIDI OUT to your computer',
      sources: [
        {
          filename: 'Moog-Manual.pdf',
          display_name: 'Moog Minimoog Manual',
          page_number: 5,
          manufacturer: 'Moog',
          model: 'Minimoog',
          instrument_type: 'synthesizer',
          section_type: 'connections',
          content_preview: 'MIDI connections...',
        },
      ],
      query: 'How do I connect MIDI?',
    };

    vi.mocked(api.askQuestion).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useQA());

    await act(async () => {
      await result.current.askQuestion({ question: 'How do I connect MIDI?' });
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.answer).toBe('Connect the MIDI OUT to your computer');
    expect(result.current.sources).toHaveLength(1);
    expect(result.current.sources[0].display_name).toBe('Moog Minimoog Manual');
  });

  it('should handle question error', async () => {
    const mockError = { response: { data: { detail: 'No manuals uploaded' } } };
    vi.mocked(api.askQuestion).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useQA());

    await expect(
      act(async () => {
        await result.current.askQuestion({ question: 'Test question?' });
      })
    ).rejects.toThrow('No manuals uploaded');

    expect(result.current.error).toBe('No manuals uploaded');
  });

  it('should clear conversation history', async () => {
    vi.mocked(api.clearConversationHistory).mockResolvedValueOnce({ success: true, message: 'Cleared' });

    const mockResponse = {
      answer: 'Test answer',
      sources: [],
      query: 'Test question',
    };

    vi.mocked(api.askQuestion).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useQA());

    // Ask a question first
    await act(async () => {
      await result.current.askQuestion({ question: 'Test question?' });
    });

    await waitFor(() => {
      expect(result.current.answer).toBe('Test answer');
    });

    // Clear history
    await act(async () => {
      await result.current.clearHistory();
    });

    expect(result.current.answer).toBe('');
    expect(result.current.sources).toEqual([]);
  });

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useQA());

    expect(result.current.answer).toBe('');
    expect(result.current.sources).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should update conversation history', async () => {
    const mockResponse1 = {
      answer: 'Answer 1',
      sources: [],
      query: 'Question 1',
    };

    const mockResponse2 = {
      answer: 'Answer 2',
      sources: [],
      query: 'Question 2',
    };

    vi.mocked(api.askQuestion)
      .mockResolvedValueOnce(mockResponse1)
      .mockResolvedValueOnce(mockResponse2);

    const { result } = renderHook(() => useQA());

    // Ask first question
    await act(async () => {
      await result.current.askQuestion({ question: 'Question 1' });
    });

    await waitFor(() => {
      expect(result.current.conversation).toHaveLength(1);
    });

    // Ask second question
    await act(async () => {
      await result.current.askQuestion({ question: 'Question 2' });
    });

    await waitFor(() => {
      expect(result.current.conversation).toHaveLength(2);
    });

    expect(result.current.conversation[0].question).toBe('Question 1');
    expect(result.current.conversation[1].question).toBe('Question 2');
  });
});
