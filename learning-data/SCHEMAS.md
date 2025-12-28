# Learning Data Schemas

This document defines the JSON schemas used for tracking learning progress.

## Topic Record Schema

**File Location:** `/learning-data/topics/topic-{id}.json`

Each topic represents a concept, theory, or area of study that can be practiced.

```json
{
  "topic_id": "string (unique identifier, e.g., 'topic-001')",
  "title": "string (human-readable topic name)",
  "description": "string (brief description of what this topic covers)",
  "source_material": "string (path to source material, e.g., 'materials/sociology/textbook.pdf')",
  "source_reference": "string (optional: page numbers, chapter, section)",
  "created_date": "string (ISO date: YYYY-MM-DD)",
  "attempts": [
    {
      "session_id": "string (reference to quiz-session file)",
      "date": "string (ISO date: YYYY-MM-DD)",
      "score": "number (questions answered correctly)",
      "total": "number (total questions asked)",
      "status": "string (needs_review|improving|mastered)"
    }
  ],
  "last_practiced": "string (ISO date: YYYY-MM-DD)",
  "next_review": "string (ISO date: YYYY-MM-DD)",
  "srs_interval_days": "number (current spaced repetition interval)",
  "mastery_level": "string (new|learning|reviewing|mastered)",
  "tags": ["array of strings (categories, keywords)"]
}
```

### Mastery Levels
- **new**: Never practiced
- **learning**: Currently being learned (< 80% success rate)
- **reviewing**: Known but needs periodic review (≥ 80% success rate)
- **mastered**: Consistently correct (≥ 90% across 3+ sessions)

## Quiz Session Record Schema

**File Location:** `/learning-data/quiz-sessions/session-{date}-{number}.json`

Each session represents a study/practice session.

```json
{
  "session_id": "string (unique identifier, e.g., 'session-2025-12-28-1')",
  "date": "string (ISO date: YYYY-MM-DD)",
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime, optional)",
  "topics_practiced": [
    {
      "topic_id": "string",
      "questions_asked": "number",
      "correct_answers": "number",
      "questions": [
        {
          "question": "string (the question text)",
          "user_answer": "string (what the student answered)",
          "correct": "boolean",
          "notes": "string (optional: feedback, explanation)"
        }
      ]
    }
  ],
  "overall_score": "number (total correct / total questions)",
  "session_notes": "string (optional: general observations about the session)",
  "chat_context_summary": "string (optional: key insights from the session)"
}
```

## Global Progress Schema

**File Location:** `/learning-data/progress/global-progress.json`

Tracks overall learning progress across all topics.

```json
{
  "last_updated": "string (ISO datetime)",
  "total_topics": "number",
  "topics_by_mastery": {
    "new": "number",
    "learning": "number",
    "reviewing": "number",
    "mastered": "number"
  },
  "total_sessions": "number",
  "total_questions_answered": "number",
  "overall_accuracy": "number (percentage)",
  "study_streak_days": "number",
  "last_study_date": "string (ISO date)"
}
```

## Spaced Repetition Algorithm

**File Location:** `/learning-data/progress/srs-config.json`

Configuration for the spaced repetition system.

```json
{
  "algorithm": "SM2-simplified",
  "intervals": {
    "initial": 1,
    "success_multiplier": 2.5,
    "failure_reset": 1,
    "max_interval": 180
  },
  "mastery_thresholds": {
    "learning_to_reviewing": 0.8,
    "reviewing_to_mastered": 0.9,
    "mastered_attempts_required": 3
  }
}
```

## Status Values

### Topic Status (per attempt)
- `needs_review`: Score < 60%
- `improving`: Score 60-79%
- `mastered`: Score ≥ 80%

### Mastery Level (overall topic state)
- `new`: Never attempted
- `learning`: Active learning phase
- `reviewing`: Periodic review phase
- `mastered`: Fully mastered

## File Naming Conventions

- Topics: `topic-{sequential-number}.json` (e.g., `topic-001.json`)
- Sessions: `session-{YYYY-MM-DD}-{session-number}.json` (e.g., `session-2025-12-28-1.json`)
- Progress files: Use descriptive names (e.g., `global-progress.json`, `srs-config.json`)

## Data Flow

1. **Before Study Session**: Query what topics are due for review
2. **During Session**: LLM asks quiz questions on selected topics
3. **After Session**: Record results using `record_quiz.py`
4. **System Updates**:
   - Topic records updated with new attempts
   - Next review dates calculated
   - Global progress statistics updated
   - Session record created
