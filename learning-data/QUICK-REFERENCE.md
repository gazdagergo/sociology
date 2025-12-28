# Quick Reference for LLM

**IMPORTANT: Read `/learning-data/README.md` first for complete understanding.**

This is a quick cheat sheet for common operations during learning sessions.

## 🔄 Standard Session Workflow

```bash
# 1. START OF SESSION
cd learning-data/scripts
python what_to_practice.py

# 2. QUIZ USER ON RETURNED TOPICS
# (conduct quiz, track results in memory)

# 3. END OF SESSION - Save results via JSON
# Create session JSON with results, then:
python record_quiz.py --json /tmp/session.json

# 4. OPTIONAL - Show progress
python view_progress.py
```

## 📋 Command Cheat Sheet

### Query Commands (Read-Only)

```bash
# What should we practice today?
python what_to_practice.py
python what_to_practice.py --limit 5        # Top 5 only
python what_to_practice.py --json           # JSON output

# Show overall progress
python view_progress.py
python view_progress.py --json              # JSON output

# Show specific topic progress
python view_progress.py --topic topic-001
python view_progress.py --topic topic-001 --json
```

### Write Commands (Modify Data)

```bash
# Create new topic
python create_topic.py "Title" "Description" "source.pdf" "tag1,tag2"

# Record quiz session (interactive)
python record_quiz.py --interactive

# Record quiz session (JSON)
python record_quiz.py --json session-file.json
```

## 📄 Session JSON Template

```json
{
  "date": "YYYY-MM-DD",
  "topics_practiced": [
    {
      "topic_id": "topic-XXX",
      "questions_asked": 5,
      "correct_answers": 4,
      "questions": [
        {
          "question": "Question text?",
          "user_answer": "User's answer",
          "correct": true,
          "notes": "Optional feedback"
        }
      ]
    }
  ],
  "overall_score": 0.80,
  "session_notes": "Optional summary"
}
```

## 🎯 Decision Tree for LLM

```
User wants to practice
  ├─> Query what_to_practice.py
  │   └─> Get list of topics due
  │
  ├─> Ask quiz questions on those topics
  │   └─> Track: topic_id, questions_asked, correct_answers
  │
  └─> End of session
      ├─> Create session JSON
      └─> Run record_quiz.py --json

User asks about progress
  ├─> Overall? → python view_progress.py
  └─> Specific topic? → python view_progress.py --topic topic-XXX

User encounters new concept
  └─> python create_topic.py "Title" "Description" ...
```

## 💡 Pro Tips

1. **Always** check `what_to_practice.py` at session start
2. **Always** record results with `record_quiz.py` at session end
3. **Never** skip recording - data persistence is the whole point
4. **Use JSON mode** for programmatic handling (easier for LLM)
5. **Provide encouragement** based on mastery_level and trends
6. **Trust the algorithm** - don't override spaced repetition dates

## 🚨 Common Mistakes to Avoid

❌ Conducting quiz without checking what's due first
❌ Not recording session results
❌ Creating duplicate topics
❌ Hardcoding topic IDs (query them instead)
❌ Ignoring overdue topics
❌ Over-quizzing mastered topics

## 📊 Interpreting Mastery Levels

| Level | Meaning | Action |
|-------|---------|--------|
| `new` | Never practiced | Start with basics, build foundation |
| `learning` | Active learning | Focus practice here, provide detailed explanations |
| `reviewing` | Solid understanding | Periodic review, deeper questions |
| `mastered` | Fully mastered | Light review only, advanced applications |

## 🎓 Providing Feedback to User

Based on topic status:

- **< 60%**: "Let's review the key concepts. This needs more practice."
- **60-79%**: "You're improving! Focus on [weak areas]."
- **80-89%**: "Good job! You're on track to master this."
- **≥ 90%**: "Excellent! You've mastered this topic."

Based on mastery progression:
- **new → learning**: "Great start! Keep practicing."
- **learning → reviewing**: "You're getting it! Solid progress."
- **reviewing → mastered**: "Outstanding! This is now mastered."

## 📁 File Locations

All paths relative to repository root:

- Topics: `learning-data/topics/topic-*.json`
- Sessions: `learning-data/quiz-sessions/session-*.json`
- Progress: `learning-data/progress/global-progress.json`
- Config: `learning-data/progress/srs-config.json`
- Scripts: `learning-data/scripts/*.py`

## 🔍 Quick Debugging

```bash
# List all topics
ls -la learning-data/topics/

# List all sessions
ls -la learning-data/quiz-sessions/

# View a specific file
cat learning-data/topics/topic-001.json | python -m json.tool

# Check global progress
cat learning-data/progress/global-progress.json | python -m json.tool
```

---

**Remember:** This system makes learning sessions persistent and intelligent. Use it every session!
