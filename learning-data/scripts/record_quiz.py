#!/usr/bin/env python3
"""
Record quiz results after a study session.

This script updates topic records with quiz attempt data and creates session records.

Usage:
    python record_quiz.py --interactive
    python record_quiz.py --json <session_data.json>

Interactive mode walks you through recording a session.
JSON mode accepts a pre-formatted session data file.
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from learning_data import (
    load_topic,
    save_topic,
    get_next_session_id,
    save_session,
    calculate_next_review_date,
    determine_mastery_level,
    update_global_progress,
    load_srs_config
)


def record_quiz_session_interactive():
    """Interactive mode for recording quiz results."""

    print("=== Record Quiz Session ===\n")

    session_id = get_next_session_id()
    date = datetime.now().strftime("%Y-%m-%d")

    print(f"Session ID: {session_id}")
    print(f"Date: {date}\n")

    topics_practiced = []

    while True:
        print("\n--- Topic Quiz Results ---")
        topic_id = input("Topic ID (or 'done' to finish): ").strip()

        if topic_id.lower() == 'done':
            break

        # Load topic
        topic = load_topic(topic_id)
        if not topic:
            print(f"Error: Topic {topic_id} not found. Please create it first.")
            continue

        print(f"Topic: {topic['title']}")

        # Get quiz results
        try:
            questions_asked = int(input("Number of questions asked: ").strip())
            correct_answers = int(input("Number of correct answers: ").strip())
        except ValueError:
            print("Error: Please enter valid numbers.")
            continue

        if correct_answers > questions_asked:
            print("Error: Correct answers cannot exceed total questions.")
            continue

        # Optional: detailed questions
        questions_detail = []
        add_details = input("Add detailed question info? (y/n): ").strip().lower()

        if add_details == 'y':
            for i in range(questions_asked):
                print(f"\nQuestion {i+1}:")
                q_text = input("  Question text: ").strip()
                user_ans = input("  User's answer: ").strip()
                is_correct = input("  Correct? (y/n): ").strip().lower() == 'y'
                notes = input("  Notes (optional): ").strip()

                questions_detail.append({
                    "question": q_text,
                    "user_answer": user_ans,
                    "correct": is_correct,
                    "notes": notes
                })

        # Record topic results
        topic_result = {
            "topic_id": topic_id,
            "questions_asked": questions_asked,
            "correct_answers": correct_answers,
            "questions": questions_detail
        }
        topics_practiced.append(topic_result)

        # Update topic record
        update_topic_with_attempt(topic, session_id, date, correct_answers, questions_asked)

        print(f"✓ Recorded: {correct_answers}/{questions_asked} ({correct_answers/questions_asked*100:.1f}%)")

    if not topics_practiced:
        print("\nNo topics recorded. Exiting.")
        return

    # Session notes
    print("\n--- Session Summary ---")
    session_notes = input("Session notes (optional): ").strip()

    # Calculate overall score
    total_correct = sum(t['correct_answers'] for t in topics_practiced)
    total_questions = sum(t['questions_asked'] for t in topics_practiced)
    overall_score = total_correct / total_questions if total_questions > 0 else 0

    # Create session record
    session_data = {
        "session_id": session_id,
        "date": date,
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "topics_practiced": topics_practiced,
        "overall_score": round(overall_score, 2),
        "session_notes": session_notes,
        "chat_context_summary": ""
    }

    save_session(session_data)
    update_global_progress(session_data)

    print(f"\n✓ Session saved: {session_id}")
    print(f"  Overall score: {total_correct}/{total_questions} ({overall_score*100:.1f}%)")
    print(f"  Topics practiced: {len(topics_practiced)}")


def update_topic_with_attempt(
    topic: dict,
    session_id: str,
    date: str,
    score: int,
    total: int
) -> None:
    """Update topic record with new attempt data."""

    srs_config = load_srs_config()
    accuracy = score / total if total > 0 else 0

    # Determine status for this attempt
    if accuracy >= 0.8:
        status = "mastered"
    elif accuracy >= 0.6:
        status = "improving"
    else:
        status = "needs_review"

    # Add attempt record
    attempt = {
        "session_id": session_id,
        "date": date,
        "score": score,
        "total": total,
        "status": status
    }
    topic['attempts'].append(attempt)

    # Update last practiced
    topic['last_practiced'] = date

    # Calculate next review date
    success = accuracy >= 0.8
    current_interval = topic.get('srs_interval_days', 1)
    next_review, new_interval = calculate_next_review_date(
        current_interval, success, srs_config
    )
    topic['next_review'] = next_review
    topic['srs_interval_days'] = new_interval

    # Update mastery level
    topic['mastery_level'] = determine_mastery_level(topic['attempts'], srs_config)

    # Save updated topic
    save_topic(topic)


def record_quiz_session_from_json(json_file: Path):
    """Record quiz session from a JSON file."""

    with open(json_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)

    # Validate and set defaults
    if 'session_id' not in session_data:
        session_data['session_id'] = get_next_session_id()

    if 'date' not in session_data:
        session_data['date'] = datetime.now().strftime("%Y-%m-%d")

    # Process each topic
    for topic_result in session_data.get('topics_practiced', []):
        topic_id = topic_result['topic_id']
        topic = load_topic(topic_id)

        if not topic:
            print(f"Warning: Topic {topic_id} not found. Skipping.")
            continue

        update_topic_with_attempt(
            topic,
            session_data['session_id'],
            session_data['date'],
            topic_result['correct_answers'],
            topic_result['questions_asked']
        )

    # Save session
    save_session(session_data)
    update_global_progress(session_data)

    print(f"✓ Session recorded from JSON: {session_data['session_id']}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python record_quiz.py --interactive")
        print("  python record_quiz.py --json <file.json>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "--interactive":
        record_quiz_session_interactive()
    elif mode == "--json" and len(sys.argv) > 2:
        json_file = Path(sys.argv[2])
        if not json_file.exists():
            print(f"Error: File not found: {json_file}")
            sys.exit(1)
        record_quiz_session_from_json(json_file)
    else:
        print("Invalid arguments. Use --interactive or --json <file>")
        sys.exit(1)


if __name__ == "__main__":
    main()
