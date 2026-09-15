import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Sources from "./Sources";

export default function MessageBubble({ role, text, chunks }) {
  if (role === "user") {
    return (
      <div className="bubble bubble-user">
        <p>{text}</p>
      </div>
    );
  }

  return (
    <div className="message-assistant">
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
      </div>
      <Sources chunks={chunks} />
    </div>
  );
}