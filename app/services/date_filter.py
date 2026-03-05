"""
Date filtering module for removing specific dates from optimized prompts.

This module provides functions to detect and replace specific dates with
fuzzy time expressions to keep prompts reusable over time.
"""
import re
from typing import Tuple

# Date patterns to detect
DATE_PATTERNS = [
    # ISO format: 2026-03-05, 2026/03/05
    r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
    # US format: 03/05/2026, March 5, 2026
    r'\b\d{1,2}/\d{1,2}/\d{4}\b',
    # Month names: March 5, 2026, 5 March 2026
    r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\b',
    # Chinese date format: 2026年3月5日, 3月5日
    r'\b\d{4}年\d{1,2}月\d{1,2}日\b',
    r'\b\d{1,2}月\d{1,2}日\b',
    # Relative dates that are too specific: 3 days ago, 2 weeks ago
    r'\b\d+\s+(?:days?|weeks?|months?|years?)\s+ago\b',
    # Today, yesterday, tomorrow
    r'\b(?:today|yesterday|tomorrow)\b',
    # Day of week with date: Friday March 5
    r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?:day)?,\s+\w+\s+\d{1,2}\b',
]

# Specific year replacements
REPLACEMENTS = {
    '2026': '今年',
    '2025': '去年',
    '2024': '前年',
}

# Fuzzy replacements (convert specific to general)
FUZZY_REPLACEMENTS = [
    (r'最近\s*\d+\s*天', '最近几天'),
    (r'本周', '最近一周'),
    (r'上周', '最近一周'),
    (r'本月', '最近一个月'),
    # Note: '今年' is intentionally excluded - it's used as a year replacement target
    (r'\d+\s*天前', '最近几天'),
    (r'\d+\s*周前', '最近几周'),
    (r'\d+\s*个月前', '最近几个月'),
    (r'\d+\s*月前', '最近几个月'),
]


def contains_specific_date(text: str) -> bool:
    """
    Check if text contains specific dates.

    Args:
        text: The text to check

    Returns:
        True if specific dates are found, False otherwise
    """
    for pattern in DATE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def replace_dates_with_fuzzy(text: str) -> Tuple[str, int]:
    """
    Replace specific dates with fuzzy time expressions.

    Args:
        text: The text to process

    Returns:
        Tuple of (processed_text, number_of_replacements)
    """
    processed = text
    replacements_count = 0

    # Step 1: Apply specific year replacements FIRST (before general date patterns)
    for specific, fuzzy in REPLACEMENTS.items():
        pattern = specific + r'年'
        replacement = fuzzy  # Don't add "年" to replacement
        if pattern in processed:
            count = processed.count(pattern)
            processed = processed.replace(pattern, replacement)
            replacements_count += count

    # Step 2: Apply fuzzy replacements for relative dates
    for specific_pattern, fuzzy_replacement in FUZZY_REPLACEMENTS:
        matches = re.findall(specific_pattern, processed)
        if matches:
            processed = re.sub(specific_pattern, fuzzy_replacement, processed)
            replacements_count += len(matches)

    # Step 3: Apply date pattern replacements (most specific first)
    # Chinese full date (must come before short date)
    if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', processed):
        matches = re.findall(r'\d{4}年\d{1,2}月\d{1,2}日', processed)
        if matches:
            processed = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日', '最近', processed)
            replacements_count += len(matches)

    # Chinese short date
    if re.search(r'\d{1,2}月\d{1,2}日', processed):
        matches = re.findall(r'\d{1,2}月\d{1,2}日', processed)
        if matches:
            processed = re.sub(r'\d{1,2}月\d{1,2}日', '最近', processed)
            replacements_count += len(matches)

    # ISO format dates
    iso_patterns = [
        (r'\d{4}-\d{1,2}-\d{1,2}', '最近'),
        (r'\d{4}/\d{1,2}/\d{1,2}', '最近'),
        (r'\d{1,2}/\d{1,2}/\d{4}', '最近'),
    ]
    for pattern, replacement in iso_patterns:
        matches = re.findall(pattern, processed)
        if matches:
            processed = re.sub(pattern, replacement, processed)
            replacements_count += len(matches)

    # English month names
    month_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?'
    if re.search(month_pattern, processed, re.IGNORECASE):
        matches = re.findall(month_pattern, processed, re.IGNORECASE)
        if matches:
            processed = re.sub(month_pattern, '最近', processed, flags=re.IGNORECASE)
            replacements_count += len(matches)

    # Step 4: Apply English specific day replacements
    english_replacements = {
        r'\btoday\b': '今天',
        r'\byesterday\b': '最近',
        r'\btomorrow\b': '最近',
        r'\d+\s+days?\s+ago': '最近几天',
        r'\d+\s+weeks?\s+ago': '最近几周',
        r'\d+\s+months?\s+ago': '最近几个月',
    }

    for pattern, replacement in english_replacements.items():
        matches = re.findall(pattern, processed, re.IGNORECASE)
        if matches:
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
            replacements_count += len(matches)

    return processed, replacements_count


def get_date_constraint_instruction() -> str:
    """
    Get instruction text to add to LLM system prompt.

    Returns:
        Instruction string warning against using specific dates
    """
    return """
**CRITICAL CONTENT CONSTRAINT - NO SPECIFIC DATES:**
- DO NOT include specific dates like "2026-03-05", "March 5, 2026", "2026年3月5日"
- DO NOT use expressions like "today", "yesterday", "tomorrow", "3 days ago"
- INSTEAD use fuzzy time expressions:
  * Use "最近" (recent/latest) for general time references
  * Use "最近一周" (last week/recent week) for week ranges
  * Use "最近几天" (recent days) for day ranges
  * Use "最新" (latest) for most recent information
  * Use "当前" (current) for present time references

The optimized prompt should remain valid and reusable over time without becoming outdated.
"""
