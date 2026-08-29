import type { AskResponse, Health, Mode } from "./types";

// In dev, "/api" is proxied to the FastAPI backend (see vite.config.ts).
// In production, set VITE_API_URL to your deployed API base URL.
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "/api";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore non-JSON errors */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function ask(question: string, mode: Mode): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, mode }),
  });
  return handle<AskResponse>(res);
}

export async function getHealth(): Promise<Health> {
  const res = await fetch(`${API_BASE}/health`);
  return handle<Health>(res);
}
