export interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'analyst'
  is_active: boolean
  created_at: string
  updated_at?: string
  last_login?: string
}

export interface Project {
  id: number
  name: string
  description?: string
  client_name: string
  status: 'active' | 'completed' | 'archived' | 'on_hold'
  materiality_threshold: number
  materiality_percentage: number
  owner_id: number
  created_by: number
  created_at: string
  updated_at?: string
  completed_at?: string
  total_documents: number
  processed_documents: number
  total_adjustments: number
  reviewed_adjustments: number
  qa_completed: boolean
  qa_notes?: string
  completion_percentage: number
  adjustment_review_percentage: number
  is_ready_for_export: boolean
}

export interface Document {
  id: number
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  document_type: 'general_ledger' | 'profit_loss' | 'balance_sheet' | 'trial_balance' | 'payroll' | 'cash_flow' | 'supporting_docs' | 'other'
  classification_confidence: number
  status: 'pending' | 'processing' | 'completed' | 'error'
  error_message?: string
  project_id: number
  uploaded_by: number
  row_count: number
  column_count: number
  created_at: string
  updated_at?: string
  processed_at?: string
  processing_time?: number
  processing_notes?: string
  file_extension: string
  is_excel: boolean
  is_csv: boolean
  is_pdf: boolean
  is_word: boolean
  is_processed: boolean
  has_error: boolean
}

export interface Adjustment {
  id: number
  title: string
  description: string
  adjustment_type: string
  amount: number
  debit_account?: string
  credit_account?: string
  narrative?: string
  confidence_score: number
  rule_applied?: string
  status: 'pending' | 'accepted' | 'rejected' | 'modified'
  reviewer_notes?: string
  is_material: boolean
  materiality_reason?: string
  project_id: number
  source_document_id?: number
  created_by: number
  reviewed_by?: number
  created_at: string
  updated_at?: string
  reviewed_at?: string
  processing_time?: number
  ai_model_used?: string
  is_accepted: boolean
  is_rejected: boolean
  is_modified: boolean
  is_pending: boolean
  absolute_amount: number
  is_high_confidence: boolean
  confidence_percentage: number
}

export interface Question {
  id: number
  title: string
  description: string
  question_type: 'text' | 'multiple_choice' | 'yes_no' | 'number' | 'date' | 'file_upload'
  options?: string[]
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'pending' | 'answered' | 'clarification_needed' | 'closed'
  is_ai_generated: boolean
  ai_context?: string
  confidence_score: number
  project_id: number
  assigned_to?: number
  created_by: number
  created_at: string
  updated_at?: string
  due_date?: string
  is_answered: boolean
  is_overdue: boolean
}

export interface Answer {
  id: number
  question_id: number
  answered_by: number
  answer_text?: string
  answer_number?: number
  answer_date?: string
  answer_boolean?: boolean
  answer_file_path?: string
  notes?: string
  is_final: boolean
  created_at: string
  updated_at?: string
  answer_value: string | number | boolean | null
}

export interface Report {
  id: number
  title: string
  description?: string
  report_type: 'excel_databook' | 'word_report' | 'pdf_report' | 'summary_report'
  filename?: string
  file_size?: number
  status: 'pending' | 'generating' | 'completed' | 'error'
  error_message?: string
  qa_completed: boolean
  project_id: number
  generated_by: number
  created_at: string
  updated_at?: string
  generated_at?: string
  generation_time?: number
  adjustments_included: number
  is_completed: boolean
  has_error: boolean
  is_ready_for_download: boolean
  file_size_mb: number
  file_extension: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface DashboardMetrics {
  total_projects: number
  active_projects: number
  completed_projects: number
  total_documents: number
  processed_documents: number
  total_adjustments: number
  reviewed_adjustments: number
  avg_completion_percentage: number
  avg_adjustment_review_percentage: number
}

export interface DocumentUploadProgress {
  id: number
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  error_message?: string
  processing_time?: number
}