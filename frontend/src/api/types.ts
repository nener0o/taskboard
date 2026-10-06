export type Role = "user" | "manager" | "admin";

export type User = {
  id: number;
  name: string;
  email: string;
  role: Role;
  is_active: boolean;
  permissions: string[];
};

export type Task = {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  is_public: boolean;
  owner_id: number;
  assignee_id: number | null;
  owner_name: string;
  assignee_name: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskPage = {
  items: Task[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type Attachment = {
  id: number;
  task_id: number;
  original_name: string;
  content_type: string;
  size: number;
  uploaded_by: number;
  created_at: string;
  download_url: string;
};

export type Weather = {
  available: boolean;
  location: string;
  temperature_c: number | null;
  weather_code: number | null;
  summary: string;
  source: string;
  stale: boolean;
};

export type Tokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};
