/**
 * Custom hook for Q&A functionality
 */
import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { QARequest, QAResponse } from '../types';

interface ConversationItem {
  question: string;
  answer: string;
  sources: number;
}

export const useQA = () => {
  const [currentAnswer, setCurrentAnswer] = useState<QAResponse | null>(null);
  const [conversation, setConversation] = useState<ConversationItem[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Ask a question
  const askQuestion = useCallback(async (request: QARequest) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.askQuestion(request);
      setCurrentAnswer(response);

      // Add to conversation history
      setConversation(prev => [
        ...prev,
        {
          question: request.question,
          answer: response.answer,
          sources: response.sources.length,
        },
      ]);

      return response;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to get answer';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load suggestions
  const loadSuggestions = useCallback(async (instrumentType?: string) => {
    try {
      const response = await api.getSuggestions(instrumentType);
      setSuggestions(response.suggestions);
    } catch (err: any) {
      console.error('Failed to load suggestions:', err);
    }
  }, []);

  // Clear conversation
  const clearConversation = useCallback(async () => {
    try {
      await api.clearConversationHistory();
      setConversation([]);
      setCurrentAnswer(null);
    } catch (err: any) {
      console.error('Failed to clear conversation:', err);
    }
  }, []);

  return {
    answer: currentAnswer?.answer || '',
    sources: currentAnswer?.sources || [],
    currentAnswer,
    conversation,
    suggestions,
    loading,
    error,
    askQuestion,
    loadSuggestions,
    clearHistory: clearConversation,
  };
};
