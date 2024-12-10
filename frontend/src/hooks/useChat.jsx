import React, { createContext, useState, useContext, useEffect } from "react";
import axios from "axios";

// Create an axios instance with base URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

// Create the context
const ChatContext = createContext();

// Create the provider component
export const ChatProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [cameraZoomed, setCameraZoomed] = useState(false);
  const [audioRes, setAudioRes] = useState();
  const [messages, setMessages] = useState([]);

  const onMessagePlayed = () => {
    setMessages((messages) => messages.slice(1));
  };

  useEffect(() => {
    if (messages.length > 0) {
      setMessage(messages[0]);
    } else {
      setMessage(null);
    }
  }, [messages]);

  const chat = async (audioBlob) => {
    if (loading) return;

    setLoading(true);
    setMessage(null);

    try {
      // Step 1: Transcribe audio using /wake endpoint
      const wakeFormData = new FormData();
      wakeFormData.append("audio", audioBlob);

      const wakeResponse = await api.post("/wake", wakeFormData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const transcribedText = wakeResponse.data.transcribed_text;

      // Step 2: Send transcribed text to /chat endpoint
      const chatResponse = await api.post("/chat", { text: transcribedText });

      console.log(chatResponse);

      setAudioRes(chatResponse.data.audio);
      const messagesRes = chatResponse.data.messages;
      setMessages((messages) => [...messages, ...messagesRes]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Provide the context values
  return (
    <ChatContext.Provider
      value={{
        audioRes,
        chat,
        message,
        loading,
        cameraZoomed,
        setCameraZoomed,
        onMessagePlayed,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

// Custom hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
