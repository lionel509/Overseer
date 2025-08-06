import React from 'react';
import { ChatInterface } from '../organisms/ChatInterface';

export const ChatPage: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <h1 className="text-2xl font-bold mb-4">AI Chat</h1>
      <p className="mb-4 text-gray-600 dark:text-gray-400">
        Ask the Overseer AI anything about your system.
      </p>
      <div className="flex-grow">
        <ChatInterface />
      </div>
    </div>
  );
};
