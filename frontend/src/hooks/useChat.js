import { useState, useCallback, useRef } from "react";
import { sendMessage } from "../services/api";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const sendingRef = useRef(false);

  const ask = useCallback(async (text) => {
    if (!text.trim() || sendingRef.current) return;
    sendingRef.current = true;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(text);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response, chunks: data.chunks_usados },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      sendingRef.current = false;
    }
  }, []);

  return { messages, loading, error, ask };
}