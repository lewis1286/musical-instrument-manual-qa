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

// Patch Advisor types
export interface PatchDesignRequest {
  query: string;
  preferences?: Record<string, any>;
}

export interface ModuleInfo {
  type: string;
  name: string;
  manufacturer: string;
  model: string;
  confidence: number;
  features: string[];
}

export interface MissingModuleInfo {
  type: string;
  role: string;
  specifications: string[];
  optional: boolean;
}

export interface PatchInstruction {
  step: number;
  action: string;
  module: string;
  manual_reference?: string;
  settings: Record<string, string>;
}

export interface AlternativeModule {
  type: string;
  note: string;
}

export interface PatchDesignResponse {
  success: boolean;
  query: string;
  sound_type?: string;
  characteristics: string[];
  synthesis_approach: string;
  patch_template?: string;
  mermaid_diagram: string;
  instructions: PatchInstruction[];
  available_modules: ModuleInfo[];
  missing_modules: MissingModuleInfo[];
  suggested_alternatives: Array<{
    missing_module: string;
    alternatives: AlternativeModule[];
  }>;
  match_quality: number;
  parameter_suggestions: Record<string, string>;
  final_response: string;
  agent_messages: string[];
  errors: string[];
  error?: string;
}

export interface ModuleInventoryItem {
  filename: string;
  manual: string;
  manufacturer: string;
  model: string;
  capabilities: string[];
}

export interface ModuleInventoryResponse {
  inventories: ModuleInventoryItem[];
  total_count: number;
}
