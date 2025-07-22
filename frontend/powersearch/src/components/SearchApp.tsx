import React, { useState, useEffect, useRef } from 'react';

interface SearchResult {
  success: boolean;
  data?: any;
  error?: string;
}

interface FileType {
  id: string;
  label: string;
  icon: string;
  keywords: string[];
}

interface SearchResultItem {
  id: string;
  title: string;
  description: string;
  type: string;
}

const fileTypes: FileType[] = [
  { id: 'all', label: 'All Files', icon: '🔍', keywords: [] },
  { id: 'pdf', label: 'PDF', icon: '📄', keywords: ['pdf:', 'document:'] },
  { id: 'text', label: 'Text', icon: '📝', keywords: ['text:', 'txt:'] },
];

const SearchApp: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedFileType, setSelectedFileType] = useState<FileType>(fileTypes[0]);
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [showResults, setShowResults] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Mock search results for demonstration
  const mockSearchResults: SearchResultItem[] = [
    { id: '1', title: 'Document.pdf', description: 'Financial report from Q4 2023', type: 'pdf' },
    { id: '2', title: 'Report.pdf', description: 'Annual sales report', type: 'pdf' },
    { id: '3', title: 'Notes.txt', description: 'Meeting notes from last week', type: 'text' },
    { id: '4', title: 'README.txt', description: 'Project documentation', type: 'text' },
    { id: '5', title: 'Invoice.pdf', description: 'Client invoice #1234', type: 'pdf' },
  ];

  // Auto-detect file type based on query
  const getFileTypeFromQuery = (query: string): FileType => {
    const lowerQuery = query.toLowerCase();
    
    for (const fileType of fileTypes.slice(1)) { // Skip 'all' type
      if (fileType.keywords.some(keyword => lowerQuery.includes(keyword))) {
        return fileType;
      }
    }
    
    return fileTypes[0]; // Default to 'all'
  };

  useEffect(() => {
    const detectedType = getFileTypeFromQuery(searchQuery);
    if (detectedType.id !== selectedFileType.id && selectedFileType.id === 'all') {
      setSelectedFileType(detectedType);
    } else if (searchQuery === '' && selectedFileType.id !== 'all') {
      setSelectedFileType(fileTypes[0]);
    }
  }, [searchQuery, selectedFileType.id]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      
      // Check if click is outside both dropdown and button
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(target) &&
        buttonRef.current &&
        !buttonRef.current.contains(target)
      ) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isDropdownOpen]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(event.target.value);
    // Hide results when query is empty
    if (event.target.value.trim() === '') {
      setShowResults(false);
    }
  };

  const handleFileTypeSelect = (fileType: FileType): void => {
    console.log('File type selected:', fileType.label);
    setSelectedFileType(fileType);
    setIsDropdownOpen(false);
  };

  const handleKeyPress = async (event: React.KeyboardEvent<HTMLInputElement>): Promise<void> => {
    if (event.key === 'Enter') {
      event.preventDefault();
      
      if (searchQuery.trim() === '') {
        return;
      }

      setIsLoading(true);
      setShowResults(false);

      try {
        // Pass both query and selected file type
        const result: SearchResult = await window.electronAPI.searchQuery(
          searchQuery.trim(),
          selectedFileType.id
        );
        
        if (result.success) {
          console.log('Search successful:', result.data);
          
          // Filter mock results based on file type
          let filteredResults = mockSearchResults;
          if (selectedFileType.id !== 'all') {
            filteredResults = mockSearchResults.filter(item => {
              return item.type === selectedFileType.id;
            });
          }
          
          setSearchResults(filteredResults);
          setShowResults(true);
        } else {
          console.error('Search failed:', result.error);
          setSearchResults([]);
          setShowResults(true);
        }
      } catch (error) {
        console.error('Error during search:', error);
        setSearchResults([]);
        setShowResults(true);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDropdownToggle = (event: React.MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    setIsDropdownOpen(prev => !prev);
  };

  const handleAllFilesClick = (event: React.MouseEvent<HTMLDivElement>): void => {
    console.log('All Files clicked');
    event.stopPropagation();
    handleFileTypeSelect(fileTypes[0]);
  };

  const handlePdfClick = (event: React.MouseEvent<HTMLDivElement>): void => {
    console.log('PDF clicked');
    event.stopPropagation();
    handleFileTypeSelect(fileTypes[1]);
  };

  const handleTextClick = (event: React.MouseEvent<HTMLDivElement>): void => {
    console.log('Text clicked');
    event.stopPropagation();
    handleFileTypeSelect(fileTypes[2]);
  };

  const handleResultClick = (item: SearchResultItem): void => {
    console.log('Opening item:', item);
    // Here you would implement the logic to open the file
  };

  return (
    <div className="search-app">
      <div className="search-container">
        <div className="search-input-wrapper">
          <div className="file-type-dropdown">
            <button
              ref={buttonRef}
              className="dropdown-button"
              onClick={handleDropdownToggle}
              aria-expanded={isDropdownOpen}
              aria-haspopup="true"
              disabled={isLoading}
              type="button"
            >
              <span>{selectedFileType.icon}</span>
              <span className="dropdown-arrow">▼</span>
            </button>
            
            <div 
              ref={dropdownRef}
              className={`dropdown-menu ${isDropdownOpen ? 'open' : ''}`}
            >
              {/* All Files Option */}
              <div
                className={`dropdown-item ${selectedFileType.id === 'all' ? 'selected' : ''}`}
                onClick={handleAllFilesClick}
                role="menuitem"
                tabIndex={0}
              >
                <span>🔍</span>
                <span>All Files</span>
              </div>
              
              {/* PDF Option */}
              <div
                className={`dropdown-item ${selectedFileType.id === 'pdf' ? 'selected' : ''}`}
                onClick={handlePdfClick}
                role="menuitem"
                tabIndex={0}
              >
                <span>📄</span>
                <span>PDF</span>
              </div>
              
              {/* Text Option */}
              <div
                className={`dropdown-item ${selectedFileType.id === 'text' ? 'selected' : ''}`}
                onClick={handleTextClick}
                role="menuitem"
                tabIndex={0}
              >
                <span>📝</span>
                <span>Text</span>
              </div>
            </div>
          </div>
          
          <input
            type="text"
            className="search-input"
            placeholder="Search anything..."
            value={searchQuery}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            autoFocus
            disabled={isLoading}
          />
          
          <span className="right-icon" aria-label="Search icon">
            {isLoading ? '⏳' : '🔍'}
          </span>
        </div>
      </div>
      
      <div className={`search-results ${showResults ? 'visible' : ''}`}>
        {isLoading ? (
          <div className="search-results-header">Searching...</div>
        ) : searchResults.length > 0 ? (
          <>
            <div className="search-results-header">
              Found {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
            </div>
            {searchResults.map((item) => (
              <div
                key={item.id}
                className="search-result-item"
                onClick={() => handleResultClick(item)}
              >
                <div className="search-result-title">{item.title}</div>
                <div className="search-result-description">{item.description}</div>
              </div>
            ))}
          </>
        ) : showResults ? (
          <div className="no-results">No results found for "{searchQuery}"</div>
        ) : null}
      </div>
    </div>
  );
};

export default SearchApp; 
