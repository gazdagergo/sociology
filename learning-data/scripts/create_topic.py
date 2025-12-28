#!/usr/bin/env python3
"""
Create a new topic for tracking.

Usage:
    python create_topic.py "Topic Title" "Description" [source_material] [tags]

Examples:
    python create_topic.py "Socialization Theories" "Primary and secondary socialization" "materials/sociology/textbook.pdf" "socialization,theories"
    python create_topic.py "Social Structure" "Macro-level social organization"
"""

import sys
from datetime import datetime
from learning_data import (
    get_next_topic_id,
    save_topic,
    load_srs_config
)


def create_topic(
    title: str,
    description: str,
    source_material: str = "",
    source_reference: str = "",
    tags: list = None
) -> dict:
    """Create a new topic record."""

    topic_id = get_next_topic_id()
    srs_config = load_srs_config()

    topic_data = {
        "topic_id": topic_id,
        "title": title,
        "description": description,
        "source_material": source_material,
        "source_reference": source_reference,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "attempts": [],
        "last_practiced": None,
        "next_review": datetime.now().strftime("%Y-%m-%d"),  # Available immediately
        "srs_interval_days": srs_config['intervals']['initial'],
        "mastery_level": "new",
        "tags": tags or []
    }

    save_topic(topic_data)
    return topic_data


def main():
    if len(sys.argv) < 3:
        print("Usage: python create_topic.py <title> <description> [source_material] [tags]")
        print("\nExamples:")
        print('  python create_topic.py "Socialization" "Theory of socialization" "textbook.pdf" "theory,socialization"')
        sys.exit(1)

    title = sys.argv[1]
    description = sys.argv[2]
    source_material = sys.argv[3] if len(sys.argv) > 3 else ""
    tags = sys.argv[4].split(',') if len(sys.argv) > 4 else []

    topic = create_topic(title, description, source_material, tags=tags)

    print(f"✓ Created topic: {topic['topic_id']}")
    print(f"  Title: {topic['title']}")
    print(f"  Description: {topic['description']}")
    if source_material:
        print(f"  Source: {topic['source_material']}")
    if tags:
        print(f"  Tags: {', '.join(tags)}")
    print(f"  Next review: {topic['next_review']}")


if __name__ == "__main__":
    main()
