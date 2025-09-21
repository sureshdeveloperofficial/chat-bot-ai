from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
import logging
from datetime import datetime
import shutil
import tempfile
import uuid

import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import PyPDF2
import docx2txt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Vector DB Service", version="1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./vector_storage")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(STORAGE_PATH, exist_ok=True)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

class SearchRequest(BaseModel):
    query: str
    username: str
    top_k: int = 5

class SearchResult(BaseModel):
    content: str
    metadata: Dict
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int

class DocumentInfo(BaseModel):
    id: str
    filename: str
    size: int
    chunks: int
    uploaded_at: str

def get_user_storage_path(username: str) -> str:
    user_path = os.path.join(STORAGE_PATH, username)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def load_user_index(username: str):
    user_path = get_user_storage_path(username)
    index_path = os.path.join(user_path, "faiss.index")
    metadata_path = os.path.join(user_path, "metadata.json")
    
    if os.path.exists(index_path) and os.path.exists(metadata_path):
        try:
            index = faiss.read_index(index_path)
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return index, metadata
        except Exception as e:
            logger.error(f"Error loading index for user {username}: {e}")
    
    return None, {}

def save_user_index(username: str, index, metadata: Dict):
    user_path = get_user_storage_path(username)
    index_path = os.path.join(user_path, "faiss.index")
    metadata_path = os.path.join(user_path, "metadata.json")
    
    try:
        faiss.write_index(index, index_path)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving index for user {username}: {e}")
        return False

def extract_text_from_file(file_path: str, filename: str) -> str:
    try:
        if filename.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        elif filename.lower().endswith('.docx'):
            return docx2txt.process(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to extract text from {filename}")

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Query(...)
):
    if not embeddings:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    document_id = str(uuid.uuid4())
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        text = extract_text_from_file(tmp_path, file.filename)
        
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text content found in file")
        
        chunk_embeddings = embeddings.embed_documents(chunks)
        embeddings_array = np.array(chunk_embeddings).astype('float32')
        
        index, metadata = load_user_index(username)
        
        if index is None:
            dimension = embeddings_array.shape[1]
            index = faiss.IndexFlatIP(dimension)
            metadata = {"documents": {}, "chunks": []}
        
        start_idx = len(metadata["chunks"])
        index.add(embeddings_array)
        
        for i, chunk in enumerate(chunks):
            metadata["chunks"].append({
                "document_id": document_id,
                "chunk_index": i,
                "content": chunk,
                "metadata": {
                    "filename": file.filename,
                    "chunk_number": i + 1,
                    "total_chunks": len(chunks)
                }
            })
        
        metadata["documents"][document_id] = {
            "filename": file.filename,
            "size": file.size or 0,
            "chunks": len(chunks),
            "uploaded_at": datetime.utcnow().isoformat(),
            "start_index": start_idx,
            "end_index": start_idx + len(chunks)
        }
        
        save_user_index(username, index, metadata)
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "message": "Document uploaded and indexed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        os.unlink(tmp_path)

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    if not embeddings:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    index, metadata = load_user_index(request.username)
    
    if index is None or not metadata.get("chunks"):
        return SearchResponse(results=[], total=0)
    
    try:
        query_embedding = embeddings.embed_query(request.query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        k = min(request.top_k, len(metadata["chunks"]))
        scores, indices = index.search(query_vector, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(metadata["chunks"]):
                chunk_data = metadata["chunks"][idx]
                results.append(SearchResult(
                    content=chunk_data["content"],
                    metadata=chunk_data["metadata"],
                    score=float(score)
                ))
        
        return SearchResponse(results=results, total=len(results))
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents(username: str = Query(...)):
    index, metadata = load_user_index(username)
    
    if not metadata.get("documents"):
        return []
    
    documents = []
    for doc_id, doc_data in metadata["documents"].items():
        documents.append(DocumentInfo(
            id=doc_id,
            filename=doc_data["filename"],
            size=doc_data["size"],
            chunks=doc_data["chunks"],
            uploaded_at=doc_data["uploaded_at"]
        ))
    
    return documents

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, username: str = Query(...)):
    index, metadata = load_user_index(username)
    
    if not metadata.get("documents") or document_id not in metadata["documents"]:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_data = metadata["documents"][document_id]
    start_idx = doc_data["start_index"]
    end_idx = doc_data["end_index"]
    
    new_chunks = []
    for i, chunk in enumerate(metadata["chunks"]):
        if not (start_idx <= i < end_idx):
            new_chunks.append(chunk)
    
    metadata["chunks"] = new_chunks
    del metadata["documents"][document_id]
    
    if new_chunks:
        all_embeddings = []
        for chunk in new_chunks:
            chunk_embedding = embeddings.embed_query(chunk["content"])
            all_embeddings.append(chunk_embedding)
        
        embeddings_array = np.array(all_embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        new_index = faiss.IndexFlatIP(dimension)
        new_index.add(embeddings_array)
        
        save_user_index(username, new_index, metadata)
    else:
        user_path = get_user_storage_path(username)
        index_path = os.path.join(user_path, "faiss.index")
        metadata_path = os.path.join(user_path, "metadata.json")
        
        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
    
    return {"message": f"Document {document_id} deleted successfully"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "vector",
        "openai_configured": bool(OPENAI_API_KEY),
        "storage_path": STORAGE_PATH
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)