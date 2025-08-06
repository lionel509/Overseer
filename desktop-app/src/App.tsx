import React, { useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useAppDispatch } from './store/hooks';
import { initializeApp } from './store/appSlice';
import { initializePythonBackend } from './store/pythonSlice';
import CommandPalette from './components/CommandPalette';
import { DashboardPage } from './components/pages/DashboardPage';
import { ChatPage } from './components/pages/ChatPage';
import { AutomationsPage } from './components/pages/AutomationsPage';
import { SettingsPage } from './components/pages/SettingsPage';
import './App.css';

const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-md text-sm font-medium ${
        isActive
          ? 'bg-blue-500 text-white'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
      }`}>
      {children}
    </Link>
  );
};

function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(initializeApp());
    dispatch(initializePythonBackend());
  }, [dispatch]);

  return (
    <div className="app bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white">
      <header className="bg-white dark:bg-gray-800 shadow-md p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Overseer</h1>
        <nav className="flex items-center space-x-4">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/chat">AI Chat</NavLink>
          <NavLink to="/automations">Automations</NavLink>
          <NavLink to="/settings">Settings</NavLink>
        </nav>
      </header>
      <main className="p-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/automations" element={<AutomationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
      <CommandPalette />
    </div>
  );
}

export default App; 