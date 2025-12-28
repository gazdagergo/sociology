#!/usr/bin/env python3
"""
View learning progress and statistics.

Usage:
    python view_progress.py [--topic TOPIC_ID] [--json]

Options:
    --topic TOPIC_ID    Show detailed progress for a specific topic
    --json              Output as JSON instead of human-readable format

Examples:
    python view_progress.py                 # Overall progress
    python view_progress.py --topic topic-001  # Specific topic progress
    python view_progress.py --json          # JSON output
"""

import sys
import json
from datetime import datetime
from learning_data import (
    load_global_progress,
    load_all_topics,
    load_topic
)


def show_overall_progress(as_json: bool = False):
    """Display overall learning progress."""

    progress = load_global_progress()
    all_topics = load_all_topics()

    if as_json:
        print(json.dumps(progress, indent=2))
        return

    print("=== Overall Learning Progress ===\n")

    # Overall stats
    print(f"Last updated: {progress.get('last_updated', 'Never')}")
    print(f"Last study date: {progress.get('last_study_date', 'Never')}")
    print(f"Total sessions: {progress.get('total_sessions', 0)}")
    print(f"Total questions answered: {progress.get('total_questions_answered', 0)}")
    print(f"Overall accuracy: {progress.get('overall_accuracy', 0):.1f}%")
    print()

    # Topics by mastery
    mastery = progress.get('topics_by_mastery', {})
    total = progress.get('total_topics', 0)

    print("Topics by Mastery Level:")
    print(f"  New:       {mastery.get('new', 0):3d} ({mastery.get('new', 0)/total*100 if total > 0 else 0:.0f}%)")
    print(f"  Learning:  {mastery.get('learning', 0):3d} ({mastery.get('learning', 0)/total*100 if total > 0 else 0:.0f}%)")
    print(f"  Reviewing: {mastery.get('reviewing', 0):3d} ({mastery.get('reviewing', 0)/total*100 if total > 0 else 0:.0f}%)")
    print(f"  Mastered:  {mastery.get('mastered', 0):3d} ({mastery.get('mastered', 0)/total*100 if total > 0 else 0:.0f}%)")
    print(f"  Total:     {total:3d}")
    print()

    # Recent topics
    if all_topics:
        print("Recent Topics:")
        # Sort by last practiced date
        recent = sorted(
            [t for t in all_topics if t.get('last_practiced')],
            key=lambda x: x.get('last_practiced', ''),
            reverse=True
        )[:5]

        for topic in recent:
            last_attempt = topic['attempts'][-1] if topic.get('attempts') else None
            if last_attempt:
                accuracy = (last_attempt['score'] / last_attempt['total'] * 100
                           if last_attempt['total'] > 0 else 0)
                print(f"  {topic['title']} ({topic['topic_id']})")
                print(f"    Last: {topic['last_practiced']} - {accuracy:.0f}% - {topic['mastery_level']}")


def show_topic_progress(topic_id: str, as_json: bool = False):
    """Display detailed progress for a specific topic."""

    topic = load_topic(topic_id)

    if not topic:
        print(f"Error: Topic {topic_id} not found.")
        sys.exit(1)

    if as_json:
        print(json.dumps(topic, indent=2))
        return

    print(f"=== Topic Progress: {topic['title']} ===\n")

    print(f"Topic ID: {topic['topic_id']}")
    print(f"Description: {topic.get('description', 'N/A')}")
    print(f"Source: {topic.get('source_material', 'N/A')}")
    if topic.get('source_reference'):
        print(f"Reference: {topic['source_reference']}")
    print(f"Tags: {', '.join(topic.get('tags', [])) or 'None'}")
    print()

    print(f"Mastery Level: {topic['mastery_level']}")
    print(f"Created: {topic.get('created_date', 'Unknown')}")
    print(f"Last Practiced: {topic.get('last_practiced', 'Never')}")
    print(f"Next Review: {topic.get('next_review', 'Not scheduled')}")
    print(f"SRS Interval: {topic.get('srs_interval_days', 0)} days")
    print()

    # Attempt history
    attempts = topic.get('attempts', [])

    if attempts:
        print(f"Attempt History ({len(attempts)} total):\n")

        # Calculate statistics
        total_questions = sum(a['total'] for a in attempts)
        total_correct = sum(a['score'] for a in attempts)
        overall_accuracy = (total_correct / total_questions * 100
                           if total_questions > 0 else 0)

        print(f"  Total questions: {total_questions}")
        print(f"  Total correct: {total_correct}")
        print(f"  Overall accuracy: {overall_accuracy:.1f}%")
        print()

        # Recent attempts
        print("  Recent Attempts:")
        for i, attempt in enumerate(reversed(attempts[-5:]), 1):
            accuracy = (attempt['score'] / attempt['total'] * 100
                       if attempt['total'] > 0 else 0)
            print(f"    {len(attempts) - i + 1}. {attempt['date']}: "
                  f"{attempt['score']}/{attempt['total']} ({accuracy:.0f}%) - "
                  f"{attempt['status']}")

        # Progress trend
        if len(attempts) >= 3:
            recent_scores = [
                a['score'] / a['total'] if a['total'] > 0 else 0
                for a in attempts[-3:]
            ]
            trend = sum(recent_scores) / len(recent_scores)

            print()
            print(f"  Recent trend (last 3 attempts): {trend*100:.1f}%")

            if trend >= 0.9:
                print("  📈 Excellent! You've mastered this topic.")
            elif trend >= 0.8:
                print("  ✓ Good progress! Keep reviewing to maintain mastery.")
            elif trend >= 0.6:
                print("  ⚠️ Improving. Focus on weak areas.")
            else:
                print("  📚 Needs more practice. Review the material carefully.")
    else:
        print("No attempts yet. This topic has not been practiced.")


def main():
    topic_id = None
    as_json = False

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--topic' and i + 1 < len(sys.argv):
            topic_id = sys.argv[i + 1]
            i += 2
        elif arg == '--json':
            as_json = True
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python view_progress.py [--topic TOPIC_ID] [--json]")
            sys.exit(1)

    if topic_id:
        show_topic_progress(topic_id, as_json)
    else:
        show_overall_progress(as_json)


if __name__ == "__main__":
    main()
