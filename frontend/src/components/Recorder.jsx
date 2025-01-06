"use client";

import { useEffect, useRef, useState } from "react";
import notActiveAssistantIcon from "../assets/voice.svg";

const mimeType = "audio/webm";

const pulseAnimation = `
  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
    100% {
      transform: scale(1);
    }
  }
`;

function Recorder({ uploadAudio, loading }) {
  const mediaRecorder = useRef();
  const [permission, setPermission] = useState(false);
  const [stream, setStream] = useState();
  const [recordingStatus, setRecordingStatus] = useState("inactive");
  const [audioChunks, setAudioChunks] = useState([]);
  const [audio, setAudio] = useState(null);

  useEffect(() => {
    getMicrophonePermission();
  }, []);

  const getMicrophonePermission = async () => {
    if ("MediaRecorder" in window) {
      try {
        const streamData = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: false,
        });
        setPermission(true);
        setStream(streamData);
      } catch (err) {
        alert(err.message);
      }
    } else {
      alert("The MediaRecorder API is not supported in your browser.");
    }
  };

  const startRecording = async () => {
    if (mediaRecorder.current === null || stream === null) return;

    setRecordingStatus("recording");
    const media = new MediaRecorder(stream, { mimeType: mimeType });
    mediaRecorder.current = media;
    mediaRecorder.current.start();
    let localAudioChunks = [];
    mediaRecorder.current.ondataavailable = (event) => {
      if (typeof event.data === "undefined") return;
      if (event.data.size === 0) return;
      localAudioChunks.push(event.data);
    };
    setAudioChunks(localAudioChunks);
  };

  const stopRecording = () => {
    if (mediaRecorder.current === null) return;

    setRecordingStatus("inactive");
    mediaRecorder.current.stop();
    mediaRecorder.current.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: mimeType });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudio(audioUrl);
      uploadAudio(audioBlob);
      setAudioChunks([]);
    };
  };

  return (
    <div className="flex justify-center">
      {!permission ? (
        <button onClick={getMicrophonePermission} type="button">
          Get Microphone
        </button>
      ) : (
        <img
          src={notActiveAssistantIcon}
          alt={recordingStatus === "inactive" ? "Not Recording" : "Recording"}
          width={150}
          height={150}
          onClick={
            recordingStatus === "inactive" ? startRecording : stopRecording
          }
          className={`assistant cursor-pointer hover:scale-110 duration-150 transition-all ease-in-out ${
            recordingStatus === "recording" ? "animate-pulse" : ""
          }`}
          disabled={loading}
        />
      )}
    </div>
  );
}

export default Recorder;
