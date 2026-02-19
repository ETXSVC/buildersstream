export type RFIStatus = 'open' | 'answered' | 'closed';
export type SubmittalStatus = 'draft' | 'submitted' | 'under_review' | 'approved' | 'approved_as_noted' | 'rejected' | 'resubmit';
export type DocumentStatus = 'active' | 'superseded' | 'archived';

export interface DocumentFolder {
  id: string;
  name: string;
  parent: string | null;
  document_count: number;
  created_at: string;
}

export interface Document {
  id: string;
  folder: string | null;
  folder_name: string | null;
  project: string | null;
  project_name: string | null;
  title: string;
  file_name: string;
  file_size: number | null;
  file_type: string | null;
  status: DocumentStatus;
  version_number: number;
  is_current_version: boolean;
  uploaded_by_name: string | null;
  download_url: string | null;
  created_at: string;
}

export interface RFI {
  id: string;
  project: string;
  project_name: string;
  rfi_number: number;
  title: string;
  status: RFIStatus;
  question: string;
  answer: string | null;
  submitted_by_name: string | null;
  assigned_to_name: string | null;
  date_submitted: string;
  due_date: string | null;
  date_answered: string | null;
  is_overdue: boolean;
}

export interface Submittal {
  id: string;
  project: string;
  project_name: string;
  submittal_number: number;
  title: string;
  spec_section: string | null;
  status: SubmittalStatus;
  submitted_by_name: string | null;
  reviewed_by_name: string | null;
  submitted_date: string | null;
  required_by: string | null;
  reviewed_date: string | null;
  review_notes: string | null;
}

export interface Photo {
  id: string;
  project: string;
  project_name: string;
  album: string | null;
  album_name: string | null;
  caption: string | null;
  thumbnail_url: string | null;
  download_url: string | null;
  taken_at: string | null;
  uploaded_by_name: string | null;
  created_at: string;
}

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const RFI_STATUS_COLORS: Record<RFIStatus, string> = {
  open: 'bg-amber-100 text-amber-700',
  answered: 'bg-blue-100 text-blue-700',
  closed: 'bg-green-100 text-green-700',
};

export const SUBMITTAL_STATUS_COLORS: Record<SubmittalStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  submitted: 'bg-blue-100 text-blue-700',
  under_review: 'bg-purple-100 text-purple-700',
  approved: 'bg-green-100 text-green-700',
  approved_as_noted: 'bg-teal-100 text-teal-700',
  rejected: 'bg-red-100 text-red-700',
  resubmit: 'bg-orange-100 text-orange-700',
};
