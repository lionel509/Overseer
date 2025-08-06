import React, { useState, useCallback, useEffect } from 'react';
import { MessageList } from '../molecules/MessageList';
import { MessageInput } from '../molecules/MessageInput';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
}

declare global {
  interface Window {
    ipc: {
      invoke: (channel: string, ...args: any[]) => Promise<any>;
    };
  }
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await window.ipc.invoke('run-command', {
        feature: 'llm_advisor',
        prompt: text,
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response || "Sorry, I couldn't get a response.",
        sender: 'ai',
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "An error occurred while communicating with the backend.",
        sender: 'ai',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <MessageList messages={messages} />
      <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};
