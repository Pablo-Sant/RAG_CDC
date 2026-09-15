import { useChat } from "./hooks/useChat";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import BookIcon from "./components/BookIcon";
import "./App.css";

export default function App() {
  const { messages, loading, error, ask } = useChat();

  return (
    <div className="app">
      <header className="app-header">
        <div className="eyebrow">
          <span className="eyebrow-icon"><BookIcon /></span>
          <span>ASSISTENTE JURÍDICO · CDC</span>
        </div>
        <h1>Código de Defesa do Consumidor</h1>
      </header>

      <ChatWindow messages={messages} loading={loading} error={error} />
      <ChatInput onSend={ask} disabled={loading} />
    </div>
  );
}