import React, { useState } from 'react';
import axios from 'axios';

// Configure axios with timeout
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000, // 2 minutes timeout for uploads
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

const PDFUploader = ({ sessionId, onUploaded }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      setError('Please select a PDF file.');
      return;
    }

    // Validate file size (10MB limit)
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_FILE_SIZE) {
      setError('File too large. Maximum size is 10MB.');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      await api.post('/upload-pdf', formData);
      
      setSuccess(`PDF uploaded and processed successfully! (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
      onUploaded(file.name);
    } catch (error) {
      console.error('Upload error:', error);
      
      let errorMessage = 'An error occurred while uploading the PDF. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Upload timeout. The file is too large or the server is taking too long to respond.';
      } else if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        switch (status) {
          case 408:
            errorMessage = 'Request timeout. The PDF is too large or complex to process.';
            break;
          case 413:
            errorMessage = 'File too large. Maximum size is 10MB.';
            break;
          case 500:
            errorMessage = 'Server error while processing PDF. Please try again.';
            break;
          default:
            errorMessage = error.response.data?.detail || errorMessage;
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-icon">📄</div>
      <div className="upload-text">
        Drag and drop your PDF file here, or click to browse
      </div>
      
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileUpload}
        className="file-input"
        id="pdf-upload"
        disabled={isUploading}
      />
      
      <label htmlFor="pdf-upload" className="upload-btn">
        {isUploading ? 'Processing...' : 'Choose PDF File'}
      </label>

      {isUploading && (
        <div className="loading">
          <div className="spinner"></div>
          <span>Processing PDF... This may take a moment.</span>
        </div>
      )}

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {success && (
        <div className="success">
          {success}
        </div>
      )}
    </div>
  );
};

export default PDFUploader;

