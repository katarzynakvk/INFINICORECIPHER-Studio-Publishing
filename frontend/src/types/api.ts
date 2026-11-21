export interface ApiError {
  code: string;
  message: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
}

export interface Project {
  book_id: string;
  title: string;
  schema_version: number;
  created_at: string;
  state: "ACTIVE" | "ARCHIVED";
  root: string;
}
