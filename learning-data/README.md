# Learning Data System - LLM Guide

**📖 READ THIS COMPLETELY before conducting any learning session.**

## 🎯 Purpose

This system tracks learning progress persistently across chat sessions using JSON files. You (the LLM) will directly create and edit these files to maintain continuity in the user's learning journey.

**Key Benefits:**
- Learning progress persists between sessions
- Intelligent topic review scheduling (spaced repetition)
- No reliance on chat context/history
- User can track mastery progression over time

## 📁 Directory Structure

```
learning-data/
├── topics/              # One JSON file per topic (e.g., topic-001.json)
├── quiz-sessions/       # One JSON file per session (e.g., session-2025-12-28-1.json)
├── progress/
│   ├── global-progress.json  # Overall statistics
│   └── srs-config.json       # Spaced repetition configuration
├── README.md           # This file
└── SCHEMAS.md          # Detailed JSON structure reference
```

## 🔄 Standard Learning Session Workflow

### 1. **Start of Session: Check What to Practice**

**Action:** Read topic files to determine what's due for review today.

```bash
# Read all topics
ls learning-data/topics/

# For each topic file, read it and check:
# - next_review date (is it today or earlier?)
# - mastery_level (prioritize 'learning' and 'reviewing')
# - last_practiced (how long since last practice?)
```

**Prioritization Logic:**
1. **Overdue topics** (next_review < today) - HIGHEST PRIORITY
2. **Topics needing review** (last attempt had status "needs_review")
3. **New topics** (never practiced)
4. **Topics due today** (next_review == today)
5. **Learning/Reviewing topics** (not yet mastered)

**Tell the user:**
"Based on your learning data, you should practice: [Topic 1], [Topic 2], [Topic 3]"

### 2. **During Session: Conduct Quiz**

- Ask quiz questions on the selected topic(s)
- Track in memory: questions asked, correct answers, incorrect answers
- Note specific areas of difficulty

**Keep a running tally:**
```
Topic: Socialization Theory (topic-001)
- Question 1: "What is primary socialization?" → Correct ✓
- Question 2: "Name three agents..." → Correct ✓
- Question 3: "What is anticipatory..." → Incorrect ✗
- Question 4: "Define resocialization..." → Correct ✓
- Question 5: "Looking-glass self..." → Correct ✓

Score: 4/5 (80%)
```

### 3. **End of Session: Record Results**

**You MUST do all of these steps:**

#### Step 3a: Create Session Record

**File:** `learning-data/quiz-sessions/session-YYYY-MM-DD-N.json`

- Check existing sessions for today to determine N (1, 2, 3...)
- Create new session file with this structure:

```json
{
  "session_id": "session-2025-12-28-1",
  "date": "2025-12-28",
  "start_time": "2025-12-28T14:30:00Z",
  "end_time": "2025-12-28T15:00:00Z",
  "topics_practiced": [
    {
      "topic_id": "topic-001",
      "questions_asked": 5,
      "correct_answers": 4,
      "questions": [
        {
          "question": "What is primary socialization?",
          "user_answer": "Learning during childhood from family",
          "correct": true,
          "notes": "Good understanding"
        },
        {
          "question": "What is anticipatory socialization?",
          "user_answer": "Not sure",
          "correct": false,
          "notes": "Needs review on this concept"
        }
      ]
    }
  ],
  "overall_score": 0.80,
  "session_notes": "Strong on basic concepts, needs review on advanced terminology",
  "chat_context_summary": ""
}
```

#### Step 3b: Update Topic Records

For each topic practiced, **read** the topic file, then **update** it:

**Add new attempt to attempts array:**
```json
{
  "session_id": "session-2025-12-28-1",
  "date": "2025-12-28",
  "score": 4,
  "total": 5,
  "status": "mastered"  // See status rules below
}
```

**Status determination:**
- `needs_review`: Score < 60%
- `improving`: Score 60-79%
- `mastered`: Score ≥ 80%

**Update these fields:**
```json
{
  "last_practiced": "2025-12-28",
  "next_review": "2026-01-02",  // Calculate using rules below
  "srs_interval_days": 5,       // Calculate using rules below
  "mastery_level": "reviewing"  // See mastery rules below
}
```

**Spaced Repetition Calculation Rules:**

Read `learning-data/progress/srs-config.json` for configuration, then:

```
IF score >= 80% (success):
  new_interval = current_interval × 2.5
  new_interval = MIN(new_interval, 180)  // max 180 days

ELSE (failure):
  new_interval = 1  // reset to 1 day

next_review = today + new_interval days
```

**Mastery Level Determination:**

Look at the last 3 attempts:

```
IF no attempts:
  mastery_level = "new"

ELSE IF last 3 attempts all >= 90%:
  mastery_level = "mastered"

ELSE IF average of last 3 attempts >= 80%:
  mastery_level = "reviewing"

ELSE:
  mastery_level = "learning"
```

#### Step 3c: Update Global Progress

**Read** `learning-data/progress/global-progress.json`, then **update**:

```json
{
  "last_updated": "2025-12-28T15:00:00Z",
  "total_topics": 5,  // Count topic files
  "topics_by_mastery": {
    "new": 1,       // Count topics with mastery_level = "new"
    "learning": 2,  // Count topics with mastery_level = "learning"
    "reviewing": 1,
    "mastered": 1
  },
  "total_sessions": 3,  // Increment by 1
  "total_questions_answered": 45,  // Add questions from this session
  "overall_accuracy": 82.5,  // Recalculate from all topic attempts
  "study_streak_days": 3,
  "last_study_date": "2025-12-28"
}
```

**Calculate overall_accuracy:**
```
1. Read ALL topic files
2. Sum all attempt.score values
3. Sum all attempt.total values
4. overall_accuracy = (total_correct / total_questions) × 100
```

### 4. **Provide Feedback to User**

Based on the results:

```
Score 90-100%: "Excellent! You've mastered this topic."
Score 80-89%:  "Great job! You're on track to mastery."
Score 60-79%:  "Good progress. Focus on [weak areas]."
Score < 60%:   "This needs more practice. Let's review [concepts]."
```

Include next review information:
"I've scheduled your next review of [Topic] for [date] ([X] days from now)."

## 📝 Creating New Topics

When the user starts studying a new concept, create a topic file.

**File:** `learning-data/topics/topic-XXX.json` (use next sequential number)

**To find next number:**
```bash
ls learning-data/topics/  # Look for highest number, add 1
```

**Initial topic structure:**
```json
{
  "topic_id": "topic-001",
  "title": "Socialization Theory",
  "description": "Primary and secondary socialization, agents of socialization",
  "source_material": "materials/sociology/textbook-ch3.pdf",
  "source_reference": "Pages 45-60",
  "created_date": "2025-12-28",
  "attempts": [],
  "last_practiced": null,
  "next_review": "2025-12-28",  // Available immediately
  "srs_interval_days": 1,
  "mastery_level": "new",
  "tags": ["socialization", "theory"]
}
```

**Tell the user:**
"I've created a new topic: [Title] (topic-XXX). It's ready for practice."

## 🎯 Querying Learning Data

### Check What's Due Today

```bash
# Read all topic files
# Filter where: next_review <= today
# Sort by: next_review ASC (oldest first)
# Return top 5-10
```

### Show Overall Progress

```bash
# Read: learning-data/progress/global-progress.json
# Display: mastery distribution, accuracy, last study date
```

### Show Topic Details

```bash
# Read: learning-data/topics/topic-XXX.json
# Display: attempts history, current mastery, next review
```

## 📊 Example Complete Session Flow

```
USER: "Let's practice sociology"

LLM:
1. Reads all files in learning-data/topics/
2. Finds: topic-001 (Socialization) is overdue by 2 days
3. Finds: topic-003 (Functionalism) is due today
4. Says: "You have 2 topics due: Socialization (overdue!) and Functionalism.
         Let's start with Socialization..."

5. Asks 5 quiz questions, user gets 4 correct
6. Creates: learning-data/quiz-sessions/session-2025-12-28-1.json
7. Updates: learning-data/topics/topic-001.json
   - Adds attempt: {score: 4, total: 5, status: "mastered"}
   - Updates: last_practiced = "2025-12-28"
   - Calculates: next_review = "2026-01-02" (5 days, since score was 80%)
   - Updates: mastery_level = "reviewing" (based on attempt history)
8. Updates: learning-data/progress/global-progress.json
9. Says: "Great job! 4/5 (80%). Next review: Jan 2nd (5 days from now).
         Your mastery level is now 'reviewing'."
```

## ⚠️ Important Rules for LLM

### DO:
✅ **Always check what's due** at start of session
✅ **Always record results** after each quiz session
✅ **Create topics proactively** when new concepts arise
✅ **Update ALL files** (session, topic, global progress)
✅ **Calculate dates accurately** using spaced repetition rules
✅ **Provide encouraging feedback** based on mastery levels

### DON'T:
❌ **Don't skip recording** - persistence is the point
❌ **Don't ignore overdue topics** - they need attention
❌ **Don't guess at calculations** - follow the rules exactly
❌ **Don't create duplicate topics** - check existing first
❌ **Don't forget to commit** - ask user to commit after session

## 🔧 Troubleshooting

**"No topics found"**
- Check if learning-data/topics/ is empty
- Create first topic when user starts studying

**"Can't determine next ID"**
- List files: `ls learning-data/topics/`
- If empty, start with topic-001
- Otherwise, find highest number and add 1

**"Date calculations wrong"**
- Use ISO format: YYYY-MM-DD
- Read srs-config.json for multipliers
- Show your work when calculating

## 📚 Reference

See **SCHEMAS.md** for:
- Complete JSON structure specifications
- Field definitions and constraints
- Detailed examples

## 🚀 Getting Started

**First time using this system:**

1. Read this README completely
2. Check if any topics exist: `ls learning-data/topics/`
3. If none, create topics based on what user wants to study
4. Start session: determine what to practice
5. Quiz user, record results
6. Repeat!

**Every subsequent session:**

1. Check what's due for review
2. Quiz user on those topics
3. Record all results
4. Update progress files
5. Provide feedback and next steps

---

**Remember:** This system ensures learning continuity across sessions. Your job is to maintain it accurately so the user can trust the data and benefit from spaced repetition.
