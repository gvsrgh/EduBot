'use client';

import { useState } from 'react';
import styles from '../settings.module.css';

export default function UploadSection() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    // Filter for supported file types
    const validFiles = files.filter(file => {
      const validTypes = ['.pdf', '.txt', '.docx', '.doc'];
      return validTypes.some(type => file.name.toLowerCase().endsWith(type));
    });

    // Filter for max size (10MB)
    const maxSize = 10 * 1024 * 1024;
    const sizedFiles = validFiles.filter(file => file.size <= maxSize);

    setUploadedFiles(prev => [...prev, ...sizedFiles]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className={styles.sectionContent}>
      <div className={styles.sectionIntro}>
        <h3>📚 Knowledge Base Enhancement</h3>
        <p>Upload custom documents to expand EduBot's knowledge with your specific content</p>
      </div>

      <div 
        className={`${styles.uploadBox} ${isDragging ? styles.uploadBoxDragging : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className={styles.uploadIcon}>📄</div>
        <p className={styles.uploadText}>Drag & drop files here</p>
        <p className={styles.uploadHint}>or click to browse</p>
        <p className={styles.uploadSupported}>Supports PDF, TXT, DOCX files (Max 10MB each)</p>
        
        <input
          type="file"
          id="fileInput"
          multiple
          accept=".pdf,.txt,.docx,.doc"
          onChange={handleFileSelect}
          className={styles.fileInput}
        />
        <label htmlFor="fileInput" className={styles.uploadButton}>
          Choose Files
        </label>
      </div>

      {uploadedFiles.length > 0 && (
        <div className={styles.uploadedFilesList}>
          <h4>Uploaded Files ({uploadedFiles.length})</h4>
          <div className={styles.filesList}>
            {uploadedFiles.map((file, index) => (
              <div key={index} className={styles.fileItem}>
                <div className={styles.fileInfo}>
                  <span className={styles.fileIcon}>📎</span>
                  <div className={styles.fileDetails}>
                    <p className={styles.fileName}>{file.name}</p>
                    <p className={styles.fileSize}>{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className={styles.removeButton}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <button type="button" className={styles.uploadAllButton}>
            Upload All Files
          </button>
        </div>
      )}

      <div className={styles.uploadInfo}>
        <h4>ℹ️ Upload Guidelines</h4>
        <ul>
          <li>Documents will be processed and indexed for better search</li>
          <li>Supported formats: PDF, TXT, DOCX</li>
          <li>Maximum file size: 10MB per file</li>
          <li>Content will be available for all users in your organization</li>
        </ul>
      </div>
    </div>
  );
}
