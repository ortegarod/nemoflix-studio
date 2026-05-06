const API_BASE = "";

async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

export async function getListing(): Promise<{ images: any[]; total: number }> {
  return apiFetch("/api/listing");
}
