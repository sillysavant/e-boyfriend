"use client";

import { useEffect, useRef, useState } from "react";
import activeAssistantIcon from "../assets/active.gif";
import notActiveAssistantIcon from "../assets/inactive.png";

const mimeType = "audio/webm";

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
      ) : recordingStatus === "inactive" ? (
        <img
          src={notActiveAssistantIcon}
          alt="Not Recording"
          width={70}
          height={70}
          onClick={startRecording}
          className="assistant cursor-pointer hover:scale-110 duration-150 transition-all ease-in-out"
          disabled={loading}
        />
      ) : (
        <img
          src={activeAssistantIcon}
          alt="Recording"
          width={70}
          height={70}
          onClick={stopRecording}
          className="assistant cursor-pointer hover:scale-110 duration-150 transition-all ease-in-out"
        />
      )}
    </div>
  );
}

export default Recorder;
