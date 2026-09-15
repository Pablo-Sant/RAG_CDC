import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, loading, error }) {
  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <p className="empty-state">
          Faça uma pergunta sobre o Código de Defesa do Consumidor.
        </p>
      )}

      {messages.map((m, i) => (
        <MessageBubble key={i} role={m.role} text={m.text} chunks={m.chunks} />
      ))}

      {loading && <p className="loading">Consultando o CDC…</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}