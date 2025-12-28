# Testing the Learning Data System

This guide helps you test the learning data system in your learning chat.

## Quick Test Setup

### 1. Create Example Topics

```bash
cd learning-data/scripts

# Create a few example topics
python create_topic.py "Socialization Theory" "Primary and secondary socialization, agents of socialization" "materials/sociology/textbook.pdf" "socialization,theory"

python create_topic.py "Social Structure" "Macro-level organization, institutions, social systems" "materials/sociology/textbook.pdf" "structure,macro"

python create_topic.py "Functionalism" "Functionalist perspective, Durkheim, social solidarity" "materials/sociology/textbook.pdf" "theory,functionalism"

python create_topic.py "Conflict Theory" "Marx, class conflict, power dynamics" "materials/sociology/textbook.pdf" "theory,conflict"
```

Expected output: Creates `topic-001.json` through `topic-004.json`

### 2. Verify Topics Created

```bash
python view_progress.py
```

Expected output:
```
=== Overall Learning Progress ===

Topics by Mastery Level:
  New:       4 (100%)
  Learning:  0 (0%)
  Reviewing: 0 (0%)
  Mastered:  0 (0%)
  Total:     4
```

### 3. Check What to Practice

```bash
python what_to_practice.py
```

Expected output: All 4 topics should be listed (all are new and due for first practice)

### 4. Create a Test Session

Create a file `/tmp/test-session.json`:

```json
{
  "session_id": "session-2025-12-28-1",
  "date": "2025-12-28",
  "topics_practiced": [
    {
      "topic_id": "topic-001",
      "questions_asked": 5,
      "correct_answers": 4,
      "questions": [
        {
          "question": "What is primary socialization?",
          "user_answer": "Socialization during childhood from family",
          "correct": true,
          "notes": "Good understanding"
        },
        {
          "question": "Name three agents of socialization",
          "user_answer": "Family, school, peers",
          "correct": true,
          "notes": "Correct"
        },
        {
          "question": "What is secondary socialization?",
          "user_answer": "Learning in later life stages",
          "correct": true,
          "notes": "Good"
        },
        {
          "question": "Who coined the term 'looking-glass self'?",
          "user_answer": "Charles Cooley",
          "correct": true,
          "notes": "Correct"
        },
        {
          "question": "What is anticipatory socialization?",
          "user_answer": "Not sure",
          "correct": false,
          "notes": "Need to review this concept"
        }
      ]
    },
    {
      "topic_id": "topic-003",
      "questions_asked": 3,
      "correct_answers": 2,
      "questions": [
        {
          "question": "What is the functionalist perspective?",
          "user_answer": "Society as interconnected parts working together",
          "correct": true,
          "notes": "Good grasp"
        },
        {
          "question": "Who is the father of functionalism?",
          "user_answer": "Emile Durkheim",
          "correct": true,
          "notes": "Correct"
        },
        {
          "question": "What are latent functions?",
          "user_answer": "Obvious functions",
          "correct": false,
          "notes": "Confused with manifest functions"
        }
      ]
    }
  ],
  "overall_score": 0.75,
  "session_notes": "Good progress on socialization. Functionalism needs more review on latent vs manifest functions.",
  "chat_context_summary": "Student showed strong understanding of basic concepts but struggled with more nuanced terminology."
}
```

Record the session:

```bash
python record_quiz.py --json /tmp/test-session.json
```

Expected output:
```
✓ Session recorded from JSON: session-2025-12-28-1
```

### 5. Verify Results Were Recorded

```bash
# Check topic details
python view_progress.py --topic topic-001

# Check overall progress
python view_progress.py

# Check what to practice next
python what_to_practice.py
```

Expected changes:
- `topic-001`: Should show 1 attempt, 80% score, mastery level "reviewing", next review in ~4 days
- `topic-003`: Should show 1 attempt, 67% score, mastery level "learning", next review tomorrow
- `topic-002` and `topic-004`: Still "new", available for practice
- Global progress: 1 session completed, 8 total questions, 75% overall accuracy

### 6. Test Interactive Mode (Optional)

```bash
python record_quiz.py --interactive
```

Follow the prompts to add another session.

## Testing in Learning Chat

### Test 1: Basic Query

**In your learning chat, say:**
```
Can you check what topics I should practice today?
```

**Expected LLM behavior:**
1. Runs `cd learning-data/scripts && python what_to_practice.py`
2. Reads the output
3. Tells you which topics are due
4. Suggests starting with highest priority topics

### Test 2: Quiz Session

**In your learning chat, say:**
```
Let's practice topic-001 (Socialization Theory)
```

**Expected LLM behavior:**
1. Asks quiz questions about socialization
2. Tracks your answers
3. At end of quiz, creates session JSON
4. Runs `python record_quiz.py --json` to save results
5. Shows you your score and next review date

### Test 3: Progress Check

**In your learning chat, say:**
```
Show me my overall learning progress
```

**Expected LLM behavior:**
1. Runs `python view_progress.py`
2. Summarizes your mastery distribution
3. Highlights topics needing attention
4. Provides encouraging feedback

### Test 4: Viewing Topic Details

**In your learning chat, say:**
```
How am I doing on Socialization Theory?
```

**Expected LLM behavior:**
1. Identifies topic ID (topic-001)
2. Runs `python view_progress.py --topic topic-001`
3. Shows attempt history, trend, and recommendations

## Advanced Tests

### Test Spaced Repetition

1. Record multiple sessions over several days
2. Mark some topics as failed (< 60%)
3. Check that failed topics come up sooner
4. Verify successful topics have increasing intervals

### Test Mastery Progression

1. Practice a topic 3 times with >90% each time
2. Check mastery level changes: new → learning → reviewing → mastered
3. Verify mastered topics have longer review intervals

### Test JSON Output

```bash
# Get structured data for LLM parsing
python what_to_practice.py --json
python view_progress.py --json
python view_progress.py --topic topic-001 --json
```

LLM should be able to parse and use this data programmatically.

## Common Issues & Solutions

### "Module not found: learning_data"

**Solution:** Make sure you're in the `learning-data/scripts` directory:
```bash
cd learning-data/scripts
```

### "No topics due for review"

**Solution:** Either:
- Create new topics (they're immediately available)
- Check next review dates - some might not be due yet
- Force practice a topic even if not due

### "Invalid JSON"

**Solution:** Validate your JSON file:
```bash
python -m json.tool test-session.json
```

### Scripts not executable

**Solution:** Make them executable:
```bash
chmod +x *.py
```

## Expected Behavior Summary

| Action | System Response |
|--------|----------------|
| Create topic | New topic file, available for practice immediately |
| 80%+ quiz score | Interval increases (×2.5), mastery may increase |
| <60% quiz score | Interval resets to 1 day, mastery stays/decreases |
| Practice 3× at 90%+ | Topic marked as "mastered" |
| Query what to practice | Returns overdue → new → due today |
| View progress | Shows mastery distribution, accuracy, trends |

## Cleanup (if needed)

To reset and start fresh:

```bash
# Backup first
cp -r learning-data learning-data-backup

# Clear data
rm learning-data/topics/*.json
rm learning-data/quiz-sessions/*.json

# Reset progress
cat > learning-data/progress/global-progress.json << 'EOF'
{
  "last_updated": "2025-12-28T00:00:00Z",
  "total_topics": 0,
  "topics_by_mastery": {
    "new": 0,
    "learning": 0,
    "reviewing": 0,
    "mastered": 0
  },
  "total_sessions": 0,
  "total_questions_answered": 0,
  "overall_accuracy": 0,
  "study_streak_days": 0,
  "last_study_date": null
}
EOF
```

---

**Ready to test!** Start with the Quick Test Setup, then try the tests in your learning chat.
