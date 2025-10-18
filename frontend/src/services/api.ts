/**
 * API client for backend communication
 */
import axios, { AxiosInstance } from 'axios';
import type {
  PendingManual,
  ManualListResponse,
  ManualSaveRequest,
  QARequest,
  QAResponse,
  SuggestionsResponse,
  ConversationHistoryResponse,
  DatabaseStats,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; openai_configured: boolean }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Manual management
  async processManual(file: File): Promise<PendingManual> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/manuals/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async saveManual(request: ManualSaveRequest): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post('/api/manuals/save', request);
    return response.data;
  }

  async listManuals(): Promise<ManualListResponse> {
    const response = await this.client.get('/api/manuals/');
    return response.data;
  }

  async deleteManual(filename: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.delete(`/api/manuals/${encodeURIComponent(filename)}`);
    return response.data;
  }

  async cancelUpload(filename: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/api/manuals/cancel/${encodeURIComponent(filename)}`);
    return response.data;
  }

  // Q&A
  async askQuestion(request: QARequest): Promise<QAResponse> {
    const response = await this.client.post('/api/qa/ask', request);
    return response.data;
  }

  async getSuggestions(instrumentType?: string): Promise<SuggestionsResponse> {
    const response = await this.client.post('/api/qa/suggestions', {
      instrument_type: instrumentType,
    });
    return response.data;
  }

  async getConversationHistory(): Promise<ConversationHistoryResponse> {
    const response = await this.client.get('/api/qa/history');
    return response.data;
  }

  async clearConversationHistory(): Promise<{ success: boolean; message: string }> {
    const response = await this.client.delete('/api/qa/history');
    return response.data;
  }

  // Stats
  async getStats(): Promise<DatabaseStats> {
    const response = await this.client.get('/api/stats');
    return response.data;
  }

  async resetDatabase(): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post('/api/database/reset');
    return response.data;
  }

  async getManufacturers(): Promise<{ manufacturers: string[] }> {
    const response = await this.client.get('/api/filters/manufacturers');
    return response.data;
  }

  async getInstrumentTypes(): Promise<{ instrument_types: string[] }> {
    const response = await this.client.get('/api/filters/instrument-types');
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;
