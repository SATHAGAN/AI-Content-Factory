export interface Channel {
  id: string;
  name: string;
  description: string | null;
  default_language: string;
  approval_mode: string;
  daily_shorts_target: number;
  daily_long_target: number;
}

export interface ContentProfile {
  id: string;
  name: string;
  category: string;
  audience: string | null;
  language: string;
  tone: string | null;
  settings: Record<string, unknown>;
}

export interface Project {
  id: string;
  name: string;
  status: string;
  channel_id: string | null;
  content_profile_id: string | null;
  source_document_id: string | null;
  settings: Record<string, unknown>;
}
