# PDF Document Search System

A simple microservices-based solution for uploading PDF documents and performing semantic search using LanceDB vector database with a user-friendly Streamlit web interface.

## Architecture

The system consists of three main services:

1. **API Backend** (Port 8000): REST API for client interactions
2. **Vector Store** (Port 8001): LanceDB-based vector storage and search service
3. **Streamlit UI** (Port 8501): Web interface for document upload and search

## Features

- Upload PDF documents and extract text content
- Store document text as vector embeddings using LanceDB
- Semantic search across documents using sentence transformers
- Return matching document IDs, page numbers, and line numbers
- Enhanced search response with timing and similarity scores
- User-friendly web interface for all operations
- RESTful API with FastAPI
- Docker containerization for easy deployment

## Project Structure

```
p3-search/
├── api-backend/
│   ├── main.py                 # API backend service
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Docker configuration
├── vector-store/
│   ├── main.py                 # Vector store service with LanceDB
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Docker configuration
├── streamlit-ui/
│   ├── app.py                  # Streamlit web interface
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Docker configuration
├── docker-compose.yml          # Multi-service deployment
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd p3-search
   ```

2. **Start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the applications**:
   - **Streamlit Web UI**: http://localhost:8501 (Primary interface)
   - **API Backend**: http://localhost:8000 (API documentation)
   - **Vector Store**: http://localhost:8001 (Direct vector operations)

## Using the Web Interface

### Upload PDFs
1. Go to http://localhost:8501
2. Select "📄 Upload PDFs" from the sidebar
3. Choose one or more PDF files
4. Click "🚀 Upload Documents"
5. View upload results and document processing status

### Search Documents
1. Select "🔍 Search Documents" from the sidebar
2. Enter your search query (e.g., "machine learning", "project management")
3. Adjust advanced options if needed:
   - Maximum results (1-20)
   - Minimum similarity threshold (0.0-1.0)
4. Click "🔍 Search" to find relevant content
5. Export results as CSV if needed

### Document Library
1. Select "📚 Document Library" from the sidebar
2. View system status and health checks
3. Get tips for exploring your document collection

### Manual Setup

#### Prerequisites
- Python 3.11+
- pip

#### Streamlit UI Service

1. **Navigate to streamlit-ui directory**:
   ```bash
   cd streamlit-ui
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variable for local development**:
   ```bash
   export API_BASE_URL=http://localhost:8000
   export ENVIRONMENT=local
   ```

4. **Run the service**:
   ```bash
   streamlit run app.py --server.port 8501
   ```

#### Vector Store Service

1. **Navigate to vector-store directory**:
   ```bash
   cd vector-store
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

#### API Backend Service

1. **Open a new terminal and navigate to api-backend**:
   ```bash
   cd api-backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variable**:
   ```bash
   export VECTOR_STORE_URL=http://localhost:8001
   ```

4. **Run the service**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Documentation

### Upload PDF Document

**Endpoint**: `POST /upload-pdf`

Upload a PDF document for indexing and vector storage.

```bash
curl -X POST \
  http://localhost:8000/upload-pdf \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf"
```

**Response**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "your-document.pdf",
  "lines_processed": 245,
  "message": "PDF uploaded and processed successfully"
}
```

### Search Documents

**Endpoint**: `POST /search-doc`

Search for documents using semantic similarity.

```bash
curl -X POST \
  http://localhost:8000/search-doc \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "limit": 5
  }'
```

**Response**:
```json
{
  "query": "machine learning algorithms",
  "response_time_ms": 42.5,
  "number_of_results": 3,
  "results": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "ml-research.pdf",
      "page_number": 5,
      "line_number": 42,
      "text_fragment": "Machine learning algorithms are powerful tools for data analysis and pattern recognition...",
      "similarity_score": 0.857
    },
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "ml-research.pdf", 
      "page_number": 12,
      "line_number": 156,
      "text_fragment": "Deep learning algorithms, a subset of machine learning, have shown remarkable results...",
      "similarity_score": 0.823
    }
  ]
}
```

### Get Document by ID

**Endpoint**: `GET /documents/{document_id}`

Retrieve all lines for a specific document.

```bash
curl -X GET http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

### Health Check

**Endpoint**: `GET /health`

Check service health and connectivity.

```bash
curl -X GET http://localhost:8000/health
```

## Usage Examples

### Python Example

```python
import requests

# Upload a PDF
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-pdf',
        files={'file': f}
    )
    result = response.json()
    document_id = result['document_id']

# Search documents
search_response = requests.post(
    'http://localhost:8000/search-doc',
    json={
        'query': 'machine learning algorithms',
        'limit': 10,
        'min_similarity': 0.5
    }
)
result = search_response.json()

print(f"Found {result['number_of_results']} results in {result['response_time_ms']:.1f}ms")
for match in result['results']:
    print(f"Document: {match['filename']} (Page {match['page_number']}, Line {match['line_number']})")
    print(f"Text: {match['text_fragment']}")
    print(f"Similarity: {match['similarity_score']:.3f}")
    print("---")
```

### JavaScript Example

```javascript
// Upload PDF
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/upload-pdf', {
    method: 'POST',
    body: formData
});
const uploadResult = await uploadResponse.json();

// Search documents
const searchResponse = await fetch('http://localhost:8000/search-doc', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'machine learning',
        limit: 10,
        min_similarity: 0.5
    })
});
const result = await searchResponse.json();

console.log(`Found ${result.number_of_results} results in ${result.response_time_ms}ms`);
result.results.forEach(match => {
    console.log(`${match.filename} (Page ${match.page_number}, Line ${match.line_number})`);
    console.log(`Text: ${match.text_fragment}`);
    console.log(`Similarity: ${match.similarity_score}`);
});
```

## Technical Details

### Vector Storage
- **Database**: LanceDB (serverless vector database)
- **Embeddings**: sentence-transformers ('all-MiniLM-L6-v2' model)
- **Search**: Cosine similarity with configurable result limits

### PDF Processing
- **Library**: PyPDF2 for text extraction
- **Processing**: Line-by-line text extraction and embedding generation
- **Filtering**: Meaningful lines (>10 characters) are indexed

### Service Communication
- **Protocol**: HTTP REST API
- **Client**: httpx for async HTTP communication
- **Timeout**: Configurable timeouts for reliability

## Development

### Running Tests

All test files and testing utilities are organized in the `tests/` directory.

**One Command Testing (Recommended):**
```bash
cd tests
python test.py
```

That's it! This single command will:
- Install any missing dependencies automatically
- Run all test suites sequentially  
- Provide a comprehensive summary
- Save detailed results to JSON

**Individual Test Suites:**
```bash
cd tests

# Run specific tests
python test_quick.py      # Quick comprehensive test
python test_simple.py     # Basic validation test  
python test_advanced.py   # Performance and metrics test
```

For detailed testing information, see `tests/README.md`.

### Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

### Monitoring

Both services provide health check endpoints:
- API Backend: `GET /health`
- Vector Store: `GET /health`

## Troubleshooting

### Common Issues

1. **Service connection errors**:
   - Ensure both services are running
   - Check port availability (8000, 8001)
   - Verify VECTOR_STORE_URL environment variable

2. **PDF processing errors**:
   - Ensure PDF files are not corrupted
   - Check file size limits
   - Verify PDF contains extractable text

3. **Search not returning results**:
   - Ensure documents are uploaded first
   - Try different search terms
   - Check similarity thresholds

### Logs

View service logs:
```bash
# Docker Compose
docker-compose logs api-backend
docker-compose logs vector-store

# Manual setup
# Check terminal outputs where services are running
```

## License

This project is open source and available under the MIT License.