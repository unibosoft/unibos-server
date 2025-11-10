#!/usr/bin/env python3
"""
Documents Module Functions
All functionality for the documents menu items
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Color definitions
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_ORANGE = "\033[48;5;208m"


def clear_screen():
    """Clear the screen"""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def wait_for_key():
    """Wait for any key press"""
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        input()
        return ''


def browse_documents():
    """Browse and manage documents"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}📁 Browse Documents{Colors.RESET}")
    print("=" * 60)
    
    # Use the invoice directory as primary, with fallback
    primary_dir = Path("/Users/berkhatirli/Desktop/unibos/berk_claude_file_pool_DONT_DELETE/input/kesilen_faturalar")
    fallback_dir = Path.home() / "Documents" / "unibos_documents"
    
    if primary_dir.exists():
        docs_dir = primary_dir
    else:
        docs_dir = fallback_dir
        docs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{Colors.CYAN}Document Directory:{Colors.RESET} {docs_dir}")
    print(f"\n{Colors.BOLD}Files:{Colors.RESET}")
    print("-" * 40)
    
    # List all files
    files = list(docs_dir.glob("*"))
    if not files:
        print(f"{Colors.DIM}No documents found{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Tip: Upload documents using option 3{Colors.RESET}")
    else:
        for i, file in enumerate(files[:20], 1):  # Show first 20
            size = file.stat().st_size / 1024  # KB
            modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            
            # File type icon
            icon = "📄"
            if file.suffix.lower() == '.pdf':
                icon = "📕"
            elif file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                icon = "🖼️"
            elif file.suffix.lower() in ['.doc', '.docx']:
                icon = "📝"
            elif file.suffix.lower() in ['.xls', '.xlsx']:
                icon = "📊"
            
            print(f"{i:2}. {icon} {file.name[:40]:<40} {size:>8.1f} KB  {modified}")
    
    print("\n" + "-" * 60)
    print(f"Total: {len(files)} documents")
    
    print(f"\n{Colors.DIM}Press any key to return...{Colors.RESET}")
    wait_for_key()


def search_documents():
    """Full-text document search"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 Search Documents{Colors.RESET}")
    print("=" * 60)
    
    print(f"\n{Colors.CYAN}Enter search query:{Colors.RESET} ", end='')
    sys.stdout.flush()
    
    # Get search query
    query = input().strip()
    
    if not query:
        print(f"{Colors.YELLOW}No search query provided{Colors.RESET}")
        time.sleep(2)
        return
    
    print(f"\n{Colors.YELLOW}Searching for: '{query}'...{Colors.RESET}")
    
    # Search in both directories
    primary_dir = Path("/Users/berkhatirli/Desktop/unibos/berk_claude_file_pool_DONT_DELETE/input/kesilen_faturalar")
    fallback_dir = Path.home() / "Documents" / "unibos_documents"
    
    docs_dir = primary_dir if primary_dir.exists() else fallback_dir
    results = []
    
    # Search in filenames and content (simplified)
    for file in docs_dir.glob("*"):
        # Check filename
        if query.lower() in file.name.lower():
            results.append((file, "filename match"))
            continue
        
        # Check content for text files
        if file.suffix.lower() in ['.txt', '.md', '.json', '.csv']:
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append((file, "content match"))
            except:
                pass
    
    print(f"\n{Colors.BOLD}Search Results:{Colors.RESET}")
    print("-" * 40)
    
    if not results:
        print(f"{Colors.DIM}No documents found matching '{query}'{Colors.RESET}")
    else:
        for i, (file, match_type) in enumerate(results[:10], 1):
            print(f"{i:2}. {file.name} ({Colors.GREEN}{match_type}{Colors.RESET})")
    
    print(f"\n{Colors.DIM}Press any key to return...{Colors.RESET}")
    wait_for_key()


def upload_documents():
    """Upload new documents"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}📤 Upload Documents{Colors.RESET}")
    print("=" * 60)
    
    print(f"\n{Colors.CYAN}Enter source file path:{Colors.RESET} ", end='')
    sys.stdout.flush()
    
    source_path = input().strip()
    
    if not source_path:
        print(f"{Colors.YELLOW}No path provided{Colors.RESET}")
        time.sleep(2)
        return
    
    source = Path(source_path).expanduser()
    
    if not source.exists():
        print(f"{Colors.RED}File not found: {source_path}{Colors.RESET}")
        time.sleep(2)
        return
    
    # Copy to documents directory
    docs_dir = Path.home() / "Documents" / "unibos_documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    dest = docs_dir / source.name
    
    try:
        shutil.copy2(source, dest)
        print(f"{Colors.GREEN}✓ Document uploaded successfully!{Colors.RESET}")
        print(f"  Saved to: {dest}")
    except Exception as e:
        print(f"{Colors.RED}Upload failed: {e}{Colors.RESET}")
    
    time.sleep(3)


def ocr_scanner():
    """OCR Scanner for images"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}📸 OCR Scanner{Colors.RESET}")
    print("=" * 60)
    
    try:
        import pytesseract
        from PIL import Image
        ocr_available = True
    except ImportError:
        ocr_available = False
    
    if not ocr_available:
        print(f"\n{Colors.YELLOW}OCR dependencies not installed{Colors.RESET}")
        print("\nTo enable OCR, install:")
        print("  pip install pytesseract pillow")
        print("  brew install tesseract (on macOS)")
        print("  sudo apt-get install tesseract-ocr (on Linux)")
        
        print(f"\n{Colors.DIM}Press any key to return...{Colors.RESET}")
        wait_for_key()
        return
    
    print(f"\n{Colors.CYAN}Enter image file path:{Colors.RESET} ", end='')
    sys.stdout.flush()
    
    image_path = input().strip()
    
    if not image_path:
        print(f"{Colors.YELLOW}No path provided{Colors.RESET}")
        time.sleep(2)
        return
    
    image_file = Path(image_path).expanduser()
    
    if not image_file.exists():
        print(f"{Colors.RED}Image not found: {image_path}{Colors.RESET}")
        time.sleep(2)
        return
    
    print(f"\n{Colors.YELLOW}Processing OCR...{Colors.RESET}")
    
    try:
        # Open image
        img = Image.open(image_file)
        
        # Perform OCR
        text = pytesseract.image_to_string(img, lang='eng+tur')
        
        print(f"\n{Colors.BOLD}Extracted Text:{Colors.RESET}")
        print("-" * 40)
        print(text[:1000])  # Show first 1000 chars
        
        if len(text) > 1000:
            print(f"\n{Colors.DIM}... (truncated, {len(text)} total characters){Colors.RESET}")
        
        # Save to file
        output_file = image_file.with_suffix('.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\n{Colors.GREEN}✓ Text saved to: {output_file}{Colors.RESET}")
        
    except Exception as e:
        print(f"{Colors.RED}OCR failed: {e}{Colors.RESET}")
    
    print(f"\n{Colors.DIM}Press any key to return...{Colors.RESET}")
    wait_for_key()


def tag_manager():
    """Manage document tags"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}🏷️ Tag Manager{Colors.RESET}")
    print("=" * 60)
    
    # Tags database file
    tags_file = Path.home() / "Documents" / "unibos_documents" / ".tags.json"
    
    # Load existing tags
    tags_db = {}
    if tags_file.exists():
        try:
            with open(tags_file, 'r') as f:
                tags_db = json.load(f)
        except:
            tags_db = {}
    
    print(f"\n{Colors.BOLD}Tag Statistics:{Colors.RESET}")
    print("-" * 40)
    
    # Count tags
    all_tags = {}
    for file_tags in tags_db.values():
        for tag in file_tags:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    
    if not all_tags:
        print(f"{Colors.DIM}No tags defined yet{Colors.RESET}")
    else:
        # Sort by frequency
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:10]:
            bar = "█" * min(count * 2, 40)
            print(f"  {tag:<20} {bar} ({count})")
    
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print("  1. Add tags to document")
    print("  2. Remove tags from document")
    print("  3. View documents by tag")
    print("  4. Back")
    
    print(f"\n{Colors.CYAN}Select option:{Colors.RESET} ", end='')
    sys.stdout.flush()
    
    choice = input().strip()
    
    if choice == '1':
        # Add tags
        print(f"\n{Colors.CYAN}Enter document name:{Colors.RESET} ", end='')
        sys.stdout.flush()
        doc_name = input().strip()
        
        print(f"{Colors.CYAN}Enter tags (comma-separated):{Colors.RESET} ", end='')
        sys.stdout.flush()
        tags = [t.strip() for t in input().split(',')]
        
        if doc_name and tags:
            if doc_name not in tags_db:
                tags_db[doc_name] = []
            tags_db[doc_name].extend(tags)
            tags_db[doc_name] = list(set(tags_db[doc_name]))  # Remove duplicates
            
            # Save
            with open(tags_file, 'w') as f:
                json.dump(tags_db, f, indent=2)
            
            print(f"{Colors.GREEN}✓ Tags added successfully{Colors.RESET}")
            time.sleep(2)
    
    elif choice == '3':
        # View by tag
        print(f"\n{Colors.CYAN}Enter tag to search:{Colors.RESET} ", end='')
        sys.stdout.flush()
        search_tag = input().strip()
        
        if search_tag:
            print(f"\n{Colors.BOLD}Documents with tag '{search_tag}':{Colors.RESET}")
            found = False
            for doc, doc_tags in tags_db.items():
                if search_tag in doc_tags:
                    print(f"  • {doc}")
                    found = True
            
            if not found:
                print(f"{Colors.DIM}No documents found with this tag{Colors.RESET}")
            
            print(f"\n{Colors.DIM}Press any key to continue...{Colors.RESET}")
            wait_for_key()


def document_analytics():
    """Document statistics and analytics"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}📊 Document Analytics{Colors.RESET}")
    print("=" * 60)
    
    # Use the invoice directory as primary
    primary_dir = Path("/Users/berkhatirli/Desktop/unibos/berk_claude_file_pool_DONT_DELETE/input/kesilen_faturalar")
    fallback_dir = Path.home() / "Documents" / "unibos_documents"
    
    if primary_dir.exists():
        docs_dir = primary_dir
    else:
        docs_dir = fallback_dir
        docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Gather statistics
    files = list(docs_dir.glob("*"))
    
    # File type statistics
    file_types = {}
    total_size = 0
    
    for file in files:
        if file.is_file():
            ext = file.suffix.lower() or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file.stat().st_size
    
    print(f"\n{Colors.BOLD}Overview:{Colors.RESET}")
    print(f"  Total documents: {len(files)}")
    print(f"  Total size: {total_size / (1024*1024):.2f} MB")
    print(f"  Average size: {(total_size / len(files) / 1024) if files else 0:.1f} KB")
    
    print(f"\n{Colors.BOLD}File Types:{Colors.RESET}")
    print("-" * 40)
    
    if file_types:
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:10]:
            percentage = (count / len(files)) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {ext:<15} {bar:<20} {count:3} ({percentage:.1f}%)")
    else:
        print(f"{Colors.DIM}No files found{Colors.RESET}")
    
    # Recent activity
    print(f"\n{Colors.BOLD}Recent Activity:{Colors.RESET}")
    print("-" * 40)
    
    if files:
        # Sort by modification time
        recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        for file in recent_files:
            modified = datetime.fromtimestamp(file.stat().st_mtime)
            time_ago = datetime.now() - modified
            
            if time_ago.days > 0:
                ago_str = f"{time_ago.days} days ago"
            elif time_ago.seconds > 3600:
                ago_str = f"{time_ago.seconds // 3600} hours ago"
            else:
                ago_str = f"{time_ago.seconds // 60} minutes ago"
            
            print(f"  • {file.name[:40]:<40} ({ago_str})")
    
    # Storage usage
    print(f"\n{Colors.BOLD}Storage Usage:{Colors.RESET}")
    print("-" * 40)
    
    # Get disk usage
    try:
        import shutil
        total, used, free = shutil.disk_usage(docs_dir)
        
        usage_percent = (used / total) * 100
        docs_percent = (total_size / total) * 100 if total_size > 0 else 0
        
        print(f"  Disk usage: {usage_percent:.1f}%")
        print(f"  Documents usage: {docs_percent:.4f}% of total disk")
        print(f"  Free space: {free / (1024**3):.1f} GB")
    except:
        print(f"{Colors.DIM}Disk usage information not available{Colors.RESET}")
    
    print(f"\n{Colors.DIM}Press any key to return...{Colors.RESET}")
    wait_for_key()


# Export functions
__all__ = [
    'browse_documents',
    'search_documents', 
    'upload_documents',
    'ocr_scanner',
    'tag_manager',
    'document_analytics'
]