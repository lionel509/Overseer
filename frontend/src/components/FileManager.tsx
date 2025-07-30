import React, { useState } from 'react'

interface FileItem {
  id: string
  name: string
  type: 'file' | 'directory'
  size: string
  modified: string
  path: string
}

const FileManager: React.FC = () => {
  const [currentPath, setCurrentPath] = useState('/home/user')
  const [files, setFiles] = useState<FileItem[]>([
    { id: '1', name: 'Documents', type: 'directory', size: '-', modified: '2024-01-15', path: '/home/user/Documents' },
    { id: '2', name: 'Downloads', type: 'directory', size: '-', modified: '2024-01-14', path: '/home/user/Downloads' },
    { id: '3', name: 'report.pdf', type: 'file', size: '2.3 MB', modified: '2024-01-13', path: '/home/user/report.pdf' },
    { id: '4', name: 'config.json', type: 'file', size: '1.2 KB', modified: '2024-01-12', path: '/home/user/config.json' },
    { id: '5', name: 'backup.tar.gz', type: 'file', size: '45.7 MB', modified: '2024-01-11', path: '/home/user/backup.tar.gz' }
  ])
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  const handleFileSelect = (fileId: string) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    )
  }

  const handlePathChange = (newPath: string) => {
    setCurrentPath(newPath)
    // In a real app, this would fetch files from the new path
  }

  const getFileIcon = (type: 'file' | 'directory') => {
    return type === 'directory' ? '📁' : '📄'
  }

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="mb-8">
        <h2 className="text-4xl font-bold text-gray-800 mb-2">File Manager</h2>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
          <span className="font-mono text-gray-600">{currentPath}</span>
        </div>
      </div>
      
      <div className="flex gap-3 mb-6 flex-wrap">
        <button className="px-6 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-50 hover:border-gray-300">
          📁 New Folder
        </button>
        <button className="px-6 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-50 hover:border-gray-300">
          📄 New File
        </button>
        <button className="px-6 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-50 hover:border-gray-300">
          📤 Upload
        </button>
        <button className="px-6 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-50 hover:border-gray-300">
          📥 Download
        </button>
        <button className="px-6 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-50 hover:border-gray-300">
          🗑️ Delete
        </button>
      </div>
      
      <div className="flex-1 bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="grid grid-cols-4 p-4 bg-gray-50 border-b border-gray-200 font-semibold text-gray-600 text-sm">
          <div>Name</div>
          <div>Size</div>
          <div>Modified</div>
          <div>Actions</div>
        </div>
        
        {files.map((file) => (
          <div 
            key={file.id} 
            className={`grid grid-cols-4 p-4 border-b border-gray-100 cursor-pointer transition-colors hover:bg-gray-50 ${
              selectedFiles.includes(file.id) ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
            }`}
            onClick={() => handleFileSelect(file.id)}
          >
            <div className="flex items-center gap-3 font-medium">
              <span className="text-xl">{getFileIcon(file.type)}</span>
              <span>{file.name}</span>
            </div>
            <div className="text-gray-600">{file.size}</div>
            <div className="text-gray-600">{file.modified}</div>
            <div className="flex gap-2">
              <button className="p-1 hover:bg-gray-200 rounded text-lg transition-colors">👁️</button>
              <button className="p-1 hover:bg-gray-200 rounded text-lg transition-colors">✏️</button>
              <button className="p-1 hover:bg-gray-200 rounded text-lg transition-colors">🗑️</button>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 flex justify-between items-center pt-4 border-t border-gray-200">
        <div className="text-gray-600 text-sm">
          {selectedFiles.length} item(s) selected
        </div>
        <div className="flex items-center gap-4 text-gray-600 text-sm">
          <span>Storage: 45.2 GB used of 500 GB</span>
          <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full" style={{ width: '9%' }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FileManager 