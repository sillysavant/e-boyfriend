import React, { createContext, useState, useContext, useRef } from "react";
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
  const audioRef = useRef(null);

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

      setMessage(chatResponse.data);

      if (chatResponse.data.audio_url) {
        if (!audioRef.current) {
          audioRef.current = new Audio();
        }

        audioRef.current.src = chatResponse.data.audio_url;
        await audioRef.current.play();
      }
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
        chat,
        loading,
        message,
        cameraZoomed,
        setCameraZoomed,
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
