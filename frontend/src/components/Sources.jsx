import { useState } from "react";

function parseChunk(chunk) {
  if (typeof chunk === "string") {
    try {
      return JSON.parse(chunk);
    } catch {
      return { texto: chunk };
    }
  }
  return chunk;
}

export default function Sources({ chunks }) {
  const [open, setOpen] = useState(false);

  if (!chunks || chunks.length === 0) return null;

  return (
    <div className="sources">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "Ocultar" : "Ver"} trechos do CDC citados ({chunks.length})
      </button>

      {open && (
        <ol className="sources-list">
          {chunks.map((raw, i) => {
            const chunk = parseChunk(raw);
            const relevancia = chunk.score ? Math.round(chunk.score * 100) : null;

            return (
              <li key={i}>
                <span className="source-meta">
                  <span className="source-page">
                    {chunk.fonte || "CDC"} — pág. {chunk.pagina || "?"}
                  </span>
                  {relevancia !== null && (
                    <span className="source-score">{relevancia}% relevância</span>
                  )}
                </span>
                <p className="source-text">{chunk.texto}</p>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}