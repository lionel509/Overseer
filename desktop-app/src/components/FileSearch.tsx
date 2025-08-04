import React, { useState, useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { executePythonCommand } from '../store/pythonSlice'
import { 
  Search, 
  Folder, 
  File, 
  FileText, 
  Image, 
  Video, 
  Music, 
  Archive,
  Download,
  Copy,
  ExternalLink,
  Filter,
  SortAsc,
  SortDesc,
  Eye,
  EyeOff,
  Calendar,
  HardDrive,
  Clock,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

interface FileItem {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  modified?: Date
  extension?: string
  isHidden?: boolean
  permissions?: string
}

interface SearchFilters {
  fileTypes: string[]
  sizeRange: { min: number; max: number }
  dateRange: { start: Date | null; end: Date | null }
  includeHidden: boolean
  searchInContent: boolean
}

interface SearchResult {
  files: FileItem[]
  totalCount: number
  searchTime: number
  query: string
}

const FileSearch: React.FC = () => {
  const dispatch = useAppDispatch()
  const { isConnected } = useAppSelector(state => state.python)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [currentDirectory, setCurrentDirectory] = useState('/')
  const [searchHistory, setSearchHistory] = useState<string[]>([])
  const [filters, setFilters] = useState<SearchFilters>({
    fileTypes: [],
    sizeRange: { min: 0, max: Infinity },
    dateRange: { start: null, end: null },
    includeHidden: false,
    searchInContent: false
  })
  const [showFilters, setShowFilters] = useState(false)
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'modified' | 'type'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const searchInputRef = useRef<HTMLInputElement>(null)

  // File type icons mapping
  const fileTypeIcons: Record<string, React.ReactNode> = {
    'txt': <FileText className="w-4 h-4 text-blue-600" />,
    'md': <FileText className="w-4 h-4 text-blue-600" />,
    'pdf': <FileText className="w-4 h-4 text-red-600" />,
    'doc': <FileText className="w-4 h-4 text-blue-600" />,
    'docx': <FileText className="w-4 h-4 text-blue-600" />,
    'jpg': <Image className="w-4 h-4 text-green-600" />,
    'jpeg': <Image className="w-4 h-4 text-green-600" />,
    'png': <Image className="w-4 h-4 text-green-600" />,
    'gif': <Image className="w-4 h-4 text-green-600" />,
    'mp4': <Video className="w-4 h-4 text-purple-600" />,
    'avi': <Video className="w-4 h-4 text-purple-600" />,
    'mov': <Video className="w-4 h-4 text-purple-600" />,
    'mp3': <Music className="w-4 h-4 text-orange-600" />,
    'wav': <Music className="w-4 h-4 text-orange-600" />,
    'zip': <Archive className="w-4 h-4 text-yellow-600" />,
    'tar': <Archive className="w-4 h-4 text-yellow-600" />,
    'gz': <Archive className="w-4 h-4 text-yellow-600" />
  }

  useEffect(() => {
    // Focus search input on mount
    if (searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [])

  const handleSearch = async (query: string = searchQuery) => {
    if (!query.trim() || !isConnected) return

    setIsSearching(true)
    const startTime = Date.now()

    try {
      // Execute file search command
      const response = await dispatch(executePythonCommand({
        command: 'file_search',
        args: [query, currentDirectory, JSON.stringify(filters)]
      }))

      if (response.payload?.success) {
        const results: SearchResult = {
          files: response.payload.data || [],
          totalCount: response.payload.data?.length || 0,
          searchTime: Date.now() - startTime,
          query: query
        }
        setSearchResults(results)

        // Add to search history
        if (!searchHistory.includes(query)) {
          setSearchHistory(prev => [query, ...prev.slice(0, 9)]) // Keep last 10
        }
      } else {
        console.error('Search failed:', response.payload?.error)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleSearch()
    } else if (event.key === 'Escape') {
      setSearchQuery('')
      setSearchResults(null)
    }
  }

  const handleFileSelect = (filePath: string) => {
    const newSelected = new Set(selectedFiles)
    if (newSelected.has(filePath)) {
      newSelected.delete(filePath)
    } else {
      newSelected.add(filePath)
    }
    setSelectedFiles(newSelected)
  }

  const handleSelectAll = () => {
    if (searchResults) {
      const allPaths = searchResults.files.map(f => f.path)
      setSelectedFiles(new Set(allPaths))
    }
  }

  const handleDeselectAll = () => {
    setSelectedFiles(new Set())
  }

  const handleFileAction = async (action: string, filePath: string) => {
    try {
      switch (action) {
        case 'open':
          await window.electronAPI.system.openFile(filePath)
          break
        case 'copy_path':
          await navigator.clipboard.writeText(filePath)
          break
        case 'show_in_folder':
          // This would require additional IPC implementation
          console.log('Show in folder:', filePath)
          break
        default:
          console.log('Unknown action:', action)
      }
    } catch (error) {
      console.error('File action error:', error)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const getFileIcon = (file: FileItem): React.ReactNode => {
    if (file.type === 'directory') {
      return <Folder className="w-4 h-4 text-blue-600" />
    }

    const ext = file.extension?.toLowerCase()
    return fileTypeIcons[ext || ''] || <File className="w-4 h-4 text-gray-600" />
  }

  const sortFiles = (files: FileItem[]): FileItem[] => {
    return [...files].sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'size':
          comparison = (a.size || 0) - (b.size || 0)
          break
        case 'modified':
          comparison = (a.modified?.getTime() || 0) - (b.modified?.getTime() || 0)
          break
        case 'type':
          comparison = a.type.localeCompare(b.type)
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })
  }

  const filteredResults = searchResults ? sortFiles(searchResults.files) : []

  if (!isConnected) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="text-yellow-800">Python backend not connected</span>
          </div>
          <p className="text-yellow-700 mt-2">
            Connect to the Python backend to use file search.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">File Search</h1>
          <p className="text-gray-600">Search files and directories with native file system access</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Search className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Search Files</h3>
        </div>
        
        <div className="space-y-4">
          {/* Search input */}
          <div className="relative">
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter search query (e.g., *.txt, document, /path/to/search)..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isSearching}
            />
            <button
              onClick={() => handleSearch()}
              disabled={!searchQuery.trim() || isSearching}
              className="absolute right-2 top-2 px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSearching ? (
                <div className="flex items-center space-x-1">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Searching</span>
                </div>
              ) : (
                <span>Search</span>
              )}
            </button>
          </div>

          {/* Current directory */}
          <div className="flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Current directory:</span>
            <span className="text-sm font-mono text-gray-800">{currentDirectory}</span>
          </div>

          {/* Search history */}
          {searchHistory.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-gray-600">Recent searches:</span>
              {searchHistory.slice(0, 5).map((query, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setSearchQuery(query)
                    handleSearch(query)
                  }}
                  className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Filter className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Search Filters</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* File types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">File Types</label>
              <div className="space-y-1">
                {['txt', 'pdf', 'doc', 'jpg', 'png', 'mp4', 'mp3', 'zip'].map(type => (
                  <label key={type} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.fileTypes.includes(type)}
                      onChange={(e) => {
                        const newTypes = e.target.checked
                          ? [...filters.fileTypes, type]
                          : filters.fileTypes.filter(t => t !== type)
                        setFilters(prev => ({ ...prev, fileTypes: newTypes }))
                      }}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">{type.toUpperCase()}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Size range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Size Range</label>
              <div className="space-y-2">
                <input
                  type="number"
                  placeholder="Min size (KB)"
                  value={filters.sizeRange.min === 0 ? '' : filters.sizeRange.min}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    sizeRange: { ...prev.sizeRange, min: parseInt(e.target.value) || 0 }
                  }))}
                  className="w-full p-2 border border-gray-300 rounded text-sm"
                />
                <input
                  type="number"
                  placeholder="Max size (KB)"
                  value={filters.sizeRange.max === Infinity ? '' : filters.sizeRange.max}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    sizeRange: { ...prev.sizeRange, max: parseInt(e.target.value) || Infinity }
                  }))}
                  className="w-full p-2 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>

            {/* Date range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
              <div className="space-y-2">
                <input
                  type="date"
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, start: e.target.value ? new Date(e.target.value) : null }
                  }))}
                  className="w-full p-2 border border-gray-300 rounded text-sm"
                />
                <input
                  type="date"
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, end: e.target.value ? new Date(e.target.value) : null }
                  }))}
                  className="w-full p-2 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>

            {/* Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Options</label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={filters.includeHidden}
                    onChange={(e) => setFilters(prev => ({ ...prev, includeHidden: e.target.checked }))}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">Include hidden files</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={filters.searchInContent}
                    onChange={(e) => setFilters(prev => ({ ...prev, searchInContent: e.target.checked }))}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">Search in content</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Search className="w-6 h-6 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Search Results</h3>
              <span className="text-sm text-gray-500">
                ({searchResults.totalCount} files, {searchResults.searchTime}ms)
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {/* Sort controls */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-2 py-1 text-sm border border-gray-300 rounded"
              >
                <option value="name">Name</option>
                <option value="size">Size</option>
                <option value="modified">Modified</option>
                <option value="type">Type</option>
              </select>
              <button
                onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                className="p-1 text-gray-500 hover:text-gray-700"
              >
                {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Selection controls */}
          <div className="flex items-center justify-between mb-4 p-2 bg-gray-50 rounded">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {selectedFiles.size} of {filteredResults.length} selected
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleSelectAll}
                className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Select All
              </button>
              <button
                onClick={handleDeselectAll}
                className="px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Deselect All
              </button>
            </div>
          </div>

          {/* Results list */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredResults.map((file) => (
              <div
                key={file.path}
                className={`flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors ${
                  selectedFiles.has(file.path) ? 'bg-blue-50 border-blue-200' : 'border-gray-200'
                }`}
              >
                <div className="flex items-center space-x-3 flex-1">
                  <input
                    type="checkbox"
                    checked={selectedFiles.has(file.path)}
                    onChange={() => handleFileSelect(file.path)}
                    className="rounded"
                  />
                  <div className="flex items-center space-x-2">
                    {getFileIcon(file)}
                    <div>
                      <div className="font-medium text-gray-900">{file.name}</div>
                      <div className="text-sm text-gray-500">{file.path}</div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  {file.size && (
                    <span>{formatFileSize(file.size)}</span>
                  )}
                  {file.modified && (
                    <span>{formatDate(file.modified)}</span>
                  )}
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleFileAction('open', file.path)}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title="Open file"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleFileAction('copy_path', file.path)}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title="Copy path"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {filteredResults.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No files found</p>
                <p className="text-sm">Try adjusting your search query or filters</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FileSearch 