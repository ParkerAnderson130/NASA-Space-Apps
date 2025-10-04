import React from "react";

// User message component
export function UserMessage({ text }) {
  return (
    <div className="message user">
      <pre>{text}</pre>
    </div>
  );
}

// Assistant message component
export function AssistantMessage({ text, cypher, dbResults }) {
  return (
    <div className="message assistant">
      <div className="assistant-text">
        <strong>Answer:</strong>
        <pre>{text}</pre>
      </div>
      {cypher && (
        <div className="assistant-cypher">
          <strong>Cypher Query:</strong>
          <pre>{cypher}</pre>
        </div>
      )}
      {dbResults && (
        <div className="assistant-dbResults">
          <strong>Database Results:</strong>
          <pre>{JSON.stringify(dbResults, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
