#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
screenshot_manager.py - UNIBOS Screenshot Management System
Handles automatic detection, archiving and analysis of screenshots
"""

import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# Import logger
try:
    from unibos_logger import logger, LogCategory
except ImportError:
    # Fallback if logger not available
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def debug(msg, **kwargs): print(f"DEBUG: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")
    
    class LogCategory:
        SYSTEM = "system"

class ScreenshotManager:
    """Manages screenshot detection, archiving and analysis"""
    
    def __init__(self, base_path: str = None):
        """Initialize screenshot manager"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.archive_base = self.base_path / "archive" / "media" / "screenshots"
        # Dynamic folder selection based on version
        self.current_folder = None
        
        # Screenshot patterns
        self.ss_patterns = [
            r'\.png$', r'\.jpg$', r'\.jpeg$',
            r'\.PNG$', r'\.JPG$', r'\.JPEG$'
        ]
        
        # Combined pattern for grep
        self.grep_pattern = r'\.(png|jpg|jpeg|PNG|JPG|JPEG)$'
        
    def get_current_version(self) -> str:
        """Get current version from VERSION.json"""
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', 'v000')
            return 'v000'
        except Exception as e:
            logger.error(f"Failed to get version: {str(e)}", category=LogCategory.SYSTEM)
            return 'v000'
    
    def get_build_number(self) -> str:
        """Get current build number"""
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('build_number', datetime.now().strftime('%Y%m%d_%H%M'))
            return datetime.now().strftime('%Y%m%d_%H%M')
        except:
            return datetime.now().strftime('%Y%m%d_%H%M')
    
    def find_screenshots(self) -> List[Path]:
        """Find all screenshots in main directory"""
        screenshots = []
        try:
            # Extended patterns for various screenshot formats
            image_extensions = ['.png', '.PNG', '.jpg', '.JPG', '.jpeg', '.JPEG', '.gif', '.GIF', '.bmp', '.BMP']
            
            # Keywords that identify screenshots
            screenshot_keywords = [
                'Screenshot', 'screenshot', 'SCREENSHOT',
                'Screen Shot', 'screen shot',
                'Ekran', 'ekran', 'EKRAN',
                'PHOTO', 'Photo', 'photo',
                'IMG', 'img', 'Img',
                'Image', 'image', 'IMAGE',
                'Capture', 'capture', 'CAPTURE',
                'Snap', 'snap', 'SNAP',
                'unibos', 'UNIBOS', 'Unibos'
            ]
            
            # Use os.listdir for better handling of special characters
            import os
            for filename in os.listdir(self.base_path):
                full_path = self.base_path / filename
                
                # Check if it's a file with image extension
                if full_path.is_file() and any(filename.endswith(ext) for ext in image_extensions):
                    # Check if it matches any keyword pattern OR is any image file
                    if any(keyword in filename for keyword in screenshot_keywords) or True:  # Accept all images
                        if full_path not in screenshots:
                            screenshots.append(full_path)
                            logger.debug(f"Found screenshot/image: {filename}", category=LogCategory.SYSTEM)
            
            # Sort by modification time (newest first)
            screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if screenshots:
                logger.info(f"Found {len(screenshots)} screenshot(s) in main directory", 
                          category=LogCategory.SYSTEM)
                for ss in screenshots:
                    logger.debug(f"  - {ss.name}", category=LogCategory.SYSTEM)
            
            return screenshots
        except Exception as e:
            logger.error(f"Error finding screenshots: {str(e)}", category=LogCategory.SYSTEM)
            return []
    
    def generate_archive_name(self, original_path: Path, index: int = 1) -> str:
        """Generate archive name for screenshot"""
        version = self.get_current_version()
        build = self.get_build_number()
        
        # Extract timestamp from filename if possible
        match = re.search(r'(\d{4}-\d{2}-\d{2})\s+at\s+(\d{2})\.(\d{2})\.(\d{2})', original_path.name)
        if match:
            date = match.group(1).replace('-', '')
            hour = match.group(2)
            minute = match.group(3)
            timestamp = f"{date}_{hour}{minute}"
        else:
            # Use current timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Generate name: unibos_vXXX_YYYYMMDD_HHMM_N.png (NO build keyword)
        archive_name = f"unibos_{version}_{timestamp}_{index}.png"
        
        return archive_name
    
    def analyze_screenshot_content(self, screenshot_path: Path) -> str:
        """Analyze screenshot content and generate description"""
        try:
            # Get basic info
            file_size = screenshot_path.stat().st_size / 1024  # KB
            
            # Analyze filename for clues
            filename = screenshot_path.name.lower()
            
            # Content hints based on filename patterns
            content_hints = []
            
            if 'error' in filename or 'hata' in filename:
                content_hints.append("Hata mesajı içeriği")
            elif 'menu' in filename or 'menü' in filename:
                content_hints.append("Menü görüntüsü")
            elif 'test' in filename:
                content_hints.append("Test sonucu")
            elif 'bug' in filename:
                content_hints.append("Bug/sorun gösterimi")
            elif 'feature' in filename or 'özellik' in filename:
                content_hints.append("Yeni özellik gösterimi")
            elif 'ui' in filename or 'interface' in filename:
                content_hints.append("Kullanıcı arayüzü")
            elif 'terminal' in filename or 'console' in filename:
                content_hints.append("Terminal/konsol çıktısı")
            elif 'dev' in filename or 'tools' in filename:
                content_hints.append("Dev tools görüntüsü")
            elif 'claude' in filename:
                content_hints.append("Claude önerileri/menüsü")
            else:
                # Default content based on size
                if file_size < 100:
                    content_hints.append("Küçük boyutlu görsel")
                elif file_size < 500:
                    content_hints.append("Orta boyutlu ekran görüntüsü")
                else:
                    content_hints.append("Büyük boyutlu detaylı görüntü")
            
            # Generate content description
            content_desc = " - ".join(content_hints) if content_hints else "Genel ekran görüntüsü"
            
            # Log content analysis
            logger.info(f"Screenshot içerik analizi: {screenshot_path.name} => {content_desc}", 
                      category=LogCategory.SYSTEM)
            
            return content_desc
            
        except Exception as e:
            logger.error(f"Screenshot içerik analizi hatası: {str(e)}", 
                       category=LogCategory.SYSTEM)
            return "Analiz edilemedi"
    
    def archive_screenshot(self, screenshot_path: Path) -> Optional[Path]:
        """Archive a single screenshot"""
        try:
            # FORCED RULE: Analyze content BEFORE archiving
            content_desc = self.analyze_screenshot_content(screenshot_path)
            # Determine correct folder based on version number
            version = self.get_current_version()
            version_num = int(version[1:])  # Remove 'v' prefix
            
            if version_num <= 99:
                folder = "v001-099"
            elif version_num <= 199:
                folder = "v100-199"
            elif version_num <= 299:
                folder = "v200-299"
            else:
                folder = f"v{(version_num // 100) * 100:03d}-{((version_num // 100) + 1) * 100 - 1:03d}"
            
            # Ensure archive directory exists
            archive_dir = self.archive_base / folder
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Find next available index
            index = 1
            while True:
                archive_name = self.generate_archive_name(screenshot_path, index)
                archive_path = archive_dir / archive_name
                if not archive_path.exists():
                    break
                index += 1
            
            # Move file - handle spaces in filenames
            try:
                # First check if file really exists
                if not screenshot_path.exists():
                    # Try with absolute path
                    abs_path = screenshot_path.absolute()
                    if not abs_path.exists():
                        # Log detailed error information
                        logger.error(f"Screenshot file not found at: {screenshot_path}", category=LogCategory.SYSTEM)
                        logger.error(f"Absolute path tried: {abs_path}", category=LogCategory.SYSTEM)
                        logger.error(f"Working directory: {Path.cwd()}", category=LogCategory.SYSTEM)
                        
                        # List files in directory to debug
                        import os
                        files_in_dir = [f for f in os.listdir(self.base_path) if f.endswith(('.png', '.PNG', '.jpg', '.JPG'))]
                        logger.error(f"PNG/JPG files in directory: {files_in_dir}", category=LogCategory.SYSTEM)
                        
                        raise FileNotFoundError(f"Screenshot file not found: {screenshot_path}")
                
                # Use shutil.move with absolute paths
                src_path = str(screenshot_path.absolute())
                dst_path = str(archive_path.absolute())
                
                logger.debug(f"Moving file from: {src_path}", category=LogCategory.SYSTEM)
                logger.debug(f"Moving file to: {dst_path}", category=LogCategory.SYSTEM)
                
                shutil.move(src_path, dst_path)
                logger.debug(f"File moved successfully", category=LogCategory.SYSTEM)
                
            except Exception as e:
                logger.error(f"Failed to move file: {str(e)}", category=LogCategory.SYSTEM)
                # Try alternative method using os.rename
                try:
                    import os
                    os.rename(str(screenshot_path), str(archive_path))
                    logger.info(f"File moved using os.rename", category=LogCategory.SYSTEM)
                except Exception as e2:
                    logger.error(f"os.rename also failed: {str(e2)}", category=LogCategory.SYSTEM)
                    raise
            
            # Create content description file
            desc_file = archive_path.with_suffix('.txt')
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(f"Screenshot: {archive_name}\n")
                f.write(f"Original: {screenshot_path.name}\n")
                f.write(f"İçerik: {content_desc}\n")
                f.write(f"Arşiv Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Versiyon: {version}\n")
                f.write(f"Boyut: {screenshot_path.stat().st_size / 1024:.1f} KB\n")
            
            logger.info(f"Archived screenshot: {screenshot_path.name} -> {archive_name} [{content_desc}]", 
                      category=LogCategory.SYSTEM)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to archive screenshot {screenshot_path.name}: {str(e)}", 
                       category=LogCategory.SYSTEM)
            # Despite the error, check if file was actually moved
            if archive_path.exists():
                logger.info(f"File was successfully moved despite error message", category=LogCategory.SYSTEM)
                return archive_path
            return None
    
    def check_and_archive_all(self) -> Tuple[int, List[Path]]:
        """Check for screenshots and archive them all"""
        screenshots = self.find_screenshots()
        archived_paths = []
        
        for ss in screenshots:
            archived_path = self.archive_screenshot(ss)
            if archived_path:
                archived_paths.append(archived_path)
        
        return len(screenshots), archived_paths
    
    def get_recent_archives(self, limit: int = 5) -> List[Path]:
        """Get recently archived screenshots"""
        try:
            # Determine current folder if not set
            if not self.current_folder:
                version = self.get_current_version()
                version_num = int(version[1:])
                if version_num <= 99:
                    self.current_folder = "v001-099"
                elif version_num <= 199:
                    self.current_folder = "v100-199"
                elif version_num <= 299:
                    self.current_folder = "v200-299"
                else:
                    self.current_folder = f"v{(version_num // 100) * 100:03d}-{((version_num // 100) + 1) * 100 - 1:03d}"
            
            archive_dir = self.archive_base / self.current_folder
            if not archive_dir.exists():
                return []
            
            # Get all PNG files
            archives = list(archive_dir.glob("*.png"))
            
            # Sort by modification time (newest first)
            archives.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return archives[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent archives: {str(e)}", category=LogCategory.SYSTEM)
            return []
    
    def get_archive_info(self) -> dict:
        """Get information about archived screenshots"""
        try:
            # Determine current folder if not set
            if not self.current_folder:
                version = self.get_current_version()
                version_num = int(version[1:])
                if version_num <= 99:
                    self.current_folder = "v001-099"
                elif version_num <= 199:
                    self.current_folder = "v100-199"
                elif version_num <= 299:
                    self.current_folder = "v200-299"
                else:
                    self.current_folder = f"v{(version_num // 100) * 100:03d}-{((version_num // 100) + 1) * 100 - 1:03d}"
            
            info = {
                'current_folder': self.current_folder,
                'archive_path': str(self.archive_base / self.current_folder),
                'total_archives': 0,
                'recent_archives': []
            }
            
            archive_dir = self.archive_base / self.current_folder
            if archive_dir.exists():
                archives = list(archive_dir.glob("*.png"))
                info['total_archives'] = len(archives)
                
                # Get last 5 archives
                recent = self.get_recent_archives(5)
                info['recent_archives'] = [str(p.name) for p in recent]
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting archive info: {str(e)}", category=LogCategory.SYSTEM)
            return {}
    
    def scan_archived_screenshots(self, version_filter: str = None, limit: int = 10) -> List[dict]:
        """Scan and analyze archived screenshots
        
        Args:
            version_filter: Optional version filter (e.g. 'v331' or 'v300-v350')
            limit: Maximum number of screenshots to return (default: 10)
            
        Returns:
            List of dictionaries containing screenshot info and analysis
        """
        try:
            results = []
            
            # Determine folders to scan
            folders_to_scan = []
            
            if version_filter:
                # Parse version filter
                if '-' in version_filter:
                    # Range filter like 'v300-v350'
                    start_v, end_v = version_filter.split('-')
                    start_num = int(start_v.strip()[1:])
                    end_num = int(end_v.strip()[1:])
                    
                    # Add all relevant folders
                    for folder in self.archive_base.iterdir():
                        if folder.is_dir() and folder.name.startswith('v'):
                            # Parse folder range
                            match = re.match(r'v(\d+)-(\d+)', folder.name)
                            if match:
                                folder_start = int(match.group(1))
                                folder_end = int(match.group(2))
                                # Check if folder overlaps with requested range
                                if not (folder_end < start_num or folder_start > end_num):
                                    folders_to_scan.append(folder)
                else:
                    # Single version filter like 'v331'
                    version_num = int(version_filter[1:])
                    # Find correct folder
                    if version_num <= 99:
                        folder_name = "v001-099"
                    elif version_num <= 199:
                        folder_name = "v100-199"
                    elif version_num <= 299:
                        folder_name = "v200-299"
                    else:
                        folder_name = f"v{(version_num // 100) * 100:03d}-{((version_num // 100) + 1) * 100 - 1:03d}"
                    
                    folder_path = self.archive_base / folder_name
                    if folder_path.exists():
                        folders_to_scan.append(folder_path)
            else:
                # No filter - scan current folder
                version = self.get_current_version()
                version_num = int(version[1:])
                if version_num <= 99:
                    folder_name = "v001-099"
                elif version_num <= 199:
                    folder_name = "v100-199"
                elif version_num <= 299:
                    folder_name = "v200-299"
                else:
                    folder_name = f"v{(version_num // 100) * 100:03d}-{((version_num // 100) + 1) * 100 - 1:03d}"
                
                folder_path = self.archive_base / folder_name
                if folder_path.exists():
                    folders_to_scan.append(folder_path)
            
            # Collect all screenshots from folders
            all_screenshots = []
            for folder in folders_to_scan:
                screenshots = list(folder.glob("*.png"))
                screenshots.extend(list(folder.glob("*.jpg")))
                screenshots.extend(list(folder.glob("*.jpeg")))
                
                for ss in screenshots:
                    # Extract version from filename
                    match = re.match(r'unibos_(v\d+)_.*', ss.name)
                    if match:
                        ss_version = match.group(1)
                        # Apply version filter if specified
                        if version_filter:
                            if '-' in version_filter:
                                # Range check
                                ss_num = int(ss_version[1:])
                                if ss_num < start_num or ss_num > end_num:
                                    continue
                            else:
                                # Exact match
                                if ss_version != version_filter:
                                    continue
                    
                    all_screenshots.append(ss)
            
            # Sort by modification time (newest first)
            all_screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Analyze and collect info for requested number
            for ss in all_screenshots[:limit]:
                info = {
                    'path': str(ss),
                    'name': ss.name,
                    'folder': ss.parent.name,
                    'size_kb': ss.stat().st_size / 1024,
                    'modified': datetime.fromtimestamp(ss.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'content': None,
                    'version': None,
                    'build': None
                }
                
                # Extract version and build from filename
                match = re.match(r'unibos_(v\d+)_(\d+_\d+)_(\d+)\.png', ss.name)
                if match:
                    info['version'] = match.group(1)
                    info['build'] = match.group(2)
                
                # Check for content description file
                desc_file = ss.with_suffix('.txt')
                if desc_file.exists():
                    try:
                        with open(desc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract content line
                            for line in content.splitlines():
                                if line.startswith('İçerik:'):
                                    info['content'] = line.split(':', 1)[1].strip()
                                    break
                    except:
                        pass
                
                # If no content description, analyze filename
                if not info['content']:
                    info['content'] = self.analyze_screenshot_content(ss)
                
                results.append(info)
            
            # Log summary
            logger.info(f"Scanned {len(results)} archived screenshots from {len(folders_to_scan)} folder(s)", 
                      category=LogCategory.SYSTEM)
            
            return results
            
        except Exception as e:
            logger.error(f"Error scanning archived screenshots: {str(e)}", category=LogCategory.SYSTEM)
            return []
    
    def display_archived_screenshots(self, version_filter: str = None, limit: int = 10):
        """Display archived screenshots in a formatted table"""
        screenshots = self.scan_archived_screenshots(version_filter, limit)
        
        if not screenshots:
            print("No archived screenshots found")
            return
        
        print(f"\n📸 Archived Screenshots Analysis")
        print("=" * 100)
        
        # Header
        print(f"{'Version':<8} {'Build':<15} {'Size (KB)':<10} {'Content':<40} {'Modified':<20}")
        print("-" * 100)
        
        # Rows
        for ss in screenshots:
            version = ss.get('version', 'N/A') or 'N/A'
            build = ss.get('build', 'N/A') or 'N/A'
            size = f"{ss['size_kb']:.1f}"
            content_str = ss.get('content', 'Unknown') or 'Unknown'
            content = content_str[:37] + "..." if len(content_str) > 40 else content_str
            modified = ss['modified']
            
            print(f"{version:<8} {build:<15} {size:<10} {content:<40} {modified:<20}")
        
        print("-" * 100)
        print(f"Total: {len(screenshots)} screenshots displayed")
        
        # Show path info
        if screenshots:
            first_ss = screenshots[0]
            folder_path = Path(first_ss['path']).parent
            print(f"\nArchive location: {folder_path}")
    
    def get_latest_archived_screenshots(self, count: int = 5) -> List[Path]:
        """Get the latest archived screenshots across all folders"""
        try:
            all_screenshots = []
            
            # Scan all archive folders
            if self.archive_base.exists():
                for folder in self.archive_base.iterdir():
                    if folder.is_dir() and folder.name.startswith('v'):
                        screenshots = list(folder.glob("*.png"))
                        screenshots.extend(list(folder.glob("*.jpg")))
                        screenshots.extend(list(folder.glob("*.jpeg")))
                        all_screenshots.extend(screenshots)
            
            # Sort by modification time (newest first)
            all_screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return all_screenshots[:count]
            
        except Exception as e:
            logger.error(f"Error getting latest archived screenshots: {str(e)}", category=LogCategory.SYSTEM)
            return []

# Singleton instance
screenshot_manager = ScreenshotManager()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        print("Checking for screenshots...")
        # Set base path explicitly
        screenshot_manager.base_path = Path.cwd()
        print(f"Base path: {screenshot_manager.base_path}")
        
        count, archived = screenshot_manager.check_and_archive_all()
        if count > 0:
            print(f"\nArchived {count} screenshot(s) successfully:")
            for path in archived:
                print(f"  ✓ {path.name}")
        else:
            print("\nNo screenshots found in main directory")
            # Debug: list all PNG files
            import os
            png_files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if png_files:
                print(f"\nFound {len(png_files)} image files:")
                for f in png_files[:5]:  # Show first 5
                    print(f"  - {f}")
                if len(png_files) > 5:
                    print(f"  ... and {len(png_files) - 5} more")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "info":
        info = screenshot_manager.get_archive_info()
        print(f"Archive info:")
        print(f"  Path: {info.get('archive_path', 'N/A')}")
        print(f"  Total: {info.get('total_archives', 0)} screenshots")
        if info.get('recent_archives'):
            print("  Recent:")
            for name in info['recent_archives']:
                print(f"    - {name}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "scan":
        # Scan archived screenshots
        version_filter = None
        limit = 10
        
        # Parse additional arguments
        for i in range(2, len(sys.argv)):
            if sys.argv[i].startswith('v'):
                version_filter = sys.argv[i]
            elif sys.argv[i].isdigit():
                limit = int(sys.argv[i])
        
        print(f"Scanning archived screenshots...")
        if version_filter:
            print(f"  Version filter: {version_filter}")
        print(f"  Limit: {limit}")
        
        screenshot_manager.display_archived_screenshots(version_filter, limit)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "latest":
        # Show latest archived screenshots
        count = 10
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            count = int(sys.argv[2])
        
        print(f"Latest {count} archived screenshots:")
        latest = screenshot_manager.get_latest_archived_screenshots(count)
        
        for i, ss in enumerate(latest, 1):
            # Extract version from filename
            match = re.match(r'unibos_(v\d+)_.*', ss.name)
            version = match.group(1) if match else 'N/A'
            size_kb = ss.stat().st_size / 1024
            modified = datetime.fromtimestamp(ss.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{i:2}. {version:<6} {ss.name:<50} {size_kb:>8.1f} KB  {modified}")
    
    else:
        print("Usage:")
        print("  python screenshot_manager.py check         - Check and archive screenshots")
        print("  python screenshot_manager.py info          - Show archive information")
        print("  python screenshot_manager.py scan [vXXX] [limit] - Scan archived screenshots")
        print("    Examples:")
        print("      python screenshot_manager.py scan          - Scan current version folder")
        print("      python screenshot_manager.py scan v331     - Scan screenshots from v331")
        print("      python screenshot_manager.py scan v320-v330 20 - Scan v320-v330, show 20")
        print("  python screenshot_manager.py latest [count] - Show latest archived screenshots")