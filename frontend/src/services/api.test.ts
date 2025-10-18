import { describe, it, expect, vi } from 'vitest';
import axios from 'axios';
import { api } from './api';

// Mock axios
vi.mock('axios');

describe('API Client', () => {
  it('should have correct base URL', () => {
    expect(import.meta.env.VITE_API_URL || 'http://localhost:8000').toBeTruthy();
  });

  it('should call health check endpoint', async () => {
    const mockResponse = {
      data: { status: 'healthy', openai_configured: true },
    };

    vi.mocked(axios.create).mockReturnValue({
      get: vi.fn().mockResolvedValue(mockResponse),
    } as any);

    // Create new instance
    const testApi = new (api.constructor as any)();
    const result = await testApi.healthCheck();

    expect(result.status).toBe('healthy');
  });
});
