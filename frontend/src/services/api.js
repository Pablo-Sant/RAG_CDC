const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080/api";

export async function sendMessage(message) {
  const res = await fetch(`${API_BASE}/assistent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Erro ${res.status} ao consultar o assistente`);
  }

  return res.json(); // { response, chunks_usados }
}