import React, { useState, useMemo } from 'react'

interface FileItem {
  id: string
  name: string
  type: 'file' | 'directory'
  size: string
  modified: string
  path: string
  tags?: string[]
  category?: string
  extension?: string
  permissions?: string
  owner?: string
}

const FileManager: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([
    { id: '1', name: 'Documents', type: 'directory', size: '-', modified: '2024-01-15 10:30', path: '/home/user/Documents', category: 'folder', permissions: 'drwxr-xr-x', owner: 'user' },
    { id: '2', name: 'Downloads', type: 'directory', size: '-', modified: '2024-01-14 14:20', path: '/home/user/Downloads', category: 'folder', permissions: 'drwxr-xr-x', owner: 'user' },
    { id: '3', name: 'report.pdf', type: 'file', size: '2.3 MB', modified: '2024-01-13 09:15', path: '/home/user/report.pdf', extension: 'pdf', category: 'document', tags: ['work', 'important'], permissions: '-rw-r--r--', owner: 'user' },
    { id: '4', name: 'config.json', type: 'file', size: '1.2 KB', modified: '2024-01-12 16:45', path: '/home/user/config.json', extension: 'json', category: 'config', permissions: '-rw-r--r--', owner: 'user' },
    { id: '5', name: 'backup.tar.gz', type: 'file', size: '45.7 MB', modified: '2024-01-11 08:30', path: '/home/user/backup.tar.gz', extension: 'tar.gz', category: 'archive', permissions: '-rw-r--r--', owner: 'user' },
    { id: '6', name: 'main.py', type: 'file', size: '3.4 KB', modified: '2024-01-10 13:22', path: '/home/user/main.py', extension: 'py', category: 'code', tags: ['python'], permissions: '-rwxr-xr-x', owner: 'user' },
    { id: '7', name: 'script.js', type: 'file', size: '2.1 KB', modified: '2024-01-09 11:10', path: '/home/user/script.js', extension: 'js', category: 'code', permissions: '-rw-r--r--', owner: 'user' },
    { id: '8', name: 'image.png', type: 'file', size: '1.8 MB', modified: '2024-01-08 15:55', path: '/home/user/image.png', extension: 'png', category: 'image', permissions: '-rw-r--r--', owner: 'user' },
    { id: '9', name: 'video.mp4', type: 'file', size: '15.6 MB', modified: '2024-01-07 12:00', path: '/home/user/video.mp4', extension: 'mp4', category: 'media', permissions: '-rw-r--r--', owner: 'user' },
    { id: '10', name: 'archive.zip', type: 'file', size: '8.9 MB', modified: '2024-01-06 18:30', path: '/home/user/archive.zip', extension: 'zip', category: 'archive', permissions: '-rw-r--r--', owner: 'user' }
  ])
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'type' | 'size' | 'modified'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [showSidebar, setShowSidebar] = useState(false)

  // Filter and sort files
  const filteredAndSortedFiles = useMemo(() => {
    let filtered = files

    // Apply search filter
    if (searchQuery) {
      filtered = files.filter(file => 
        file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.extension?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    // Apply sorting
    return [...filtered].sort((a, b) => {
      let aValue: any, bValue: any
      
      switch (sortBy) {
        case 'type':
          if (a.type !== b.type) {
            return a.type === 'directory' ? -1 : 1
          }
          aValue = a.category || ''
          bValue = b.category || ''
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
        case 'size':
          aValue = a.size === '-' ? 0 : parseFloat(a.size.replace(/[^\d.]/g, ''))
          bValue = b.size === '-' ? 0 : parseFloat(b.size.replace(/[^\d.]/g, ''))
          return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
        case 'modified':
          aValue = new Date(a.modified).getTime()
          bValue = new Date(b.modified).getTime()
          return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
        default: // name
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
      }
    })
  }, [files, searchQuery, sortBy, sortOrder])

  const handleSort = (column: 'name' | 'type' | 'size' | 'modified') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  const handleFileClick = (file: FileItem) => {
    setSelectedFile(file)
    setShowSidebar(true)
  }

  const getFileIcon = (file: FileItem) => {
    if (file.type === 'directory') return '📁'
    
    switch (file.category) {
      case 'document': return '📄'
      case 'image': return '🖼️'
      case 'code': return '💻'
      case 'archive': return '📦'
      case 'media': return '🎵'
      case 'config': return '⚙️'
      default: return '📄'
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${showSidebar ? 'mr-80' : ''}`}>
        
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">File Manager</h1>
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
            />
          </div>
        </div>

        {/* File Table */}
        <div className="flex-1 bg-white overflow-auto">
          <div className="file-table-container">
            <div className="file-table-wrapper">
              <table className="file-table">
                <thead className="file-table-header">
                  <tr>
                    <th 
                      className="sortable cursor-pointer"
                      onClick={() => handleSort('name')}
                    >
                      File Name
                      {sortBy === 'name' && (
                        <span className="sort-indicator">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </th>
                    <th 
                      className="sortable cursor-pointer"
                      onClick={() => handleSort('modified')}
                    >
                      Last Modified
                      {sortBy === 'modified' && (
                        <span className="sort-indicator">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </th>
                    <th>Tags</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedFiles.map((file) => (
                    <tr 
                      key={file.id}
                      className={`file-table-row cursor-pointer ${
                        selectedFile?.id === file.id ? 'selected' : ''
                      }`}
                      onClick={() => handleFileClick(file)}
                    >
                      <td className="file-table-cell">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 flex items-center justify-center text-lg">
                            {getFileIcon(file)}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="file-name">{file.name}</div>
                            <div className="file-details">
                              {file.size} • {file.category || file.type}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="file-table-cell">
                        <span className="file-modified">
                          {new Date(file.modified).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </td>
                      <td className="file-table-cell">
                        <div className="file-tags">
                          {file.tags && file.tags.length > 0 ? (
                            file.tags.map((tag, tagIndex) => (
                              <span key={tagIndex} className="file-tag">
                                {tag}
                              </span>
                            ))
                          ) : (
                            <span className="no-tags">No tags</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      {showSidebar && selectedFile && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 z-10 overflow-y-auto shadow-lg">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">File Details</h3>
              <button
                onClick={() => setShowSidebar(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <p className="text-gray-900">{selectedFile.name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <p className="text-gray-900">{selectedFile.type}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Size</label>
                <p className="text-gray-900">{selectedFile.size}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Modified</label>
                <p className="text-gray-900">{selectedFile.modified}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Path</label>
                <p className="text-gray-900 break-all">{selectedFile.path}</p>
              </div>
              {selectedFile.tags && selectedFile.tags.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tags</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedFile.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileManager 