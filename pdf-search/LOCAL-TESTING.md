# Local Testing Guide

This guide helps you test the PDF search system locally (since Claude Code can't reach Pinecone's API).

## Prerequisites

- Python 3.11+ installed
- Git installed
- Your Pinecone API key

## Setup Steps

### 1. Clone and Navigate to Repository

```bash
git clone <your-repo-url>
cd sociology
git checkout claude/improve-learning-platform-jEpxh
cd pdf-search
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate venv
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Pinecone SDK (with gRPC support)
- PDF processing libraries (PyPDF2, pdfplumber)
- Text processing (langchain, tiktoken)
- All utilities

**Note:** This may take a few minutes as it downloads ~2GB of dependencies (including PyTorch for sentence-transformers).

### 4. Configure Environment Variables

Create a `.env` file in the `pdf-search/` directory:

```bash
echo "PINECONE_API_KEY=pcsk_2EcF5t_KvkYVceQ89SMCCheGUeXqYb3nADXtRGJuLY4qcZfbKwGqi8jLsUKBdpyQADDg2b" > .env
```

Or manually create `.env`:
```
PINECONE_API_KEY=pcsk_2EcF5t_KvkYVceQ89SMCCheGUeXqYb3nADXtRGJuLY4qcZfbKwGqi8jLsUKBdpyQADDg2b
PINECONE_ENVIRONMENT=us-east-1
```

### 5. Verify Configuration

```bash
python config.py
```

You should see:
```
=== PDF Search Configuration ===
Config Source: Environment Variables (with .env fallback)

Pinecone API Key: ********************Dg2b
Pinecone Environment: us-east-1
Index Name: sociology-pdfs
...
✓ Configuration is valid
```

## Testing Workflow

### Step 1: Create Pinecone Index

```bash
python scripts/create_index.py
```

Expected output:
```
=== Creating Pinecone Index ===
✓ Pinecone manager initialized
✓ Index 'sociology-pdfs' created successfully
```

This creates a serverless index in `us-east-1` with 1024 dimensions (for llama-text-embed-v2).

### Step 2: Index Your First PDF

```bash
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten
```

What this does:
1. Reads `materials/manifest.json`
2. Downloads PDF from Google Drive (108 pages)
3. Extracts text using pdfplumber
4. Chunks text into ~1000 char pieces with 200 char overlap
5. Uploads chunks to Pinecone with metadata

Expected output:
```
=== Indexing PDF from Manifest ===
Material ID: sozialwissenschaftliches-arbeiten

Processing sozialwissenschaftliches-arbeiten...
  Downloading PDF from Google Drive...
  Extracting text from PDF...
  Chunking text...
  Created 150 chunks
  Uploading to Pinecone...
  100%|████████████████████| 150/150 [00:15<00:00,  9.8chunks/s]

✓ Successfully indexed 150 chunks
```

### Step 3: Test Semantic Search

```bash
# Search in German
python scripts/search_pdfs.py "Wie macht man Literaturrecherche?"

# Search in English
python scripts/search_pdfs.py "How to do literature research?"

# Search with more results
python scripts/search_pdfs.py "Gütekriterien" --top-k 10

# Search with metadata filter
python scripts/search_pdfs.py "Theorien" --filter learning_unit=LE_I
```

Expected output:
```
=== Semantic Search ===
Query: "Wie macht man Literaturrecherche?"
Top 5 results:

[1] Score: 0.89
Document: Sozialwissenschaftliches Arbeiten
Learning Unit: LE_I
Text: Die Literaturrecherche ist ein zentraler Bestandteil...
---

[2] Score: 0.85
...
```

## Additional Commands

### View Index Statistics

```bash
python scripts/manage_index.py stats
```

### List All Documents

```bash
python scripts/manage_index.py list
```

### Delete a Document from Index

```bash
python scripts/manage_index.py delete sozialwissenschaftliches-arbeiten
```

### Reset Index (Delete All Data)

```bash
python scripts/manage_index.py reset --confirm
```

### Index Multiple PDFs

```bash
# Index all PDFs in manifest
python scripts/index_pdfs.py --all

# Reindex (delete old + upload new)
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten --reindex
```

## Troubleshooting

### Issue: "No module named 'pinecone'"

**Solution:** Make sure you activated the venv and ran `pip install -r requirements.txt`

### Issue: "PINECONE_API_KEY is not set"

**Solution:** Create the `.env` file in `pdf-search/` directory (not root)

### Issue: "Failed to download PDF from Google Drive"

**Solution:** Make sure the Google Drive link has public access:
1. Go to Google Drive
2. Right-click the PDF → Share
3. Change to "Anyone with the link can view"

### Issue: Index already exists

**Solution:** Either delete it via Pinecone web UI, or use:
```bash
python scripts/manage_index.py reset --confirm
python scripts/create_index.py
```

## Verifying Everything Works

Run this quick test sequence:

```bash
# 1. Check config
python config.py

# 2. Create index (skip if already exists)
python scripts/create_index.py

# 3. Index PDF
python scripts/index_pdfs.py sozialwissenschaftliches-arbeiten

# 4. Search
python scripts/search_pdfs.py "Literaturrecherche"

# 5. Check stats
python scripts/manage_index.py stats
```

If all commands succeed, your system is fully operational! 🎉

## Next Steps

Once everything works:
1. Add more PDFs to `materials/manifest.json`
2. Index them: `python scripts/index_pdfs.py --all`
3. Use semantic search in your learning sessions
4. Integrate search into your learning chat workflow

## Deactivating Virtual Environment

When done testing:

```bash
deactivate
```
