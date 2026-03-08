'use client';

import { useState, useEffect, useCallback } from 'react';
import styles from '../settings.module.css';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

interface UploadedFile {
  filename: string;
  category: string;
  size: number;
  modified: number;
}

export default function KnowledgeBase() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [deletingFile, setDeletingFile] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<{
    show: boolean;
    success: boolean;
    message: string;
  }>({ show: false, success: false, message: '' });

  const fetchFiles = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API_BASE}/settings/files`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        // Sort by modified time descending (latest first)
        const sorted = (data.files || []).sort(
          (a: UploadedFile, b: UploadedFile) => b.modified - a.modified
        );
        setFiles(sorted);
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  // Listen for custom event from UploadSection to refresh file list
  useEffect(() => {
    const handler = () => fetchFiles();
    window.addEventListener('kb-files-updated', handler);
    return () => window.removeEventListener('kb-files-updated', handler);
  }, [fetchFiles]);

  const deleteFile = async (category: string, filename: string) => {
    const key = `${category}/${filename}`;
    if (!confirm(`Delete "${filename}" from ${category}?`)) return;

    setDeletingFile(key);
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Not authenticated');

      const response = await fetch(
        `${API_BASE}/settings/files/${encodeURIComponent(category)}/${encodeURIComponent(filename)}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );

      if (response.ok) {
        setStatusMessage({
          show: true,
          success: true,
          message: `Deleted "${filename}"`,
        });
        fetchFiles();
        setTimeout(() => setStatusMessage({ show: false, success: false, message: '' }), 3000);
      } else {
        const error = await response.json();
        setStatusMessage({
          show: true,
          success: false,
          message: error.detail || 'Delete failed',
        });
      }
    } catch (error) {
      setStatusMessage({
        show: true,
        success: false,
        message: error instanceof Error ? error.message : 'Delete failed',
      });
    } finally {
      setDeletingFile(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Academic': return '📅';
      case 'Administrative': return '🏛️';
      case 'Educational': return '📖';
      default: return '📄';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Academic': return styles.categoryAcademic;
      case 'Administrative': return styles.categoryAdministrative;
      case 'Educational': return styles.categoryEducational;
      default: return '';
    }
  };

  // Filter files by search query
  const filteredFiles = files.filter(f =>
    f.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.kbContainer}>
      <div className={styles.kbHeader}>
        <h3>📂 Knowledge Base</h3>
        <span className={styles.kbCount}>{files.length} file{files.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Search Bar */}
      <div className={styles.kbSearchWrapper}>
        <span className={styles.kbSearchIcon}>🔍</span>
        <input
          type="text"
          placeholder="Search files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className={styles.kbSearchInput}
        />
        {searchQuery && (
          <button
            type="button"
            className={styles.kbSearchClear}
            onClick={() => setSearchQuery('')}
          >
            ✕
          </button>
        )}
      </div>

      {/* Status Message */}
      {statusMessage.show && (
        <div className={`${styles.kbStatus} ${statusMessage.success ? styles.kbStatusSuccess : styles.kbStatusError}`}>
          {statusMessage.success ? '✓' : '✗'} {statusMessage.message}
        </div>
      )}

      {/* File List */}
      <div className={styles.kbFileList}>
        {loading ? (
          <div className={styles.kbEmpty}>Loading files...</div>
        ) : filteredFiles.length === 0 ? (
          <div className={styles.kbEmpty}>
            {searchQuery ? `No files matching "${searchQuery}"` : 'No files uploaded yet'}
          </div>
        ) : (
          filteredFiles.map((file, index) => {
            const key = `${file.category}/${file.filename}`;
            return (
              <div key={index} className={styles.kbFileItem}>
                <div className={styles.kbFileIcon}>
                  {getCategoryIcon(file.category)}
                </div>
                <div className={styles.kbFileDetails}>
                  <p className={styles.kbFileName} title={file.filename}>
                    {file.filename}
                  </p>
                  <div className={styles.kbFileMeta}>
                    <span className={`${styles.kbCategoryBadge} ${getCategoryColor(file.category)}`}>
                      {file.category}
                    </span>
                    <span className={styles.kbFileSizeDot}>·</span>
                    <span>{formatFileSize(file.size)}</span>
                    <span className={styles.kbFileSizeDot}>·</span>
                    <span>{formatDate(file.modified)}</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => deleteFile(file.category, file.filename)}
                  className={styles.kbDeleteBtn}
                  title="Delete file"
                  disabled={deletingFile === key}
                >
                  {deletingFile === key ? '⏳' : '🗑️'}
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Summary footer */}
      {files.length > 0 && (
        <div className={styles.kbFooter}>
          {filteredFiles.length !== files.length && (
            <span>Showing {filteredFiles.length} of {files.length}</span>
          )}
        </div>
      )}
    </div>
  );
}
