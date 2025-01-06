import React, { useState } from "react";
import { useChat } from "../hooks/useChat";
import Recorder from "./Recorder";
import InputSelector from "./InputSelector";
import zoomInIcon from "../assets/zoomin.svg";
import zoomOutIcon from "../assets/zoomout.svg";
import settingIcon from "../assets/setting.svg";
import SettingsModal from "./SettingsModal";
import typeIcon from "../assets/type.svg";

export const UI = ({ hidden, ...props }) => {
  const { chat, loading, handleZoomIn, handleZoomOut, zoomLevel } = useChat();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [inputMode, setInputMode] = useState(null); // null, 'voice', or 'type'

  const handleAudioUpload = async (blob) => {
    try {
      await chat(blob);
    } catch (error) {
      console.error("Error uploading audio:", error);
    }
  };

  const handleSettingsClick = () => {
    setIsSettingsOpen(true);
  };

  const handleCloseSettings = () => {
    setIsSettingsOpen(false);
  };

  const handleSelectMic = () => {
    setInputMode("voice");
  };

  const handleSelectType = (message) => {
    // Handle text message submission here
    console.log("Sending message:", message);
    // You can add your text processing logic here
  };

  const handleSwitchToType = () => {
    setInputMode(null); // This will show the InputSelector again
  };

  const renderInputMethod = () => {
    if (!inputMode) {
      return (
        <InputSelector
          onSelectMic={handleSelectMic}
          onSelectType={handleSelectType}
        />
      );
    }
    if (inputMode === "voice") {
      return (
        <Recorder
          uploadAudio={handleAudioUpload}
          loading={loading}
          autoStart={true}
          onSwitchToType={handleSwitchToType}
        />
      );
    }
    return null;
  };

  return (
    <>
      <div className="fixed top-0 left-0 right-0 bottom-0 z-10 flex justify-between p-4 pointer-events-none">
        {/* Settings button - top right */}
        <button
          onClick={handleSettingsClick}
          className="fixed top-4 right-4 pointer-events-auto p-2 transition-all duration-300 hover:opacity-75"
        >
          <img src={settingIcon} alt="Settings" className="w-6 h-6" />
        </button>

        {/* Right side controls */}
        <div className="fixed right-4 top-1/2 -translate-y-1/2 flex flex-col gap-2">
          <button
            onClick={handleZoomIn}
            disabled={zoomLevel >= 3}
            className={`pointer-events-auto p-2 rounded-[6px] border-[1.51px] border-white/10 
              bg-[rgba(205,205,205,0.60)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
              backdrop-blur-[5.9px] transition-all duration-300
              ${
                zoomLevel >= 3
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-[rgba(205,205,205,0.75)]"
              }`}
          >
            <img src={zoomInIcon} alt="Zoom in" className="w-6 h-6" />
          </button>
          <button
            onClick={handleZoomOut}
            disabled={zoomLevel <= 0}
            className={`pointer-events-auto p-2 rounded-[6px] border-[1.51px] border-white/10 
              bg-[rgba(205,205,205,0.60)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
              backdrop-blur-[5.9px] transition-all duration-300
              ${
                zoomLevel <= 0
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-[rgba(205,205,205,0.75)]"
              }`}
          >
            <img src={zoomOutIcon} alt="Zoom out" className="w-6 h-6" />
          </button>
          {inputMode === "voice" && (
            <button
              onClick={handleSwitchToType}
              className="pointer-events-auto p-2 rounded-[6px] border-[1.51px] border-white/10 
                bg-[rgba(205,205,205,0.60)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
                backdrop-blur-[5.9px] transition-all duration-300 hover:bg-[rgba(205,205,205,0.75)]"
            >
              <img src={typeIcon} alt="Switch to typing" className="w-6 h-6" />
            </button>
          )}
        </div>

        {/* Bottom input method */}
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 max-w-screen-sm w-full pointer-events-auto">
          {renderInputMethod()}
        </div>
      </div>

      <SettingsModal isOpen={isSettingsOpen} onClose={handleCloseSettings} />
    </>
  );
};

export default UI;
