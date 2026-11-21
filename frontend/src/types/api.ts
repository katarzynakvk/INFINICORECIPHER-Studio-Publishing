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

export type SettingScope =
  | "APPLICATION"
  | "PROJECT"
  | "BOOK"
  | "EDITION"
  | "RUNTIME"
  | "AI_PROVIDER"
  | "STORAGE"
  | "SECURITY_CREDENTIAL_REFERENCE";

export interface Setting {
  setting_id: string;
  scope: SettingScope;
  scope_id: string;
  key: string;
  value: unknown;
  state: "EXPLICIT" | "UNSET";
  revision: number;
}
