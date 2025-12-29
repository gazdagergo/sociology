# JSON Schemas Reference

This document defines the structure of all JSON files in the learning data system.

## Topic Record

**Location:** `learning-data/topics/topic-XXX.json`

**Purpose:** Tracks a single learning topic with attempt history and scheduling data.

```json
{
  "topic_id": "topic-001",
  "title": "Socialization Theory",
  "description": "Primary and secondary socialization, agents of socialization, socialization theories",
  "source_material": "materials/sociology/textbook-ch3.pdf",
  "source_reference": "Pages 45-60, Chapter 3",
  "created_date": "2025-12-28",
  "attempts": [
    {
      "session_id": "session-2025-12-28-1",
      "date": "2025-12-28",
      "score": 4,
      "total": 5,
      "status": "mastered"
    },
    {
      "session_id": "session-2025-12-30-1",
      "date": "2025-12-30",
      "score": 5,
      "total": 5,
      "status": "mastered"
    }
  ],
  "last_practiced": "2025-12-30",
  "next_review": "2026-01-06",
  "srs_interval_days": 7,
  "mastery_level": "reviewing",
  "tags": ["socialization", "theory", "agents"]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Unique identifier (e.g., "topic-001") |
| `title` | string | Human-readable topic name |
| `description` | string | Brief description of what this topic covers |
| `source_material` | string | Path to source material (optional) |
| `source_reference` | string | Specific pages/sections (optional) |
| `created_date` | string | ISO date when topic was created (YYYY-MM-DD) |
| `attempts` | array | History of all quiz attempts (see below) |
| `last_practiced` | string\|null | ISO date of most recent attempt |
| `next_review` | string | ISO date when next review is due |
| `srs_interval_days` | number | Current spaced repetition interval in days |
| `mastery_level` | string | Current mastery: "new", "learning", "reviewing", "mastered" |
| `tags` | array | Keywords for categorization |

### Attempt Object

```json
{
  "session_id": "session-2025-12-28-1",
  "date": "2025-12-28",
  "score": 4,
  "total": 5,
  "status": "mastered"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Reference to quiz session file |
| `date` | string | ISO date of attempt (YYYY-MM-DD) |
| `score` | number | Number of correct answers |
| `total` | number | Total number of questions |
| `status` | string | "needs_review" (<60%), "improving" (60-79%), "mastered" (≥80%) |

### Mastery Levels

| Level | Meaning | When to Use |
|-------|---------|-------------|
| `new` | Never practiced | Initial state, no attempts |
| `learning` | Active learning phase | Average of last 3 attempts < 80% |
| `reviewing` | Periodic review needed | Average of last 3 attempts ≥ 80% |
| `mastered` | Fully mastered | Last 3 attempts all ≥ 90% |

---

## Quiz Session Record

**Location:** `learning-data/quiz-sessions/session-YYYY-MM-DD-N.json`

**Purpose:** Records a complete quiz session with all topics practiced.

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
          "user_answer": "Learning during childhood from family and close relationships",
          "correct": true,
          "notes": "Good understanding of core concept"
        },
        {
          "question": "What is anticipatory socialization?",
          "user_answer": "Not sure, maybe learning in advance?",
          "correct": false,
          "notes": "Needs review - anticipatory socialization is preparing for future roles"
        }
      ]
    }
  ],
  "overall_score": 0.80,
  "session_notes": "Strong grasp of basic socialization concepts. Struggled with advanced terminology like anticipatory socialization.",
  "chat_context_summary": "Focused on Chapter 3 concepts. Student shows good retention of primary/secondary socialization but needs more practice on specialized terms."
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique identifier (session-YYYY-MM-DD-N) |
| `date` | string | ISO date of session (YYYY-MM-DD) |
| `start_time` | string | ISO datetime when session started (optional) |
| `end_time` | string | ISO datetime when session ended (optional) |
| `topics_practiced` | array | List of topics quizzed in this session |
| `overall_score` | number | Overall accuracy (0.0 to 1.0) |
| `session_notes` | string | Summary of session insights |
| `chat_context_summary` | string | Optional context from the learning dialogue |

### Topic Practice Object

```json
{
  "topic_id": "topic-001",
  "questions_asked": 5,
  "correct_answers": 4,
  "questions": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Reference to topic file |
| `questions_asked` | number | Total questions for this topic |
| `correct_answers` | number | Number answered correctly |
| `questions` | array | Detailed question records (optional) |

### Question Object

```json
{
  "question": "What is primary socialization?",
  "user_answer": "Learning during childhood from family",
  "correct": true,
  "notes": "Good understanding"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The question text |
| `user_answer` | string | What the user answered |
| `correct` | boolean | Whether answer was correct |
| `notes` | string | Feedback or observations (optional) |

---

## Global Progress

**Location:** `learning-data/progress/global-progress.json`

**Purpose:** Overall learning statistics across all topics.

```json
{
  "last_updated": "2025-12-28T15:00:00Z",
  "total_topics": 5,
  "topics_by_mastery": {
    "new": 1,
    "learning": 2,
    "reviewing": 1,
    "mastered": 1
  },
  "total_sessions": 3,
  "total_questions_answered": 45,
  "overall_accuracy": 82.5,
  "study_streak_days": 3,
  "last_study_date": "2025-12-28"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `last_updated` | string | ISO datetime of last update |
| `total_topics` | number | Count of all topic files |
| `topics_by_mastery` | object | Count of topics at each mastery level |
| `total_sessions` | number | Total quiz sessions completed |
| `total_questions_answered` | number | Cumulative questions answered |
| `overall_accuracy` | number | Overall percentage correct (0-100) |
| `study_streak_days` | number | Consecutive days studied (future feature) |
| `last_study_date` | string\|null | ISO date of last session |

---

## SRS Configuration

**Location:** `learning-data/progress/srs-config.json`

**Purpose:** Configuration for spaced repetition algorithm.

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

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `algorithm` | string | Algorithm name (informational) |
| `intervals.initial` | number | Starting interval in days |
| `intervals.success_multiplier` | number | Multiply interval by this on success (≥80%) |
| `intervals.failure_reset` | number | Reset to this interval on failure (<80%) |
| `intervals.max_interval` | number | Maximum interval in days |
| `mastery_thresholds.learning_to_reviewing` | number | Score threshold (0.0-1.0) for reviewing status |
| `mastery_thresholds.reviewing_to_mastered` | number | Score threshold for mastered status |
| `mastery_thresholds.mastered_attempts_required` | number | Consecutive high scores needed for mastered |

---

## File Naming Conventions

| Type | Pattern | Examples |
|------|---------|----------|
| Topics | `topic-XXX.json` | `topic-001.json`, `topic-042.json` |
| Sessions | `session-YYYY-MM-DD-N.json` | `session-2025-12-28-1.json`, `session-2025-12-28-2.json` |
| Progress | Fixed names | `global-progress.json`, `srs-config.json` |

**Notes:**
- Use 3-digit zero-padded numbers for topics (001, 002, ...)
- Session number N increments per day (multiple sessions per day allowed)
- All dates use ISO format: YYYY-MM-DD
- All datetimes use ISO format: YYYY-MM-DDTHH:MM:SSZ

---

## Quick Reference

### Creating a New Topic

1. Find next ID: `ls learning-data/topics/` → use next number
2. Create file: `learning-data/topics/topic-XXX.json`
3. Use template from this document
4. Set `mastery_level: "new"`, `attempts: []`, `next_review: today`

### Recording a Quiz Session

1. Create session file: `learning-data/quiz-sessions/session-YYYY-MM-DD-N.json`
2. For each topic quizzed:
   - Read topic file
   - Add new attempt to `attempts` array
   - Update `last_practiced`, `next_review`, `srs_interval_days`, `mastery_level`
   - Write updated topic file
3. Update `learning-data/progress/global-progress.json`

### Calculating Next Review Date

```
current_interval = topic.srs_interval_days
score_percentage = score / total

IF score_percentage >= 0.80:
  new_interval = current_interval × 2.5
  new_interval = MIN(new_interval, 180)
ELSE:
  new_interval = 1

next_review = today + new_interval days
```

### Determining Mastery Level

```
attempts = topic.attempts (last 3)

IF no attempts:
  → "new"
ELSE IF all last 3 attempts have score/total >= 0.90:
  → "mastered"
ELSE IF average(last 3 attempts) >= 0.80:
  → "reviewing"
ELSE:
  → "learning"
```

---

**This schema is designed to be simple enough for manual editing while providing structure for tracking learning progress over time.**
