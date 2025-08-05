// src/api.ts
// Simple API utility for backend communication

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Send a message to the backend AI and get a response
export async function sendMessageToAI(message: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error('Failed to get AI response');
  return res.json(); // Expecting { reply: string }
}

export async function fetchFiles() {
  const res = await fetch(`${API_BASE}/files`);
  if (!res.ok) throw new Error('Failed to fetch files');
  return res.json();
}

export async function addTag(fileId: string, tag: string) {
  const res = await fetch(`${API_BASE}/files/${fileId}/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag })
  });
  if (!res.ok) throw new Error('Failed to add tag');
  return res.json();
}

export async function removeTag(fileId: string, tag: string) {
  const res = await fetch(`${API_BASE}/files/${fileId}/tags/${encodeURIComponent(tag)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to remove tag');
  return res.json();
}

export async function moveFile(fileId: string, newPath: string) {
  const res = await fetch(`${API_BASE}/files/${fileId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ newPath })
  });
  if (!res.ok) throw new Error('Failed to move file');
  return res.json();
}

export async function deleteFile(fileId: string) {
  const res = await fetch(`${API_BASE}/files/${fileId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete file');
  return res.json();
}
