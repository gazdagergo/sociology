# PDF Semantic Search with Pinecone

Semantic search system for PDF learning materials using Pinecone vector database with integrated embeddings.

## 🎯 Features

- ✅ **Semantic Search**: Find content by meaning, not just keywords
- ✅ **Cloud Integration**: Works with PDFs stored in Google Drive
- ✅ **Automatic Chunking**: Intelligently splits PDFs into searchable segments
- ✅ **Metadata Filtering**: Filter by document, learning unit, or type
- ✅ **Manifest Integration**: Seamlessly works with existing materials/manifest.json
- ✅ **Production Ready**: Error handling, logging, progress bars
- ✅ **Easy to Use**: Simple CLI scripts for all operations

## 📋 Prerequisites

1. **Pinecone Account**: Sign up at [pinecone.io](https://www.pinecone.io/)
2. **API Key**: Get your API key from Pinecone console
3. **Python 3.8+**: Ensure you have Python installed

## 🚀 Quick Start

### 1. Installation

```bash
cd pdf-search

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required settings in `.env`:**
```bash
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=us-east-1  # or your region
PINECONE_INDEX_NAME=sociology-pdfs
```

### 3. Create Index

```bash
python scripts/create_index.py
```

**Output:**
```
=== Creating Pinecone Index ===

Pinecone API Key: ********************xyz
Pinecone Environment: us-east-1
Index Name: sociology-pdfs
...

✓ Index created successfully!
```

### 4. Index Your PDFs

```bash
# Index all PDFs from manifest
python scripts/index_pdfs.py --all

# Or index a specific PDF
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten
```

**What happens:**
1. Downloads PDF from Google Drive
2. Extracts text using pdfplumber or PyPDF2
3. Chunks text into ~1000 character segments
4. Generates embeddings (server-side via Pinecone)
5. Indexes chunks with metadata

### 5. Search!

```bash
# Basic search
python scripts/search_pdfs.py "Wie macht man Literaturrecherche?"

# Advanced search
python scripts/search_pdfs.py "research methods" --top-k 10 --threshold 0.75

# Filter by document
python scripts/search_pdfs.py "socialization" --filter document_id=sozialwissenschaftliches-arbeiten
```

## 📚 Usage Guide

### Indexing PDFs

**Index all materials:**
```bash
python scripts/index_pdfs.py --all
```

**Index specific material:**
```bash
python scripts/index_pdfs.py <material-id>
```

**Reindex (delete + reindex):**
```bash
python scripts/index_pdfs.py <material-id> --reindex
```

**Examples:**
```bash
# Index the first PDF
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten

# Reindex after PDF update
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten --reindex

# Index all PDFs in manifest
python scripts/index_pdfs.py --all
```

### Searching PDFs

**Basic search:**
```bash
python scripts/search_pdfs.py "your query here"
```

**Search options:**
```bash
--top-k N         # Return top N results (default: 5)
--threshold X     # Min similarity score 0-1 (default: 0.7)
--filter key=val  # Filter by metadata
--json            # Output as JSON
```

**Examples:**
```bash
# Find content about literature research
python scripts/search_pdfs.py "Literaturrecherche"

# Get top 10 results
python scripts/search_pdfs.py "scientific writing" --top-k 10

# Filter by learning unit
python scripts/search_pdfs.py "methodology" --filter learning_unit=LE_I

# Lower threshold for more results
python scripts/search_pdfs.py "thesis" --threshold 0.6

# JSON output for programmatic use
python scripts/search_pdfs.py "research" --json
```

### Managing Index

**View statistics:**
```bash
python scripts/manage_index.py stats
```

**List indexed documents:**
```bash
python scripts/manage_index.py list
```

**Delete a document:**
```bash
python scripts/manage_index.py delete <document-id>
```

**Reset index (delete all data):**
```bash
python scripts/manage_index.py reset --confirm
```

## 🏗️ Architecture

### Directory Structure

```
pdf-search/
├── config.py              # Configuration management
├── pinecone_manager.py    # Pinecone operations
├── pdf_processor.py       # PDF extraction & chunking
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (gitignored)
├── scripts/
│   ├── create_index.py    # Create Pinecone index
│   ├── index_pdfs.py      # Index PDFs from manifest
│   ├── search_pdfs.py     # Search the index
│   └── manage_index.py    # Index management
└── README.md              # This file
```

### Data Flow

```
1. PDF in Google Drive
   ↓
2. manifest.json (metadata + links)
   ↓
3. pdf_processor.py (download, extract, chunk)
   ↓
4. Pinecone (embed + index server-side)
   ↓
5. Search via pinecone_manager.py
   ↓
6. Results with scores + metadata
```

### Chunk Structure

Each PDF is split into chunks with this structure:

```python
{
  'id': 'sozialwissenschaftliches-arbeiten#chunk_42',
  'text': 'Full chunk text for embedding...',
  'metadata': {
    'document_id': 'sozialwissenschaftliches-arbeiten',
    'document_title': 'Sozialwissenschaftliches Arbeiten',
    'chunk_number': 42,
    'total_chunks': 108,
    'chunk_text': 'Preview of chunk text...',
    'document_url': 'https://drive.google.com/...',
    'learning_unit': 'LE_I',
    'course': 'Kurs 25501 B1',
    'material_type': 'textbook',
    'total_pages': 108,
    'created_at': '2025-12-29T...',
    'document_type': 'pdf'
  }
}
```

## 🔧 Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | **Required** |
| `PINECONE_ENVIRONMENT` | Pinecone region | us-east-1 |
| `PINECONE_INDEX_NAME` | Index name | sociology-pdfs |
| `PINECONE_NAMESPACE` | Namespace for organization | default |
| `EMBEDDING_MODEL` | Embedding model | llama-text-embed-v2 |
| `EMBEDDING_DIMENSION` | Vector dimension | 1024 |
| `CHUNK_SIZE` | Characters per chunk | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `DEFAULT_TOP_K` | Search result count | 5 |
| `SIMILARITY_THRESHOLD` | Min similarity score | 0.7 |

### Customizing Chunking

Edit `config.py` or `.env`:

```bash
# Smaller chunks (more granular search)
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Larger chunks (more context)
CHUNK_SIZE=2000
CHUNK_OVERLAP=400
```

**Tradeoffs:**
- **Small chunks**: More precise results, but less context
- **Large chunks**: More context, but may be less focused
- **Overlap**: Prevents splitting across important boundaries

## 🔌 Programmatic Usage

### Using in Python Code

```python
from pinecone_manager import PineconeManager
from pdf_processor import PDFProcessor

# Initialize
manager = PineconeManager()
processor = PDFProcessor()

# Index a PDF
chunks = processor.process_pdf_from_manifest('sozialwissenschaftliches-arbeiten')
stats = manager.upsert_chunks(chunks)

# Search
results = manager.search(
    query="Wie schreibt man eine Hausarbeit?",
    top_k=5,
    filter_metadata={'learning_unit': 'LE_I'}
)

# Print results
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.4f}")
    print(f"   {result['metadata']['document_title']}")
    print(f"   {result['metadata']['chunk_text'][:200]}...")
```

### Integration with Learning Chat

The LLM can use the search functionality during study sessions:

```python
# In learning chat context:
# 1. User asks: "What does the textbook say about literature research?"

# 2. LLM runs search:
results = manager.search(
    query="Literaturrecherche methods and best practices",
    top_k=3
)

# 3. LLM synthesizes answer from top results:
# "According to Chapter 4 of Sozialwissenschaftliches Arbeiten:
#  - Use systematic database searches...
#  - Apply the snowball method...
#  - Document sources properly..."
```

## 🧪 Testing

### Test Configuration

```bash
python config.py
```

**Expected output:**
```
=== PDF Search Configuration ===
Pinecone API Key: ********************xyz
...
✓ Configuration is valid
```

### Test Pinecone Connection

```bash
python pinecone_manager.py
```

**Expected output:**
```
✓ Pinecone manager initialized
✓ Connected to index 'sociology-pdfs'
  Total vectors: 245
  Dimension: 1024
```

### Test PDF Processing

```bash
python pdf_processor.py
```

**Expected output:**
```
PDF Processor initialized
Chunk size: 1000 characters
...
Found 1 material(s) in manifest:
  - sozialwissenschaftliches-arbeiten: Sozialwissenschaftliches Arbeiten
```

## 🐛 Troubleshooting

### "Pinecone API key is required"

**Solution:** Set `PINECONE_API_KEY` in `.env` file

```bash
echo "PINECONE_API_KEY=your_key_here" >> .env
```

### "Index does not exist"

**Solution:** Create the index first

```bash
python scripts/create_index.py
```

### "Failed to download PDF"

**Causes:**
1. Google Drive link not publicly accessible
2. Invalid file ID in manifest

**Solution:**
- Check PDF is set to "Anyone with link can view"
- Verify `raw_url` in manifest.json is correct

### "No text extracted from PDF"

**Causes:**
1. PDF is scanned images (no selectable text)
2. PDF is encrypted/protected

**Solution:**
- Use OCR to extract text from scanned PDFs
- Remove PDF protection
- Check PDF manually to confirm it has selectable text

### Search returns no results

**Causes:**
1. Threshold too high
2. Query doesn't match document content
3. Index is empty

**Solutions:**
```bash
# Lower threshold
python scripts/search_pdfs.py "query" --threshold 0.5

# Increase top-k
python scripts/search_pdfs.py "query" --top-k 20

# Check index stats
python scripts/manage_index.py stats

# Verify documents are indexed
python scripts/manage_index.py list
```

## 📊 Best Practices

### Indexing Strategy

1. **Index incrementally**: Index new PDFs as you add them
2. **Reindex on updates**: Use `--reindex` if PDF content changes
3. **Batch process**: Use `--all` for initial bulk indexing
4. **Monitor stats**: Check index stats regularly

### Search Strategy

1. **Start broad**: Use general terms first
2. **Refine with filters**: Add metadata filters to narrow results
3. **Adjust threshold**: Lower for more results, raise for higher quality
4. **Use top-k wisely**: Start with 5-10, increase if needed

### Maintenance

1. **Regular backups**: Export your manifest.json
2. **Monitor costs**: Track Pinecone usage
3. **Clean up**: Delete unused document chunks
4. **Update embeddings**: Reindex if switching embedding models

## 🚀 Advanced Features

### Hybrid Search (Future Enhancement)

Combine semantic + keyword search for better results.

### Reranking (Future Enhancement)

Use BGE or similar reranker to improve result relevance.

### Multi-namespace Organization

Organize by learning unit:

```bash
# Set namespace in .env
PINECONE_NAMESPACE=LE_I

# Or pass dynamically
manager = PineconeManager(namespace="LE_II")
```

### Custom Metadata Filters

```bash
# Complex filters
python scripts/search_pdfs.py "query" \
  --filter learning_unit=LE_I \
  --filter material_type=textbook
```

## 📝 Adding New PDFs

When you add a new PDF to your learning platform:

1. **Upload to Google Drive** (already done via materials workflow)
2. **Add to manifest.json** (already done via materials workflow)
3. **Index the PDF:**
   ```bash
   python pdf-search/scripts/index_pdfs.py <material-id>
   ```
4. **Verify indexing:**
   ```bash
   python pdf-search/scripts/manage_index.py stats
   ```

That's it! The PDF is now searchable.

## 💡 Use Cases

### Study Sessions

```bash
# Find information for essay
python scripts/search_pdfs.py "Hausarbeit schreiben Tipps"

# Research a specific topic
python scripts/search_pdfs.py "Literaturrecherche Datenbanken"

# Find methodology info
python scripts/search_pdfs.py "qualitative vs quantitative methods"
```

### Exam Preparation

```bash
# Find all mentions of a concept
python scripts/search_pdfs.py "Gütekriterien" --top-k 20

# Review specific chapter content
python scripts/search_pdfs.py "Forschungsprozess" \
  --filter document_id=sozialwissenschaftliches-arbeiten
```

### LLM Integration

The search system can be used by your learning chat LLM:

```
User: "I need to write a Hausarbeit. What does the textbook say?"

LLM:
1. Searches: "Hausarbeit schreiben structure guidelines"
2. Gets top 5 relevant chunks
3. Synthesizes answer from results
4. Provides page references and quotes
```

## 🔒 Security & Privacy

- ✅ API keys stored in `.env` (gitignored)
- ✅ PDFs remain in your Google Drive
- ✅ Only metadata stored in git
- ✅ Pinecone data stays in your account
- ⚠️ Ensure Google Drive PDFs are not publicly indexed

## 📦 Dependencies

See `requirements.txt` for full list. Key libraries:

- **pinecone-client**: Vector database SDK
- **PyPDF2 / pdfplumber**: PDF text extraction
- **langchain**: Text splitting and chunking
- **requests**: HTTP client for downloading PDFs
- **python-dotenv**: Environment configuration

## 🤝 Contributing

This is a personal learning platform, but improvements are welcome:

1. Test thoroughly before committing
2. Update documentation
3. Follow existing code style
4. Add error handling

## 📄 License

Personal use for sociology studies.

## 🆘 Support

For issues:
1. Check troubleshooting section
2. Verify configuration with test scripts
3. Check Pinecone console for quota/limits
4. Review error messages carefully

---

**Happy searching! 🔍📚**
