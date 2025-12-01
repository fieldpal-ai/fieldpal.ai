#!/usr/bin/env python3
"""
Script to replace absolute URLs with relative paths in index.html
"""

import re
import sys

def fix_urls(file_path):
    """Replace absolute URLs with relative paths"""
    
    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    replacements = 0
    
    # Pattern 1: Replace https://fieldpal.riverstone.marketing/demo/ with /
    pattern1 = r'https?://fieldpal\.riverstone\.marketing/demo/'
    matches1 = len(re.findall(pattern1, content))
    content = re.sub(pattern1, '/', content)
    replacements += matches1
    print(f"  Replaced {matches1} instances of https://fieldpal.riverstone.marketing/demo/")
    
    # Pattern 2: Replace http://fieldpal.riverstone.marketing/demo (without trailing slash) with /
    pattern2 = r'http://fieldpal\.riverstone\.marketing/demo(?!/)'
    matches2 = len(re.findall(pattern2, content))
    content = re.sub(pattern2, '/', content)
    replacements += matches2
    print(f"  Replaced {matches2} instances of http://fieldpal.riverstone.marketing/demo")
    
    # Pattern 3: Fix wp-content paths that might have been affected
    # These should already be relative after pattern1, but let's make sure
    pattern3 = r'/wp-content/'
    # Count how many are already relative (don't start with http)
    # We'll leave these as is since they're already relative after pattern1
    
    # Pattern 4: Replace specific page links that don't exist with anchors or home
    # /about-us -> #about-us (or / if no anchor exists)
    # /contact -> #contact (or / if no anchor exists)
    # These are already handled by pattern1, but we can make them more specific
    
    # Write the file
    print(f"\nWriting updated file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Done! Made {replacements} replacements")
    print(f"   Original size: {original_length:,} bytes")
    print(f"   New size: {len(content):,} bytes")
    
    return replacements

if __name__ == "__main__":
    file_path = "index.html"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    try:
        fix_urls(file_path)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)



