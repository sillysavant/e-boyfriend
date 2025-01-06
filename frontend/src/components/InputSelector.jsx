import React, { useState } from "react";
import micIcon from "../assets/mic-icon.svg";
import sendIcon from "../assets/send.svg";

const InputSelector = ({ onSelectMic, onSelectType }) => {
  const [message, setMessage] = useState("");

  const handleMicClick = () => {
    onSelectMic(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSelectType(message);
      setMessage("");
    }
  };

  return (
    <div className="flex justify-center items-center w-full max-w-3xl">
      <div className="flex gap-4 justify-center items-center w-full">
        <button
          className={`group pointer-events-auto p-2 rounded-full 
            bg-[rgba(23,21,21,0.6)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
            backdrop-blur-[5.9px] transition-all duration-300 hover:bg-[rgba(205,205,205,0.75)]`}
          onClick={handleMicClick}
        >
          <img
            src={micIcon}
            alt="Voice Input"
            className="w-6 h-6 [filter:brightness(0)_invert(1)] group-hover:[filter:brightness(0)_invert(0)]"
          />
        </button>

        <form onSubmit={handleSubmit} className="flex-1 flex gap-2 relative">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
            className="w-full px-4 py-2 pr-12 rounded-[121.368px] border-[1.51px] border-white/10 
              bg-[rgba(205,205,205,0.60)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
              backdrop-blur-[5.9px] transition-all duration-300
              placeholder:text-gray-600 text-black
              focus:outline-none focus:border-white/20"
          />
          <button
            type="submit"
            className={`absolute right-3 top-1/2 -translate-y-1/2
              transition-all duration-300
              ${
                !message.trim()
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:scale-110"
              }`}
            disabled={!message.trim()}
          >
            <img src={sendIcon} alt="Send message" className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default InputSelector;
