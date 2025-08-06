import { useEffect } from 'react';
import { fetchFiles, addTag as apiAddTag, removeTag as apiRemoveTag, moveFile as apiMoveFile, deleteFile as apiDeleteFile } from '../api';
import React, { useState, useMemo, useRef } from 'react'
import { createPortal } from 'react-dom';

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
  const actionBtnRefs = useRef<{ [id: string]: HTMLButtonElement | null }>({});
  const [dropdownPos, setDropdownPos] = useState<{ top: number; left: number } | null>(null);
  const [files, setFiles] = useState<FileItem[]>([])
  // Fetch files from backend on mount
  useEffect(() => {
    fetchFiles().then(setFiles).catch(() => {
      // fallback or error handling
    });
  }, []);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'type' | 'size' | 'modified'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [showSidebar, setShowSidebar] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)

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
    if (file.type === 'file') {
      setSelectedFile(file)
      setShowSidebar(true)
    }
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

  // Dropdown menu action handlers
  const handleShowDetails = (file: FileItem) => {
    setSelectedFile(file);
    setShowDetailsModal(true);
    setOpenMenuId(null);
    setDropdownPos(null);
  };

  const handleAddTag = async (file: FileItem) => {
    setOpenMenuId(null);
    setDropdownPos(null);
    let tag = '';
    if (typeof window !== 'undefined' && window.prompt) {
      tag = window.prompt('Enter the name of the tag to add:') || '';
    }
    tag = tag.trim();
    if (!tag) {
      if (typeof window !== 'undefined' && window.alert) {
        window.alert('Tag cannot be empty.');
      }
      return;
    }
    try {
      await apiAddTag(file.id, tag);
      // Refresh file list
      const updated = await fetchFiles();
      setFiles(updated);
    } catch (e) {
      window.alert('Failed to add tag.');
    }
  };

  const handleRemoveTag = async (file: FileItem) => {
    setOpenMenuId(null);
    setDropdownPos(null);
    if (!file.tags || file.tags.length === 0) {
      if (typeof window !== 'undefined' && window.alert) {
        window.alert('No tags to remove.');
      }
      return;
    }
    let tag = '';
    if (typeof window !== 'undefined' && window.prompt) {
      tag = window.prompt('Enter the name of the tag to remove:') || '';
    }
    tag = tag.trim();
    if (!tag) {
      return;
    }
    if (!file.tags.includes(tag)) {
      if (typeof window !== 'undefined' && window.alert) {
        window.alert('Tag not found on this file.');
      }
      return;
    }
    try {
      await apiRemoveTag(file.id, tag);
      const updated = await fetchFiles();
      setFiles(updated);
    } catch (e) {
      window.alert('Failed to remove tag.');
    }
  };

  const handleMoveFile = async (file: FileItem) => {
    const newPath = prompt('Enter new path:', file.path);
    if (newPath && newPath !== file.path) {
      try {
        await apiMoveFile(file.id, newPath);
        const updated = await fetchFiles();
        setFiles(updated);
      } catch (e) {
        window.alert('Failed to move file.');
      }
    }
    setOpenMenuId(null);
    setDropdownPos(null);
  };

  const handleDeleteFile = async (file: FileItem) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      try {
        await apiDeleteFile(file.id);
        const updated = await fetchFiles();
        setFiles(updated);
      } catch (e) {
        window.alert('Failed to delete file.');
      }
    }
    setOpenMenuId(null);
    setDropdownPos(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Details Modal */}
      {showDetailsModal && selectedFile && (
        <div className="file-details-modal-bg">
          <div className="file-details-modal">
            <button
              className="close-btn"
              onClick={() => setShowDetailsModal(false)}
              title="Close"
            >
              ×
            </button>
            <h2>File Details</h2>
            <div className="space-y-1">
              <div><b>Name:</b> {selectedFile.name}</div>
              <div><b>Type:</b> {selectedFile.type}</div>
              <div><b>Size:</b> {selectedFile.size}</div>
              <div><b>Modified:</b> {selectedFile.modified}</div>
              <div><b>Path:</b> {selectedFile.path}</div>
              {selectedFile.extension && <div><b>Extension:</b> {selectedFile.extension}</div>}
              {selectedFile.category && <div><b>Category:</b> {selectedFile.category}</div>}
              {selectedFile.permissions && <div><b>Permissions:</b> {selectedFile.permissions}</div>}
              {selectedFile.owner && <div><b>Owner:</b> {selectedFile.owner}</div>}
              <div><b>Tags:</b> {selectedFile.tags && selectedFile.tags.length > 0 ? selectedFile.tags.join(', ') : 'No tags'}</div>
            </div>
          </div>
        </div>
      )}
      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${showSidebar ? 'mr-80' : ''}`}>
        
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <h1 className="text-2xl font-bold text-gray-800">File Manager</h1>
        </div>
        {/* Search Bar above table, right-aligned */}
        <div className="w-full bg-white px-4 pt-4 pb-2 border-b border-gray-200 flex">
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64 ml-auto"
          />
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
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedFiles.map((file) => (
                    <tr 
                      key={file.id}
                      data-row-id={file.id}
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
                      <td className="file-table-cell text-right" style={{ position: 'relative', zIndex: 100 }}>
                        <div className="relative flex justify-end">
                          <button
                            className="file-action-menu-trigger"
                            title="Actions"
                            ref={el => { actionBtnRefs.current[file.id] = el; }}
                            onClick={e => {
                              e.stopPropagation();
                              e.preventDefault();
                              if (openMenuId === file.id) {
                                setOpenMenuId(null);
                                setDropdownPos(null);
                              } else {
                                setOpenMenuId(file.id);
                                // Use ref if available, else event.currentTarget
                                let btn = actionBtnRefs.current[file.id] || (e.currentTarget as HTMLButtonElement);
                                const rect = btn.getBoundingClientRect();
                                setDropdownPos({
                                  top: rect.bottom + window.scrollY + 4,
                                  left: rect.right + window.scrollX - 180
                                });
                              }
                            }}
                          >
                            <span style={{ fontSize: 22, fontWeight: 'bold', lineHeight: 1 }}>⋮</span>
                          </button>
      {/* Portal dropdown menu so it is never clipped */}
      {openMenuId && dropdownPos && (() => {
        const file = files.find(f => f.id === openMenuId);
        if (!file) return null;
        return createPortal(
          <div
            className="file-action-menu"
            style={{
              position: 'absolute',
              zIndex: 9999,
              top: dropdownPos.top,
              left: dropdownPos.left,
              minWidth: 148,
              maxWidth: 180,
              background: '#16281a',
              borderRadius: '0.7rem',
              boxShadow: '0 6px 18px 0 rgba(34,139,87,0.18)',
              border: '1px solid #2e8b57',
              padding: '0.15em 0',
            }}
            onMouseDown={e => e.stopPropagation()}
            onClick={e => e.stopPropagation()}
          >
            <button className="text-blue-600" onClick={e => { e.stopPropagation(); handleShowDetails(file); }}>Show Details</button>
            <button className="text-green-600" onClick={e => { e.stopPropagation(); handleAddTag(file); }}>Add Tag</button>
            <button className="text-yellow-600" onClick={e => { e.stopPropagation(); handleRemoveTag(file); }}>Remove Tag</button>
            <button className="text-purple-600" onClick={e => { e.stopPropagation(); handleMoveFile(file); }}>Move File</button>
            <button className="text-red-600" onClick={e => { e.stopPropagation(); handleDeleteFile(file); }}>Delete File</button>
          </div>,
          document.body
        );
      })()}
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
    </div>
  )
}

export default FileManager