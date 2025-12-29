# Cloud Storage for Learning Materials

## 🎯 Purpose

**PDFs are too large for git** (2MB+ files bloat the repository).
**Solution:** Store PDFs in **Google Drive**, track links in **manifest.json**.

This allows:
- ✅ Access from anywhere (web, mobile, desktop)
- ✅ No repository bloat
- ✅ Fast git operations
- ✅ LLM can fetch content when needed

---

## 📤 How to Add a PDF

### Step 1: Upload to Google Drive

1. Go to [Google Drive](https://drive.google.com)
2. Create a folder: `Sociology Materials` (or use existing)
3. Upload your PDF file
4. Right-click the file → **Share**
5. Click **"Anyone with the link"** → **Viewer**
6. Copy the shareable link

**Example link:**
```
https://drive.google.com/file/d/1a2B3c4D5e6F7g8H9i0J/view?usp=sharing
```

### Step 2: Extract the File ID

From the link above, the **File ID** is: `1a2B3c4D5e6F7g8H9i0J`

It's the part between `/d/` and `/view`

### Step 3: Create Raw Download URL

Replace the File ID in this template:
```
https://drive.google.com/uc?export=download&id=FILE_ID_HERE
```

**Example:**
```
https://drive.google.com/uc?export=download&id=1a2B3c4D5e6F7g8H9i0J
```

### Step 4: Share Both Links

Provide both:
- **View link** (for humans to click)
- **Raw link** (for LLM to fetch content)
- **File details** (title, pages, chapters)

---

## 📋 Adding to Manifest

After uploading, add entry to `materials/manifest.json`:

```json
{
  "id": "unique-identifier",
  "title": "Book Title or Description",
  "filename": "original-filename.pdf",
  "url": "https://drive.google.com/file/d/FILE_ID/view?usp=sharing",
  "raw_url": "https://drive.google.com/uc?export=download&id=FILE_ID",
  "type": "textbook|article|paper|lecture",
  "pages": 450,
  "sections": [
    {
      "chapter": 1,
      "title": "Chapter Title",
      "pages": "1-25"
    }
  ],
  "learning_unit": "LE_I|LE_II|LE_III|LE_IV",
  "uploaded": "2025-12-29",
  "notes": "Any additional context"
}
```

**Material Types:**
- `textbook` - Course textbooks and study letters
- `article` - Academic articles and papers
- `lecture` - Lecture slides or transcripts
- `exercise` - Exercise materials and solutions
- `supplementary` - Additional reference materials

---

## 🤖 How LLM Uses This

### 1. List Available Materials

LLM reads `manifest.json` to see all available PDFs:

```javascript
"You have 5 materials available:
 1. Introduction to Sociology (Textbook, 450 pages)
 2. Durkheim - Suicide Study (Article, 45 pages)
 3. Lecture 3 - What is Sociology? (Lecture, 30 pages)
 ..."
```

### 2. Access PDF Content

When needed, LLM uses `WebFetch` to read specific pages:

```javascript
WebFetch(
  url: "raw_url from manifest",
  prompt: "Summarize Chapter 3, pages 61-95 about socialization"
)
```

### 3. Create Topics with References

When creating learning topics, LLM references material IDs:

```json
{
  "topic_id": "topic-001",
  "title": "Socialization Theory",
  "source_material": "intro-sociology-textbook",
  "source_reference": "Chapter 3, pages 61-95"
}
```

### 4. Generate Quizzes from Content

LLM can fetch relevant sections to generate quiz questions:

```javascript
// Fetch pages 61-95
// Generate 5 quiz questions
// Ask user
// Record results in learning-data/
```

---

## 🔍 Finding Material Information

**To find a specific material:**
```bash
# Read manifest
cat materials/manifest.json | grep "intro-sociology"
```

**To list all materials:**
```bash
# Use jq if available
cat materials/manifest.json | jq '.materials[] | {id, title}'

# Or just read the file
cat materials/manifest.json
```

---

## 📚 Example Manifest Entry

```json
{
  "version": "1.0",
  "last_updated": "2025-12-29",
  "materials": [
    {
      "id": "studienbrief-le1-kapitel1-3",
      "title": "Studienbrief LE I - Kapitel 1-3: Politikwissenschaft",
      "filename": "LE1_Kapitel_1-3_Politikwissenschaft.pdf",
      "url": "https://drive.google.com/file/d/ABC123/view?usp=sharing",
      "raw_url": "https://drive.google.com/uc?export=download&id=ABC123",
      "type": "textbook",
      "pages": 120,
      "sections": [
        {
          "chapter": 1,
          "title": "Was ist Politikwissenschaft?",
          "pages": "1-40"
        },
        {
          "chapter": 2,
          "title": "Theorien der Politikwissenschaft",
          "pages": "41-80"
        },
        {
          "chapter": 3,
          "title": "Methoden der Politikwissenschaft",
          "pages": "81-120"
        }
      ],
      "learning_unit": "LE_I",
      "uploaded": "2025-12-29",
      "notes": "Main textbook for Learning Unit I, covers political science fundamentals"
    }
  ]
}
```

---

## 🔧 Troubleshooting

### "LLM can't access the PDF"

**Issue:** Google Drive link not publicly accessible
**Solution:**
1. Right-click PDF in Drive
2. Share → Change to "Anyone with the link"
3. Make sure it says "Viewer" (not "Restricted")

### "WebFetch returns error"

**Issue:** Using view URL instead of raw URL
**Solution:** Use the `raw_url` format:
```
https://drive.google.com/uc?export=download&id=FILE_ID
```

### "PDF too large to fetch"

**Issue:** Very large PDFs (>10MB) may be slow
**Solution:**
- Break into smaller files (chapters)
- Or provide chapter-level links
- LLM will fetch only needed sections

---

## 📊 Benefits of This System

| Aspect | Benefit |
|--------|---------|
| **Repository size** | Stays small (only JSON, no PDFs) |
| **Access** | Works from web, mobile, anywhere |
| **Collaboration** | Easy to share links with study partners |
| **Updates** | Replace PDF in Drive, link stays same |
| **LLM integration** | Can fetch content on-demand |
| **Version control** | Only manifest changes are tracked |

---

## 🚀 Quick Start

**First PDF upload:**

1. Upload to Google Drive
2. Get shareable link
3. Share both links here in the tech chat
4. I'll add to manifest
5. Commit manifest to git

**Every subsequent PDF:**
- Same process
- Or you can edit manifest.json directly
- Just follow the structure above

---

## 📝 Notes

- **Privacy:** Only use "Anyone with link" for non-sensitive materials
- **Ownership:** Keep PDFs in your personal Drive for full control
- **Backup:** Google Drive is reliable, but keep local backups too
- **Quota:** Free Google Drive: 15GB (plenty for PDFs)

---

**Ready to add your first PDF!** Upload it to Google Drive and share the link here.
