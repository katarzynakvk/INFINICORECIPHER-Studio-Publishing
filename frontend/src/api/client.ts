import type { ApiEnvelope } from "../types/api";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  const envelope = (await response.json()) as ApiEnvelope<T>;
  if (!response.ok || !envelope.success) {
    throw new Error(envelope.error?.message ?? `Request failed (${response.status})`);
  }
  if (envelope.data === null) {
    throw new Error("Response contained no data");
  }
  return envelope.data;
}
