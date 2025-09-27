from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import httpx
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Document Search API", version="1.0.0")

# Vector store service URL
VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL", "http://localhost:8001")

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.5  # Higher default threshold for better quality results

class SearchResult(BaseModel):
    document_id: str
    filename: str
    page_number: int
    line_number: int
    text_fragment: str
    similarity_score: float

class SearchResponse(BaseModel):
    query: str
    response_time_ms: float
    number_of_results: int
    results: List[SearchResult]

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    lines_processed: int
    message: str

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_date: datetime
    lines_count: int
    first_page: int
    last_page: int

@app.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF document to the vector store for indexing.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Upload response with document ID and processing details
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Prepare the file for upload to vector store
        files = {"file": (file.filename, file_content, "application/pdf")}
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{VECTOR_STORE_URL}/upload-pdf",
                files=files
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            return UploadResponse(**response.json())
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@app.post("/search-doc", response_model=SearchResponse)
async def search_documents(search_request: SearchRequest):
    """
    Search for documents using the provided search string.
    
    Args:
        search_request: Search query and optional limit
        
    Returns:
        Search response with timing, count, and matching document fragments
    """
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VECTOR_STORE_URL}/search",
                json=search_request.dict()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            search_results_data = response.json()
            
            # Convert to new format and filter by similarity
            search_results = []
            for result in search_results_data:
                similarity_score = result["similarity_score"]
                if similarity_score >= search_request.min_similarity:
                    search_result = SearchResult(
                        document_id=result["document_id"],
                        filename=result["filename"],
                        page_number=result["page_number"],
                        line_number=result["line_number"],
                        text_fragment=result["content"],
                        similarity_score=similarity_score
                    )
                    search_results.append(search_result)
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return SearchResponse(
                query=search_request.query,
                response_time_ms=round(response_time_ms, 2),
                number_of_results=len(search_results),
                results=search_results
            )
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during search: {str(e)}"
        )

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get all lines for a specific document by document ID.
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        Document with all its lines
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{VECTOR_STORE_URL}/documents/{document_id}"
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document: {str(e)}"
        )

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    Get list of all documents with metadata.
    
    Returns:
        List of documents with metadata including upload date, line counts, and page ranges
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{VECTOR_STORE_URL}/documents")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@app.delete("/documents")
async def delete_all_documents():
    """
    Delete all documents from the vector store.
    
    Returns:
        Deletion confirmation with count of deleted documents and lines
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{VECTOR_STORE_URL}/documents")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting all documents: {str(e)}"
        )

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a specific document by document ID.
    
    Args:
        document_id: The ID of the document to delete
        
    Returns:
        Deletion confirmation with document details
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{VECTOR_STORE_URL}/documents/{document_id}")
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vector store error: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to vector store service: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if vector store is healthy
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VECTOR_STORE_URL}/health")
            vector_store_healthy = response.status_code == 200
    except:
        vector_store_healthy = False
    
    return {
        "status": "healthy",
        "service": "api-backend",
        "vector_store_connected": vector_store_healthy
    }

# Root endpoint with API information
@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "message": "Document Search API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload-pdf - Upload PDF documents",
            "search": "/search-doc - Search documents",
            "documents": "/documents - List all documents",
            "document": "/documents/{document_id} - Get document by ID",
            "delete_all": "DELETE /documents - Delete all documents",
            "delete_one": "DELETE /documents/{document_id} - Delete specific document",
            "health": "/health - Health check"
        },
        "docs": "/docs - Interactive API documentation"
    }

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Cloud Run, fallback to 8000 for local dev
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)