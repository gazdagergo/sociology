#!/usr/bin/env python3
"""
Core library for managing learning data.
Provides functions for reading, writing, and updating learning records.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# Base paths
BASE_DIR = Path(__file__).parent.parent
TOPICS_DIR = BASE_DIR / "topics"
SESSIONS_DIR = BASE_DIR / "quiz-sessions"
PROGRESS_DIR = BASE_DIR / "progress"

# Ensure directories exist
TOPICS_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
PROGRESS_DIR.mkdir(exist_ok=True)


def load_json(filepath: Path) -> Dict:
    """Load JSON file, return empty dict if not exists."""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(filepath: Path, data: Dict) -> None:
    """Save data to JSON file with pretty formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic_id() -> str:
    """Generate next sequential topic ID."""
    existing_topics = list(TOPICS_DIR.glob("topic-*.json"))
    if not existing_topics:
        return "topic-001"

    # Extract numbers from existing topics
    numbers = []
    for topic_file in existing_topics:
        try:
            num = int(topic_file.stem.split('-')[1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue

    next_num = max(numbers) + 1 if numbers else 1
    return f"topic-{next_num:03d}"


def get_next_session_id(date: str = None) -> str:
    """Generate next session ID for given date."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    existing_sessions = list(SESSIONS_DIR.glob(f"session-{date}-*.json"))
    if not existing_sessions:
        return f"session-{date}-1"

    # Extract session numbers for this date
    numbers = []
    for session_file in existing_sessions:
        try:
            num = int(session_file.stem.split('-')[-1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue

    next_num = max(numbers) + 1 if numbers else 1
    return f"session-{date}-{next_num}"


def load_topic(topic_id: str) -> Optional[Dict]:
    """Load a topic record by ID."""
    topic_file = TOPICS_DIR / f"{topic_id}.json"
    if not topic_file.exists():
        return None
    return load_json(topic_file)


def save_topic(topic_data: Dict) -> None:
    """Save a topic record."""
    topic_id = topic_data['topic_id']
    topic_file = TOPICS_DIR / f"{topic_id}.json"
    save_json(topic_file, topic_data)


def load_all_topics() -> List[Dict]:
    """Load all topic records."""
    topics = []
    for topic_file in sorted(TOPICS_DIR.glob("topic-*.json")):
        topics.append(load_json(topic_file))
    return topics


def load_session(session_id: str) -> Optional[Dict]:
    """Load a session record by ID."""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        return None
    return load_json(session_file)


def save_session(session_data: Dict) -> None:
    """Save a session record."""
    session_id = session_data['session_id']
    session_file = SESSIONS_DIR / f"{session_id}.json"
    save_json(session_file, session_data)


def load_global_progress() -> Dict:
    """Load global progress data."""
    progress_file = PROGRESS_DIR / "global-progress.json"
    return load_json(progress_file)


def save_global_progress(progress_data: Dict) -> None:
    """Save global progress data."""
    progress_file = PROGRESS_DIR / "global-progress.json"
    save_json(progress_file, progress_data)


def load_srs_config() -> Dict:
    """Load spaced repetition configuration."""
    config_file = PROGRESS_DIR / "srs-config.json"
    return load_json(config_file)


def calculate_next_review_date(
    current_interval: int,
    success: bool,
    srs_config: Dict = None
) -> tuple[str, int]:
    """
    Calculate next review date and new interval based on performance.

    Args:
        current_interval: Current SRS interval in days
        success: Whether the attempt was successful (score >= 80%)
        srs_config: SRS configuration (loaded if not provided)

    Returns:
        Tuple of (next_review_date as ISO string, new_interval in days)
    """
    if srs_config is None:
        srs_config = load_srs_config()

    intervals = srs_config['intervals']

    if success:
        # Increase interval
        new_interval = int(current_interval * intervals['success_multiplier'])
        new_interval = min(new_interval, intervals['max_interval'])
    else:
        # Reset to initial interval on failure
        new_interval = intervals['failure_reset']

    next_date = datetime.now() + timedelta(days=new_interval)
    return next_date.strftime("%Y-%m-%d"), new_interval


def determine_mastery_level(attempts: List[Dict], srs_config: Dict = None) -> str:
    """
    Determine mastery level based on attempt history.

    Args:
        attempts: List of attempt records
        srs_config: SRS configuration (loaded if not provided)

    Returns:
        Mastery level: 'new', 'learning', 'reviewing', or 'mastered'
    """
    if srs_config is None:
        srs_config = load_srs_config()

    if not attempts:
        return "new"

    thresholds = srs_config['mastery_thresholds']

    # Calculate recent performance (last 3 attempts)
    recent_attempts = attempts[-3:]
    recent_scores = [
        a['score'] / a['total'] if a['total'] > 0 else 0
        for a in recent_attempts
    ]
    avg_recent_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0

    # Check for mastered status
    if len(recent_attempts) >= thresholds['mastered_attempts_required']:
        if all(score >= thresholds['reviewing_to_mastered'] for score in recent_scores):
            return "mastered"

    # Check for reviewing status
    if avg_recent_score >= thresholds['learning_to_reviewing']:
        return "reviewing"

    # Otherwise, still learning
    return "learning"


def update_global_progress(session_data: Dict) -> None:
    """Update global progress statistics after a session."""
    progress = load_global_progress()

    # Update last studied date
    progress['last_study_date'] = session_data['date']
    progress['last_updated'] = datetime.now().isoformat()

    # Increment session count
    progress['total_sessions'] = progress.get('total_sessions', 0) + 1

    # Count topics by mastery level
    all_topics = load_all_topics()
    progress['total_topics'] = len(all_topics)

    mastery_counts = {'new': 0, 'learning': 0, 'reviewing': 0, 'mastered': 0}
    for topic in all_topics:
        level = topic.get('mastery_level', 'new')
        mastery_counts[level] = mastery_counts.get(level, 0) + 1
    progress['topics_by_mastery'] = mastery_counts

    # Calculate total questions and accuracy
    total_correct = 0
    total_questions = 0
    for topic_session in session_data.get('topics_practiced', []):
        total_correct += topic_session.get('correct_answers', 0)
        total_questions += topic_session.get('questions_asked', 0)

    # Update running totals
    progress['total_questions_answered'] = (
        progress.get('total_questions_answered', 0) + total_questions
    )

    # Calculate overall accuracy
    if progress['total_questions_answered'] > 0:
        # We need to recalculate from all topics for accuracy
        all_correct = 0
        all_total = 0
        for topic in all_topics:
            for attempt in topic.get('attempts', []):
                all_correct += attempt.get('score', 0)
                all_total += attempt.get('total', 0)

        if all_total > 0:
            progress['overall_accuracy'] = round(all_correct / all_total * 100, 2)

    save_global_progress(progress)


if __name__ == "__main__":
    print("Learning Data Library")
    print(f"Base directory: {BASE_DIR}")
    print(f"Topics directory: {TOPICS_DIR}")
    print(f"Sessions directory: {SESSIONS_DIR}")
    print(f"Progress directory: {PROGRESS_DIR}")
