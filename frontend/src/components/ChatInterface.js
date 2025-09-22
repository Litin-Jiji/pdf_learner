import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// Configure axios with timeout
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 45000, // 45 seconds timeout for chat
});

const ChatInterface = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await api.post('/chat', {
        question: userMessage,
        session_id: sessionId
      });

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMessage = 'Sorry, I encountered an error while processing your question. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout. The AI is taking too long to respond. Please try a simpler question.';
      } else if (error.response) {
        const status = error.response.status;
        switch (status) {
          case 404:
            errorMessage = 'No PDF found for this session. Please upload a PDF first.';
            break;
          case 408:
            errorMessage = 'Request timeout. The AI is taking too long to respond. Please try a simpler question.';
            break;
          case 500:
            errorMessage = 'Server error. Please try again in a moment.';
            break;
          default:
            errorMessage = error.response.data?.detail || errorMessage;
        }
      } else if (error.request) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: errorMessage
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="message assistant">
            👋 Hello! I'm ready to answer questions about your PDF. What would you like to know?
          </div>
        )}
        
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="loading">
              <div className="spinner"></div>
              <span>Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the PDF..."
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={!inputMessage.trim() || isLoading}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;

