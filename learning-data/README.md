# Learning Data System

**For LLM Reading: This directory contains a persistent learning data system that tracks quiz performance, manages spaced repetition, and maintains learning progress across sessions.**

## 🎯 Purpose

This system provides:
- **Persistent quiz tracking** - Every quiz attempt is recorded and saved
- **Spaced repetition** - Intelligent scheduling of topic reviews
- **Progress monitoring** - Track mastery levels and learning trends
- **Context continuity** - Learning state persists between chat sessions

**Key Benefit:** The LLM doesn't need to rely on chat context to track learning progress. All data is stored in structured JSON files that can be queried and updated programmatically.

## 📁 Directory Structure

```
learning-data/
├── topics/              # Individual topic records (topic-001.json, etc.)
├── quiz-sessions/       # Session records (session-2025-12-28-1.json, etc.)
├── progress/            # Global progress and configuration
│   ├── global-progress.json
│   └── srs-config.json
├── scripts/             # Python tools for managing data
│   ├── learning_data.py     # Core library
│   ├── create_topic.py      # Create new topics
│   ├── record_quiz.py       # Record quiz results
│   ├── what_to_practice.py  # Query what to study
│   └── view_progress.py     # View progress stats
├── SCHEMAS.md           # Detailed schema documentation
└── README.md            # This file
```

## 🤖 LLM Usage Guide

### Workflow for Learning Sessions

#### 1. **Start of Session: Query What to Practice**

```bash
cd learning-data/scripts
python what_to_practice.py --json
```

**What this does:**
- Returns topics due for review today based on spaced repetition
- Prioritizes overdue topics and those marked as "needs_review"
- Provides topic IDs, titles, and source materials

**LLM Action:** Use the returned topics to guide the quiz session. Focus on topics listed in the output.

#### 2. **During Session: Ask Quiz Questions**

- Read the topic's source material if needed
- Generate quiz questions based on the topic
- Track user's answers (correct/incorrect)
- Keep running tally of performance

**Important:** Store quiz results temporarily in memory during the session. You'll record them at the end.

#### 3. **End of Session: Record Results**

**Method A: Interactive (if user prefers step-by-step)**
```bash
cd learning-data/scripts
python record_quiz.py --interactive
```

**Method B: JSON (recommended for LLM)**

Create a session JSON file:
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
          "user_answer": "Learning in childhood from family",
          "correct": true,
          "notes": "Good understanding"
        }
      ]
    }
  ],
  "overall_score": 0.8,
  "session_notes": "Strong grasp of socialization concepts, needs review on secondary agents"
}
```

Then record it:
```bash
python record_quiz.py --json session-data.json
```

**What this does:**
- Updates topic records with new attempt data
- Calculates next review dates using spaced repetition
- Updates mastery levels
- Creates permanent session record
- Updates global progress statistics

#### 4. **Viewing Progress**

```bash
# Overall progress
python view_progress.py

# Specific topic
python view_progress.py --topic topic-001

# JSON output for parsing
python view_progress.py --json
```

### Creating New Topics

When you encounter a new concept/topic to track:

```bash
cd learning-data/scripts
python create_topic.py "Topic Title" "Description" "source/path.pdf" "tag1,tag2"
```

Example:
```bash
python create_topic.py "Socialization Theories" "Primary and secondary socialization processes" "materials/sociology/textbook-ch3.pdf" "socialization,theory"
```

**Returns:** A new topic ID (e.g., `topic-001`) that you can use in quiz sessions.

## 🔄 Spaced Repetition Algorithm

The system uses a simplified SM2 algorithm:

1. **Initial interval:** 1 day
2. **On success (≥80%):** Multiply interval by 2.5
3. **On failure (<80%):** Reset to 1 day
4. **Max interval:** 180 days

**Mastery Levels:**
- `new` - Never practiced
- `learning` - Active learning phase (< 80% average)
- `reviewing` - Periodic review phase (≥ 80% average)
- `mastered` - Consistently correct (≥ 90% across 3+ sessions)

## 📊 Key Data Structures

### Topic Record
```json
{
  "topic_id": "topic-001",
  "title": "Socialization Theories",
  "description": "...",
  "source_material": "materials/sociology/textbook.pdf",
  "attempts": [...],
  "last_practiced": "2025-12-28",
  "next_review": "2026-01-01",
  "srs_interval_days": 4,
  "mastery_level": "learning"
}
```

### Quiz Session Record
```json
{
  "session_id": "session-2025-12-28-1",
  "date": "2025-12-28",
  "topics_practiced": [
    {
      "topic_id": "topic-001",
      "questions_asked": 5,
      "correct_answers": 4
    }
  ],
  "overall_score": 0.8
}
```

See `SCHEMAS.md` for complete documentation.

## 🎓 Best Practices for LLM

### DO:
✅ **Check what's due** at the start of every session
✅ **Focus on overdue topics** - they need attention
✅ **Record results** after each session
✅ **Create topics proactively** when encountering new concepts
✅ **Provide encouraging feedback** based on mastery levels
✅ **Use JSON mode** for programmatic data handling

### DON'T:
❌ **Don't rely solely on chat context** for tracking progress
❌ **Don't skip recording sessions** - data persistence is critical
❌ **Don't ignore spaced repetition** - trust the algorithm
❌ **Don't create duplicate topics** - check existing topics first
❌ **Don't over-quiz on mastered topics** - focus on learning/reviewing

## 🔧 Troubleshooting

### "Topic not found"
- Run `ls -la learning-data/topics/` to see available topics
- Use correct topic ID format: `topic-001` not `1` or `topic-1`

### "No topics due for review"
- Check `python view_progress.py` to see all topics
- Create new topics if needed
- Some topics may not be due yet (check next_review dates)

### "Session not recording"
- Ensure JSON format is valid
- Check that topic IDs exist
- Verify file paths are correct

## 📝 Example Session Workflow

```python
# 1. Start session - what should we practice?
$ python what_to_practice.py --json
# Returns: topic-001 (Socialization), topic-003 (Social Structure)

# 2. LLM conducts quiz on these topics
# User answers 5 questions on topic-001: 4 correct
# User answers 3 questions on topic-003: 2 correct

# 3. Create session record
{
  "date": "2025-12-28",
  "topics_practiced": [
    {"topic_id": "topic-001", "questions_asked": 5, "correct_answers": 4},
    {"topic_id": "topic-003", "questions_asked": 3, "correct_answers": 2}
  ]
}

# 4. Record results
$ python record_quiz.py --json session.json
# System updates:
# - topic-001: next_review = 2026-01-02 (4 days), mastery = "reviewing"
# - topic-003: next_review = 2025-12-29 (1 day), mastery = "learning"

# 5. View progress
$ python view_progress.py
# Shows overall stats and mastery distribution
```

## 🚀 Quick Start for LLM

**First time using this system?**

1. Read this README entirely
2. Check existing topics: `python view_progress.py`
3. If no topics exist, create some based on study materials
4. Start a session: `python what_to_practice.py`
5. Quiz the user on returned topics
6. Record results: `python record_quiz.py --interactive` or via JSON

**Every subsequent session:**

1. `python what_to_practice.py` → Get today's topics
2. Quiz user → Track results
3. `python record_quiz.py` → Save results
4. (Optional) `python view_progress.py` → Show progress

---

## 📚 Additional Documentation

- **SCHEMAS.md** - Complete JSON schema reference
- **scripts/learning_data.py** - Core library source code (readable for understanding internals)

---

**Remember:** This system is designed to complement, not replace, the learning conversation. Use it to maintain continuity and intelligent topic selection across sessions while keeping the actual learning dialogue natural and adaptive.
