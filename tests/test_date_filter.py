"""
Unit tests for date filtering functionality.
"""
import pytest
from app.services.date_filter import contains_specific_date, replace_dates_with_fuzzy


def test_contains_specific_date():
    """Test date detection."""
    # ISO format
    assert contains_specific_date("2026-03-05") == True
    assert contains_specific_date("2026/03/05") == True

    # US format
    assert contains_specific_date("03/05/2026") == True
    assert contains_specific_date("March 5, 2026") == True

    # Chinese format
    assert contains_specific_date("2026年3月5日") == True
    assert contains_specific_date("3月5日") == True

    # Relative dates
    assert contains_specific_date("3 days ago") == True
    assert contains_specific_date("2 weeks ago") == True

    # Specific days
    assert contains_specific_date("today") == True
    assert contains_specific_date("yesterday") == True
    assert contains_specific_date("tomorrow") == True

    # No dates
    assert contains_specific_date("最近几天") == False
    assert contains_specific_date("最新数据") == False
    assert contains_specific_date("使用最新的AI技术") == False


def test_replace_dates_with_fuzzy_iso_format():
    """Test date replacement for ISO format."""
    # Test ISO format
    text1 = "使用2026-03-05的数据进行分析"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "2026-03-05" not in result1
    assert "最近" in result1
    assert count1 > 0

    # Test ISO format with slashes
    text2 = "2026/03/05的统计报告"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "2026/03/05" not in result2
    assert "最近" in result2
    assert count2 > 0


def test_replace_dates_with_fuzzy_chinese_format():
    """Test date replacement for Chinese format."""
    # Test full Chinese date
    text1 = "截至2026年3月5日的统计"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "2026年3月5日" not in result1
    assert "最近" in result1
    assert count1 > 0

    # Test short Chinese date
    text2 = "3月5日的天气情况"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "3月5日" not in result2
    assert "最近" in result2
    assert count2 > 0


def test_replace_dates_with_fuzzy_relative_dates():
    """Test date replacement for relative dates."""
    # Test "X days ago"
    text1 = "3天前的数据"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "3天前" not in result1
    assert "最近几天" in result1
    assert count1 > 0

    # Test "X weeks ago"
    text2 = "2周前的趋势"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "2周前" not in result2
    assert "最近几周" in result2
    assert count2 > 0

    # Test "X months ago"
    text3 = "6个月前的报告"
    result3, count3 = replace_dates_with_fuzzy(text3)
    assert "6个月前" not in result3
    assert "最近几个月" in result3
    assert count3 > 0


def test_replace_dates_with_fuzzy_specific_days():
    """Test date replacement for specific days."""
    # Test today
    text1 = "today's meeting"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "today" not in result1
    assert "今天" in result1
    assert count1 > 0

    # Test yesterday
    text2 = "yesterday's data"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "yesterday" not in result2
    assert "最近" in result2
    assert count2 > 0

    # Test tomorrow
    text3 = "tomorrow's forecast"
    result3, count3 = replace_dates_with_fuzzy(text3)
    assert "tomorrow" not in result3
    assert "最近" in result3
    assert count3 > 0


def test_replace_dates_with_fuzzy_year_replacements():
    """Test year-specific replacements."""
    # Test 2026 -> 今年
    text1 = "2026年的发展计划"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "2026年" not in result1
    assert "今年" in result1
    assert count1 > 0

    # Test 2025 -> 去年
    text2 = "回顾2025年的成绩"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "2025年" not in result2
    assert "去年" in result2
    assert count2 > 0

    # Test 2024 -> 前年
    text3 = "2024年的项目"
    result3, count3 = replace_dates_with_fuzzy(text3)
    assert "2024年" not in result3
    assert "前年" in result3
    assert count3 > 0


def test_replace_dates_with_fuzzy_week_month_replacements():
    """Test week and month replacements."""
    # Test 本周 -> 最近一周
    text1 = "本周的销售额"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "本周" not in result1
    assert "最近一周" in result1
    assert count1 > 0

    # Test 上周 -> 最近一周
    text2 = "上周的数据"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "上周" not in result2
    assert "最近一周" in result2
    assert count2 > 0

    # Test 本月 -> 最近一个月
    text3 = "本月的统计"
    result3, count3 = replace_dates_with_fuzzy(text3)
    assert "本月" not in result3
    assert "最近一个月" in result3
    assert count3 > 0


def test_replace_dates_no_replacement_needed():
    """Test that text without dates remains unchanged."""
    # Text with no specific dates
    text1 = "使用最新的数据进行处理"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert result1 == text1
    assert count1 == 0

    # Text with fuzzy expressions already
    text2 = "最近一周的统计数据"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert result2 == text2
    assert count2 == 0

    # Text with current/present references
    text3 = "当前的市场趋势"
    result3, count3 = replace_dates_with_fuzzy(text3)
    assert result3 == text3
    assert count3 == 0


def test_replace_dates_multiple_dates():
    """Test replacement of multiple dates in one text."""
    text = "从2026-03-01到2026-03-05的数据分析，对比3天前的结果"
    result, count = replace_dates_with_fuzzy(text)

    # All specific dates should be replaced
    assert "2026-03-01" not in result
    assert "2026-03-05" not in result
    assert "3天前" not in result

    # Should have fuzzy expressions
    assert "最近" in result

    # Should have made multiple replacements
    assert count >= 3


def test_replace_dates_preserves_content():
    """Test that replacement preserves non-date content."""
    text = "根据2026年3月5日的报告，人工智能领域的投资增长了50%，达到100亿美元"
    result, count = replace_dates_with_fuzzy(text)

    # Date should be replaced
    assert "2026年3月5日" not in result

    # Content should be preserved
    assert "人工智能领域的投资增长了50%" in result
    assert "达到100亿美元" in result
    assert count > 0


def test_replace_dates_case_insensitive():
    """Test that replacement works regardless of case."""
    # Test uppercase
    text1 = "TODAY's meeting"
    result1, count1 = replace_dates_with_fuzzy(text1)
    assert "TODAY" not in result1.upper()
    assert "今天" in result1
    assert count1 > 0

    # Test mixed case
    text2 = "Today's weather"
    result2, count2 = replace_dates_with_fuzzy(text2)
    assert "Today" not in result2
    assert "今天" in result2
    assert count2 > 0
