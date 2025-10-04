import React, { useState } from "react";
import { UserMessage, AssistantMessage } from "./MessageTypes.js";
//import "./styles/Chat.scss";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { type: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      const assistantMessage = {
        type: "assistant",
        text: data.answer,
        cypher: data.cypher_query,
        dbResults: data.database_results,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { type: "error", text: "Failed to fetch answer from API." },
      ]);
    }
  };

  return (
    <div className="chat-container">
      <h2>Neo4j Conversational Chat</h2>
      <div className="chat-window">
        {messages.map((msg, idx) => {
          if (msg.type === "user") return <UserMessage key={idx} text={msg.text} />;
          if (msg.type === "assistant")
            return (
              <AssistantMessage
                key={idx}
                text={msg.text}
                cypher={msg.cypher}
                dbResults={msg.dbResults}
              />
            );
          return <div key={idx} className="message error">{msg.text}</div>;
        })}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          placeholder="What's on your mind?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
