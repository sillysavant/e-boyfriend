"use client";

import { useEffect, useRef, useState } from "react";
import notActiveAssistantIcon from "../assets/voice.svg";
import typeIcon from "../assets/type.svg";

const mimeType = "audio/webm";

const Recorder = ({
  uploadAudio,
  loading,
  autoStart = false,
  onSwitchToType,
}) => {
  const [permission, setPermission] = useState(false);
  const [stream, setStream] = useState(null);
  const mediaRecorder = useRef(null);
  const [recordingStatus, setRecordingStatus] = useState("inactive");

  const getMicrophonePermission = async () => {
    try {
      const streamData = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false,
      });
      setPermission(true);
      setStream(streamData);
      if (autoStart) {
        startRecording(streamData);
      }
    } catch (err) {
      console.error(err.message);
    }
  };

  useEffect(() => {
    getMicrophonePermission();
  }, []);

  const startRecording = (streamData) => {
    const media = new MediaRecorder(streamData || stream, { type: mimeType });
    mediaRecorder.current = media;
    mediaRecorder.current.start();
    setRecordingStatus("recording");

    const localAudioChunks = [];
    mediaRecorder.current.ondataavailable = (event) => {
      if (typeof event.data === "undefined") return;
      if (event.data.size === 0) return;
      localAudioChunks.push(event.data);
    };

    mediaRecorder.current.onstop = async () => {
      const audioBlob = new Blob(localAudioChunks, { type: mimeType });
      await uploadAudio(audioBlob);
      setRecordingStatus("inactive");
    };
  };

  const stopRecording = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
    }
  };

  const handleClick = () => {
    if (recordingStatus === "recording") {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex justify-center items-center">
      <button
        className={`transition-all duration-300 ${
          recordingStatus === "recording" ? "animate-pulse" : ""
        }`}
        onClick={handleClick}
        disabled={loading}
      >
        <img
          src={notActiveAssistantIcon}
          alt="Voice Assistant"
          className="w-60 h-60"
        />
      </button>
    </div>
  );
};

export default Recorder;
