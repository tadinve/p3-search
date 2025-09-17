from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import lancedb
import PyPDF2
import pdfplumber
from sentence_transformers import SentenceTransformer
import numpy as np
import uuid
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import tempfile
import io
from datetime import datetime
import pandas as pd

app = FastAPI(title="Vector Store Service", version="1.0.0")

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize LanceDB
DB_PATH = "./lancedb_data"
os.makedirs(DB_PATH, exist_ok=True)

# We'll initialize the table lazily when we first add data
table = None

def get_table():
    """Get or create the LanceDB table"""
    global table
    if table is None:
        db = lancedb.connect(DB_PATH)
        try:
            table = db.open_table("documents")
        except:
            # Create table with first document - we'll handle this in upload_pdf
            pass
    return table

def create_table_with_data(documents_to_insert):
    """Create table with initial data"""
    global table
    db = lancedb.connect(DB_PATH)
    table = db.create_table("documents", documents_to_insert)
    return table

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.5

class SearchResult(BaseModel):
    document_id: str
    filename: str
    page_number: int
    line_number: int
    content: str
    similarity_score: float

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_date: datetime
    lines_count: int
    first_page: int
    last_page: int

def extract_text_from_pdf(pdf_file) -> List[Dict[str, Any]]:
    """Extract text from PDF and return as list of line objects with page info, treating table rows as single lines"""
    try:
        text_lines = []
        global_line_number = 1
        
        # Reset file pointer to beginning
        pdf_file.seek(0)
        
        # Use pdfplumber for better table detection
        with pdfplumber.open(pdf_file) as pdf:
            for page_number, page in enumerate(pdf.pages, 1):
                # Extract tables from the page
                tables = page.extract_tables()
                table_cells = set()  # Keep track of table cell positions
                
                # Process tables first and mark their cell positions
                for table in tables:
                    for row_idx, row in enumerate(table):
                        if row and any(cell and str(cell).strip() for cell in row):  # Skip empty rows
                            # Combine all cells in the row into a single line
                            row_text_parts = []
                            for cell in row:
                                if cell and str(cell).strip():
                                    row_text_parts.append(str(cell).strip())
                            
                            if row_text_parts:  # Only add non-empty rows
                                row_text = " | ".join(row_text_parts)  # Use | as column separator
                                text_lines.append({
                                    "content": f"[TABLE] {row_text}",  # Mark as table content
                                    "page_number": page_number,
                                    "line_number": global_line_number,
                                    "is_table": True
                                })
                                global_line_number += 1
                
                # Extract regular text, but try to avoid table content
                page_text = page.extract_text()
                if page_text:
                    lines = page_text.split('\n')
                    # Filter out empty lines and strip whitespace
                    lines = [line.strip() for line in lines if line.strip()]
                    
                    for line_content in lines:
                        # Skip lines that are likely part of tables we've already processed
                        # This is a heuristic - if the line contains multiple separated values, it might be a table
                        is_likely_table_line = False
                        if tables:  # Only apply this logic if tables were found on the page
                            # Check if this line looks like table data (contains multiple | or tab-separated values)
                            separators = ['\t', '  ', '   ', '    ']  # Common table separators
                            for sep in separators:
                                if len(line_content.split(sep)) >= 3:  # Likely table if 3+ columns
                                    is_likely_table_line = True
                                    break
                        
                        # Only add non-table lines or if no tables were found on this page
                        if not is_likely_table_line or not tables:
                            text_lines.append({
                                "content": line_content,
                                "page_number": page_number,
                                "line_number": global_line_number,
                                "is_table": False
                            })
                            global_line_number += 1
        
        return text_lines
    except Exception as e:
        # Fallback to PyPDF2 if pdfplumber fails
        try:
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_lines = []
            global_line_number = 1
            
            for page_number, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                lines = page_text.split('\n')
                # Filter out empty lines and strip whitespace
                lines = [line.strip() for line in lines if line.strip()]
                
                for line_content in lines:
                    text_lines.append({
                        "content": line_content,
                        "page_number": page_number,
                        "line_number": global_line_number,
                        "is_table": False
                    })
                    global_line_number += 1
            
            return text_lines
        except Exception as fallback_error:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)} (Fallback error: {str(fallback_error)})")

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using sentence transformer"""
    embedding = model.encode(text)
    return embedding.tolist()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read the uploaded file
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract text lines from PDF
        text_lines = extract_text_from_pdf(pdf_file)
        
        if not text_lines:
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Process each line and store in vector database
        documents_to_insert = []
        upload_date = datetime.now()
        
        for line_data in text_lines:
            line_content = line_data["content"]
            if len(line_content.strip()) > 10:  # Only process meaningful lines
                vector = generate_embedding(line_content)
                
                document_entry = {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "content": line_content,
                    "page_number": line_data["page_number"],
                    "line_number": line_data["line_number"],
                    "filename": file.filename,
                    "upload_date": upload_date,
                    "is_table": line_data.get("is_table", False),
                    "vector": vector
                }
                documents_to_insert.append(document_entry)
        
        # Insert documents into LanceDB
        if documents_to_insert:
            current_table = get_table()
            if current_table is None:
                # Create table with first batch of documents
                create_table_with_data(documents_to_insert)
            else:
                # Add to existing table
                current_table.add(documents_to_insert)
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "lines_processed": len(documents_to_insert),
            "message": "PDF uploaded and processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/search", response_model=List[SearchResult])
async def search_documents(search_request: SearchRequest):
    """Search for documents using vector similarity"""
    try:
        current_table = get_table()
        if current_table is None:
            return []
        
        # Generate embedding for search query
        query_vector = generate_embedding(search_request.query)
        
        # Perform vector search
        results = current_table.search(query_vector).limit(search_request.limit).to_list()
        
        # Format results and filter by similarity threshold
        search_results = []
        for result in results:
            # Convert distance to similarity (lower distance = higher similarity)
            # LanceDB returns squared L2 distance, convert to similarity score between 0-1
            distance = float(result["_distance"])
            similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity
            
            # Only include results above the similarity threshold
            if similarity_score >= search_request.min_similarity:
                search_result = SearchResult(
                    document_id=result["document_id"],
                    filename=result["filename"],
                    page_number=result["page_number"],
                    line_number=result["line_number"],
                    content=result["content"],
                    similarity_score=similarity_score
                )
                search_results.append(search_result)
        
        # Sort by similarity score (highest first)
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return search_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document_lines(document_id: str):
    """Get all lines for a specific document"""
    try:
        current_table = get_table()
        if current_table is None:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Search for all entries with the given document_id
        # Use a different approach for filtering
        all_results = current_table.to_pandas()
        results = all_results[all_results['document_id'] == document_id]
        
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Sort by line number and convert to list of dicts
        results = results.sort_values('line_number')
        results_list = results.to_dict('records')
        
        return {
            "document_id": document_id,
            "filename": results_list[0]["filename"],
            "lines": [
                {
                    "page_number": result["page_number"],
                    "line_number": result["line_number"],
                    "content": result["content"]
                }
                for result in results_list
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of all documents with metadata"""
    try:
        current_table = get_table()
        if current_table is None:
            return []
        
        # Get all data from the table
        try:
            all_data = current_table.to_pandas()
        except Exception:
            # If table exists but is empty or has issues
            return []
        
        if len(all_data) == 0:
            return []
        
        # Check if required columns exist
        required_columns = ['document_id', 'filename', 'upload_date', 'line_number', 'page_number']
        missing_columns = [col for col in required_columns if col not in all_data.columns]
        if missing_columns:
            # Handle case where old data doesn't have upload_date
            if 'upload_date' in missing_columns:
                # Set a default upload date for existing documents
                all_data['upload_date'] = datetime.now()
        
        # Group by document_id to get document-level statistics
        document_groups = all_data.groupby('document_id').agg({
            'filename': 'first',
            'upload_date': 'first',
            'line_number': 'count',  # Count of lines
            'page_number': ['min', 'max']  # First and last page
        }).reset_index()
        
        # Flatten column names
        document_groups.columns = ['document_id', 'filename', 'upload_date', 'lines_count', 'first_page', 'last_page']
        
        # Convert to list of DocumentInfo objects
        documents = []
        for _, row in document_groups.iterrows():
            doc_info = DocumentInfo(
                document_id=row['document_id'],
                filename=row['filename'],
                upload_date=row['upload_date'],
                lines_count=int(row['lines_count']),
                first_page=int(row['first_page']),
                last_page=int(row['last_page'])
            )
            documents.append(doc_info)
        
        # Sort by upload_date (newest first)
        documents.sort(key=lambda x: x.upload_date, reverse=True)
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.delete("/documents")
async def delete_all_documents():
    """Delete all documents from the vector store"""
    global table
    try:
        current_table = get_table()
        if current_table is None:
            return {"message": "No documents to delete", "deleted_count": 0}
        
        # Get count before deletion
        try:
            all_data = current_table.to_pandas()
            total_count = len(all_data)
            unique_docs = all_data['document_id'].nunique() if len(all_data) > 0 else 0
        except Exception:
            total_count = 0
            unique_docs = 0
        
        if total_count == 0:
            return {"message": "No documents to delete", "deleted_count": 0}
        
        # Drop the table and reset
        db = lancedb.connect(DB_PATH)
        try:
            db.drop_table("documents")
            table = None  # Reset global table reference
            return {
                "message": "All documents deleted successfully",
                "deleted_documents": unique_docs,
                "deleted_lines": total_count
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting table: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document by document ID"""
    global table
    try:
        current_table = get_table()
        if current_table is None:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Get all data to check if document exists and count lines
        try:
            all_data = current_table.to_pandas()
        except Exception:
            raise HTTPException(status_code=404, detail="No documents found")
        
        if len(all_data) == 0:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Check if document exists
        document_lines = all_data[all_data['document_id'] == document_id]
        if len(document_lines) == 0:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        
        # Get document info before deletion
        filename = document_lines['filename'].iloc[0]
        lines_count = len(document_lines)
        
        # Delete the document lines
        # LanceDB doesn't have direct delete by condition, so we'll recreate the table without this document
        remaining_data = all_data[all_data['document_id'] != document_id]
        
        if len(remaining_data) == 0:
            # If no documents remain, drop the table
            db = lancedb.connect(DB_PATH)
            try:
                db.drop_table("documents")
                table = None
            except Exception:
                pass
        else:
            # Recreate table with remaining data
            db = lancedb.connect(DB_PATH)
            try:
                db.drop_table("documents")
            except Exception:
                pass
            
            # Convert DataFrame back to list of dicts for LanceDB
            remaining_records = remaining_data.to_dict('records')
            table = db.create_table("documents", remaining_records)
        
        return {
            "message": f"Document deleted successfully",
            "document_id": document_id,
            "filename": filename,
            "deleted_lines": lines_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vector-store"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)