// Single source of truth for the API base URL (ADR-2 guard rail).
// In development the Vite dev server (port 5173) calls the FastAPI backend
// directly on port 8000, so .env.development sets VITE_API_BASE_URL.
// In production the SPA is served from the same origin as the API (ADR-3),
// so the base URL is empty (same-origin requests).
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Non-JSON error body; keep the status text.
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function patch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body) });
}

export function del<T = void>(path: string): Promise<T> {
  return request<T>(path, { method: "DELETE" });
}