#!/usr/bin/env python3
"""
Query which topics should be practiced today based on spaced repetition.

Usage:
    python what_to_practice.py [--limit N] [--json]

Options:
    --limit N    Return at most N topics (default: 10)
    --json       Output as JSON instead of human-readable format

Examples:
    python what_to_practice.py
    python what_to_practice.py --limit 5
    python what_to_practice.py --json
"""

import sys
import json
from datetime import datetime
from learning_data import load_all_topics


def get_topics_due_for_review(limit: int = 10) -> list:
    """
    Get topics that are due for review based on spaced repetition.

    Returns list of topics sorted by priority:
    1. Overdue topics (past next_review date)
    2. New topics (never practiced)
    3. Topics due today

    Args:
        limit: Maximum number of topics to return

    Returns:
        List of topic dictionaries with priority scores
    """
    all_topics = load_all_topics()
    today = datetime.now().strftime("%Y-%m-%d")

    prioritized_topics = []

    for topic in all_topics:
        next_review = topic.get('next_review')
        mastery_level = topic.get('mastery_level', 'new')
        last_practiced = topic.get('last_practiced')

        # Calculate priority score (lower = higher priority)
        priority = 0

        if mastery_level == 'new':
            # New topics: medium priority
            priority = 2
        elif next_review:
            # Compare dates
            if next_review <= today:
                # Overdue or due today
                days_overdue = (
                    datetime.strptime(today, "%Y-%m-%d") -
                    datetime.strptime(next_review, "%Y-%m-%d")
                ).days
                priority = 1 - (days_overdue * 0.1)  # More overdue = higher priority
            else:
                # Not due yet
                priority = 10
        else:
            # No next review set (shouldn't happen, but handle it)
            priority = 3

        # Boost priority for topics marked as needs_review
        if topic.get('attempts'):
            last_attempt = topic['attempts'][-1]
            if last_attempt.get('status') == 'needs_review':
                priority -= 0.5

        prioritized_topics.append({
            'topic': topic,
            'priority': priority,
            'days_until_review': (
                (datetime.strptime(next_review, "%Y-%m-%d") -
                 datetime.strptime(today, "%Y-%m-%d")).days
                if next_review else None
            )
        })

    # Sort by priority (lower = higher priority)
    prioritized_topics.sort(key=lambda x: x['priority'])

    # Return top N topics
    return prioritized_topics[:limit]


def format_human_readable(topics_data: list) -> str:
    """Format topics for human-readable output."""

    if not topics_data:
        return "✓ No topics due for review today! Great job staying on track."

    output = ["=== Topics to Practice Today ===\n"]

    for i, item in enumerate(topics_data, 1):
        topic = item['topic']
        days_until = item['days_until_review']

        output.append(f"{i}. {topic['title']} ({topic['topic_id']})")
        output.append(f"   Mastery: {topic['mastery_level']}")

        if topic.get('attempts'):
            last_attempt = topic['attempts'][-1]
            accuracy = (last_attempt['score'] / last_attempt['total'] * 100
                       if last_attempt['total'] > 0 else 0)
            output.append(f"   Last attempt: {last_attempt['date']} - "
                         f"{last_attempt['score']}/{last_attempt['total']} ({accuracy:.0f}%)")
        else:
            output.append("   Status: Never practiced")

        if days_until is not None:
            if days_until < 0:
                output.append(f"   ⚠️  OVERDUE by {abs(days_until)} days")
            elif days_until == 0:
                output.append("   📅 Due TODAY")
            else:
                output.append(f"   Next review in {days_until} days")

        if topic.get('source_material'):
            output.append(f"   Source: {topic['source_material']}")

        output.append("")

    return "\n".join(output)


def format_json(topics_data: list) -> str:
    """Format topics as JSON."""

    topics_list = []
    for item in topics_data:
        topic = item['topic']
        topics_list.append({
            'topic_id': topic['topic_id'],
            'title': topic['title'],
            'description': topic.get('description', ''),
            'mastery_level': topic['mastery_level'],
            'next_review': topic.get('next_review'),
            'days_until_review': item['days_until_review'],
            'last_practiced': topic.get('last_practiced'),
            'source_material': topic.get('source_material', ''),
            'tags': topic.get('tags', [])
        })

    return json.dumps({
        'date': datetime.now().strftime("%Y-%m-%d"),
        'topics_due': len(topics_list),
        'topics': topics_list
    }, indent=2)


def main():
    limit = 10
    output_json = False

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--limit' and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("Error: --limit requires a number")
                sys.exit(1)
        elif arg == '--json':
            output_json = True
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python what_to_practice.py [--limit N] [--json]")
            sys.exit(1)

    # Get topics
    topics_data = get_topics_due_for_review(limit)

    # Output
    if output_json:
        print(format_json(topics_data))
    else:
        print(format_human_readable(topics_data))


if __name__ == "__main__":
    main()
