#!/usr/bin/env python
"""Test script for Phase 1 formatting implementation"""

import sys
sys.path.insert(0, 'D:/Projects/AI Projects/Slide-Text-Extractor')

from process_slides import _format_text_with_structure

# Test cases
test_cases = [
    # Test 1: Bullet points
    {
        'input': ['• First bullet point', '• Second bullet point', '• Third point'],
        'name': 'Bullet Points'
    },
    # Test 2: Numbered list
    {
        'input': ['1. First item', '2. Second item', '3. Third item'],
        'name': 'Numbered List'
    },
    # Test 3: Mixed content
    {
        'input': ['INTRODUCTION', 'This is a paragraph.', '• Bullet one', '• Bullet two', '1. Number one'],
        'name': 'Mixed Content'
    },
    # Test 4: Continuing text
    {
        'input': ['This is the first line of a', 'paragraph that continues across', 'multiple lines.'],
        'name': 'Continuing Paragraphs'
    }
]

print("=" * 60)
print("Phase 1: Enhanced Output Formatting - Test Results")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['name']}")
    print("-" * 60)
    print("Input lines:")
    for line in test['input']:
        print(f"  - '{line}'")
    print("\nFormatted output:")
    result = _format_text_with_structure(test['input'])
    print(result)
    print()

print("=" * 60)
print("All tests completed!")
print("=" * 60)
