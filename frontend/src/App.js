import React, { useState } from 'react';
import './App.css';
import PDFUploader from './components/PDFUploader';
import ChatInterface from './components/ChatInterface';

function App() {
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [isPDFUploaded, setIsPDFUploaded] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');

  const handlePDFUploaded = (fileName) => {
    setIsPDFUploaded(true);
    setUploadedFileName(fileName);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 AI PDF Reader & Chatbot</h1>
        <p>Upload a PDF and start chatting with your document!</p>
      </header>
      
      <main className="App-main">
        {!isPDFUploaded ? (
          <PDFUploader 
            sessionId={sessionId} 
            onUploaded={handlePDFUploaded}
          />
        ) : (
          <div className="chat-container">
            <div className="upload-info">
              <p>✅ PDF uploaded: <strong>{uploadedFileName}</strong></p>
              <button 
                className="upload-new-btn"
                onClick={() => {
                  setIsPDFUploaded(false);
                  setUploadedFileName('');
                }}
              >
                Upload New PDF
              </button>
            </div>
            <ChatInterface sessionId={sessionId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;