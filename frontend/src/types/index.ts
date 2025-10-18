/**
 * TypeScript types matching backend Pydantic models
 */

// Manual-related types
export interface ManualMetadata {
  filename: string;
  display_name: string;
  manufacturer?: string;
  model?: string;
  instrument_type?: string;
  total_pages: number;
  chunk_count?: number;
}

export interface PendingManual {
  temp_file_path: string;
  original_filename: string;
  metadata: ManualMetadata;
  chunk_count: number;
}

export interface ManualListItem {
  filename: string;
  display_name: string;
  manufacturer: string;
  model: string;
  instrument_type: string;
  total_pages: number;
  chunk_count: number;
}

export interface ManualListResponse {
  manuals: ManualListItem[];
  total_count: number;
}

export interface ManualSaveRequest {
  filename: string;
  display_name: string;
  manufacturer?: string;
  model?: string;
  instrument_type?: string;
}

// Q&A related types
export interface QASource {
  filename: string;
  display_name: string;
  page_number: number;
  manufacturer: string;
  model: string;
  instrument_type: string;
  section_type: string;
  content_preview: string;
}

export interface QARequest {
  question: string;
  max_sources?: number;
  instrument_type?: string;
  manufacturer?: string;
}

export interface QAResponse {
  answer: string;
  sources: QASource[];
  query: string;
}

export interface SuggestionsResponse {
  suggestions: string[];
}

export interface ConversationHistoryResponse {
  history: Array<{
    question: string;
    answer: string;
  }>;
}

// Stats related types
export interface DatabaseStats {
  total_manuals: number;
  total_chunks: number;
  manufacturers: string[];
  instrument_types: string[];
  section_types: string[];
}

// General response types
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
}

// UI state types
export interface UploadState {
  isUploading: boolean;
  progress: number;
  error?: string;
}

export interface FilterState {
  instrumentType: string;
  manufacturer: string;
  maxSources: number;
}
