# PDF Chat Project

A modern web application that allows you to chat with your PDF documents using AI. The project consists of a FastAPI backend and a React frontend.

## Features

- 📄 Upload PDF documents
- 🤖 Chat with your PDF using AI (Google Gemini)
- 💬 Real-time chat interface
- 🎨 Modern, responsive UI
- 🔄 Session-based document management

## Project Structure

```
pdf_chat_project/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── pdf_processor.py    # PDF processing logic
│   ├── rag_chain.py        # RAG chain implementation
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── PDFUploader.js
│   │   │   └── ChatInterface.js
│   │   ├── App.js          # Main App component
│   │   └── App.css         # Styling
│   └── package.json        # Node.js dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the FastAPI server:
   ```bash
   python main.py
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## Usage

1. Start both the backend and frontend servers
2. Open your browser and go to `http://localhost:3000`
3. Upload a PDF file
4. Start chatting with your document!

## API Endpoints

- `POST /upload-pdf` - Upload and process a PDF file
- `POST /chat` - Send a message to chat with the PDF
- `GET /health` - Health check endpoint

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- LangChain - LLM application framework
- Google Gemini - AI model for chat and embeddings
- FAISS - Vector database for similarity search
- PyMuPDF - PDF processing

### Frontend
- React - JavaScript library for building user interfaces
- Axios - HTTP client for API calls
- CSS3 - Modern styling with gradients and animations

## Configuration

The Google API key is currently hardcoded in the backend. For production use, consider using environment variables:

```python
import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

## Development

To run both servers simultaneously, you can use two terminal windows or a process manager like `concurrently`.

## License

This project is for educational purposes.
