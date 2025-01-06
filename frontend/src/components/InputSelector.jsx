import React from "react";
import micIcon from "../assets/mic-icon.svg";
import typeIcon from "../assets/type.svg";

const InputSelector = ({ onSelectMic, onSelectType }) => {
  const handleMicClick = () => {
    onSelectMic(true);
  };

  return (
    <div className="flex justify-center items-center">
      <div className="flex gap-4 justify-center items-center">
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
        <button
          className={`pointer-events-auto p-2 rounded-[6px] border-[1.51px] border-white/10 
            bg-[rgba(205,205,205,0.60)] shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)] 
            backdrop-blur-[5.9px] transition-all duration-300 hover:bg-[rgba(205,205,205,0.75)]`}
          onClick={onSelectType}
        >
          <img src={typeIcon} alt="Text Input" className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default InputSelector;
