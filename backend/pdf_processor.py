import os
import tempfile
from typing import Optional

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def build_retriever_from_pdf_bytes(pdf_bytes: bytes):
    """Create a retriever from raw PDF bytes using Gemini embeddings and FAISS.

    Steps:
    - Persist the uploaded bytes to a temp PDF
    - Load pages with PyMuPDFLoader
    - Split with RecursiveCharacterTextSplitter
    - Embed with GoogleGenerativeAIEmbeddings (text-embedding-004)
    - Index with FAISS and return a retriever
    """
    tmp_file_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        loader = PyMuPDFLoader(tmp_file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        return vectorstore.as_retriever()
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


