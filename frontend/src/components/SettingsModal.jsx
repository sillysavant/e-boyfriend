import React, { useState } from "react";
import "./SettingsModal.css";
import alexImage from "../assets/Alex.svg";
import emmaImage from "../assets/Emma.svg";
import jordanImage from "../assets/Jordan.svg";
import oliviaImage from "../assets/Olivia.svg";
import samImage from "../assets/Sam.svg";
import sophieImage from "../assets/Sophie.svg";

const VOICES = ["Asian", "Caucasian", "African", "Hispanic"];
const CHARACTERS = [
  { name: "Alex", image: alexImage },
  { name: "Emma", image: emmaImage },
  { name: "Jordan", image: jordanImage },
  { name: "Olivia", image: oliviaImage },
  { name: "Sam", image: samImage },
  { name: "Sophie", image: sophieImage },
];

const SettingsModal = ({ isOpen, onClose, children }) => {
  const [currentVoice, setCurrentVoice] = useState(0);
  const [currentCharacter, setCurrentCharacter] = useState(0);

  const nextVoice = () => {
    setCurrentVoice((prev) => (prev + 1) % VOICES.length);
  };

  const prevVoice = () => {
    setCurrentVoice((prev) => (prev - 1 + VOICES.length) % VOICES.length);
  };

  const nextCharacter = () => {
    setCurrentCharacter((prev) => (prev + 1) % CHARACTERS.length);
  };

  const prevCharacter = () => {
    setCurrentCharacter(
      (prev) => (prev - 1 + CHARACTERS.length) % CHARACTERS.length
    );
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <table className="settings-table">
            <tbody>
              <tr>
                <td className="setting-label">Voice</td>
                <td className="setting-control">
                  <div className="navigation-control">
                    <button onClick={prevVoice} className="nav-button">
                      <svg width="24" height="24" viewBox="0 0 24 24">
                        <path
                          d="M15 18l-6-6 6-6"
                          stroke="currentColor"
                          strokeWidth="2"
                          fill="none"
                        />
                      </svg>
                    </button>
                    <span className="current-value">
                      {VOICES[currentVoice]}
                    </span>
                    <button onClick={nextVoice} className="nav-button">
                      <svg width="24" height="24" viewBox="0 0 24 24">
                        <path
                          d="M9 18l6-6-6-6"
                          stroke="currentColor"
                          strokeWidth="2"
                          fill="none"
                        />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="setting-label">Character</td>
                <td className="setting-control">
                  <div className="navigation-control">
                    <button onClick={prevCharacter} className="nav-button">
                      <svg width="24" height="24" viewBox="0 0 24 24">
                        <path
                          d="M15 18l-6-6 6-6"
                          stroke="currentColor"
                          strokeWidth="2"
                          fill="none"
                        />
                      </svg>
                    </button>
                    <div className="character-display">
                      <img
                        src={CHARACTERS[currentCharacter].image}
                        alt={CHARACTERS[currentCharacter].name}
                        className="character-image"
                      />
                      <span className="current-value">
                        {CHARACTERS[currentCharacter].name}
                      </span>
                    </div>
                    <button onClick={nextCharacter} className="nav-button">
                      <svg width="24" height="24" viewBox="0 0 24 24">
                        <path
                          d="M9 18l6-6-6-6"
                          stroke="currentColor"
                          strokeWidth="2"
                          fill="none"
                        />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
