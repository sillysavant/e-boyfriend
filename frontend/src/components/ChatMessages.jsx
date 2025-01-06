import React, { useEffect, useRef } from "react";

const ChatMessages = ({ messages }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="fixed bottom-32 left-1/2 -translate-x-1/2 w-full max-w-2xl h-[30vh] px-4">
      <div className="h-full overflow-y-auto pr-2 flex flex-col-reverse">
        <div className="flex flex-col gap-4 items-end">
          {messages.map((message, index) => (
            <div
              key={index}
              className="bg-[rgba(205,205,205,0.60)] backdrop-blur-[5.9px] 
                rounded-[20px] p-4 border-[1.51px] border-white/10
                shadow-[0px_4.96px_62.003px_0px_rgba(0,0,0,0.19)]
                animate-float-up
                max-w-[80%]"
            >
              <p className="text-black">{message}</p>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
};

export default ChatMessages;
