"""
Enhanced Archive Analyzer with History and Anomaly Detection
"""

import os
import sys
import glob
import json
import time
import statistics
import threading
from datetime import datetime
from pathlib import Path


class ArchiveAnalyzerMenu:
    """Enhanced archive analyzer with submenu and history"""
    
    def __init__(self, content_x, lines, cols):
        self.content_x = content_x
        self.lines = lines
        self.cols = cols
        self.content_width = cols - content_x - 2
        self.history_file = "/Users/berkhatirli/Desktop/unibos/archive/.analyzer_history.json"
        self.selected_index = 0
        self.menu_options = [
            ("new_scan", "🔍 new scan", "start a fresh archive analysis"),
            ("previous_scans", "📜 previous scans", "view last 5 scan results"),
            ("anomaly_detection", "🔎 anomaly detection", "run advanced anomaly analysis"),
            ("back", "← back", "return to version manager")
        ]
        
    def show_menu(self):
        """Display the archive analyzer submenu"""
        from main import Colors, move_cursor, get_single_key, hide_cursor, show_cursor
        
        # Clear content area
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        def draw_menu():
            """Draw menu options"""
            y = 5
            
            # Title
            move_cursor(self.content_x + 2, y)
            sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}📊 archive analyzer{Colors.RESET}")
            y += 3
            
            # Menu options
            for i, (key, title, desc) in enumerate(self.menu_options):
                move_cursor(self.content_x + 4, y)
                
                if i == self.selected_index:
                    # Selected item
                    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD} {title} {Colors.RESET}")
                    move_cursor(self.content_x + 6, y + 1)
                    sys.stdout.write(f"{Colors.DIM}{desc}{Colors.RESET}")
                else:
                    # Normal item
                    sys.stdout.write(f"{Colors.WHITE}{title}{Colors.RESET}")
                    move_cursor(self.content_x + 6, y + 1)
                    sys.stdout.write(f"{Colors.DIM}{desc}{Colors.RESET}")
                
                y += 3
            
            # Instructions
            move_cursor(self.content_x + 4, self.lines - 6)
            sys.stdout.write(f"{Colors.DIM}↑↓ navigate | enter select | q back{Colors.RESET}")
            sys.stdout.flush()
        
        hide_cursor()
        draw_menu()
        
        while True:
            key = get_single_key()
            
            if key == '\x1b[A' or key == 'UP':  # Up arrow
                if self.selected_index > 0:
                    self.selected_index -= 1
                    draw_menu()
            elif key == '\x1b[B' or key == 'DOWN':  # Down arrow
                if self.selected_index < len(self.menu_options) - 1:
                    self.selected_index += 1
                    draw_menu()
            elif key == '\r' or key == 'ENTER':  # Enter
                selected_key = self.menu_options[self.selected_index][0]
                
                if selected_key == "new_scan":
                    self.run_new_scan()
                elif selected_key == "previous_scans":
                    self.show_previous_scans()
                elif selected_key == "anomaly_detection":
                    self.run_anomaly_detection()
                elif selected_key == "back":
                    show_cursor()
                    return
                    
                # After action, redraw menu
                draw_menu()
            elif key == 'q' or key == 'Q':  # Q to quit
                show_cursor()
                return
    
    def run_new_scan(self):
        """Run a new archive scan and save to history"""
        from main import version_archive_analyzer
        
        # Run the original analyzer
        scan_result = self.perform_scan()
        
        # Save to history
        self.save_scan_to_history(scan_result)
        
        # Show results
        self.display_scan_results(scan_result)
    
    def perform_scan(self):
        """Perform the actual scan"""
        from main import Colors, move_cursor
        
        archive_path = "/Users/berkhatirli/Desktop/unibos/archive/versions"
        archives = []
        
        # Clear and show scanning message
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        move_cursor(self.content_x + 2, 5)
        sys.stdout.write(f"{Colors.CYAN}📊 scanning archives...{Colors.RESET}")
        
        # Get all version directories
        version_dirs = sorted(glob.glob(f"{archive_path}/unibos_v*"))
        total_dirs = len(version_dirs)
        
        for idx, version_dir in enumerate(version_dirs):
            if os.path.isdir(version_dir):
                # Update progress
                move_cursor(self.content_x + 2, 7)
                progress = (idx + 1) / total_dirs
                progress_bar = int(30 * progress)
                sys.stdout.write(f"[{'█' * progress_bar}{'░' * (30 - progress_bar)}] {idx + 1}/{total_dirs}")
                sys.stdout.flush()
                
                dirname = os.path.basename(version_dir)
                parts = dirname.split('_')
                
                if len(parts) >= 2:
                    version_num = parts[1][1:] if parts[1].startswith('v') else parts[1]
                    
                    # Calculate size and file count
                    total_size = 0
                    file_count = 0
                    for dirpath, dirnames, filenames in os.walk(version_dir):
                        file_count += len(filenames)
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except:
                                pass
                    
                    archives.append({
                        'version': version_num,
                        'path': version_dir,
                        'size': total_size,
                        'size_mb': total_size / (1024 * 1024),
                        'name': dirname,
                        'file_count': file_count
                    })
        
        # Calculate statistics
        if archives:
            sizes = [a['size'] for a in archives]
            mean_size = statistics.mean(sizes)
            stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
            
            # Calculate Z-scores
            for archive in archives:
                if stdev_size > 0:
                    archive['z_score'] = (archive['size'] - mean_size) / stdev_size
                else:
                    archive['z_score'] = 0
                
                # Mark anomalies
                archive['is_anomaly'] = abs(archive['z_score']) > 2
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_archives': len(archives),
            'archives': archives,
            'stats': {
                'mean_size_mb': mean_size / (1024 * 1024) if archives else 0,
                'stdev_size_mb': stdev_size / (1024 * 1024) if archives else 0,
                'anomaly_count': sum(1 for a in archives if a.get('is_anomaly', False))
            }
        }
    
    def save_scan_to_history(self, scan_result):
        """Save scan results to history file"""
        # Load existing history
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add new scan (keep only last 5)
        history.insert(0, scan_result)
        history = history[:5]
        
        # Save back
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def show_previous_scans(self):
        """Display previous scan results"""
        from main import Colors, move_cursor, get_single_key
        
        # Load history
        if not os.path.exists(self.history_file):
            move_cursor(self.content_x + 2, 10)
            sys.stdout.write(f"{Colors.YELLOW}no previous scans found{Colors.RESET}")
            move_cursor(self.content_x + 2, 12)
            sys.stdout.write(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
            sys.stdout.flush()
            get_single_key()
            return
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
        
        if not history:
            move_cursor(self.content_x + 2, 10)
            sys.stdout.write(f"{Colors.YELLOW}no previous scans found{Colors.RESET}")
            move_cursor(self.content_x + 2, 12)
            sys.stdout.write(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
            sys.stdout.flush()
            get_single_key()
            return
        
        # Clear and display history
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        y = 5
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}📜 previous scans{Colors.RESET}")
        y += 3
        
        for i, scan in enumerate(history):
            if i >= 5:
                break
                
            timestamp = datetime.fromisoformat(scan['timestamp'])
            move_cursor(self.content_x + 4, y)
            sys.stdout.write(f"{Colors.YELLOW}{i+1}.{Colors.RESET} {timestamp.strftime('%Y-%m-%d %H:%M')}")
            y += 1
            
            move_cursor(self.content_x + 6, y)
            sys.stdout.write(f"{Colors.DIM}archives: {scan['total_archives']} | ")
            sys.stdout.write(f"anomalies: {scan['stats']['anomaly_count']} | ")
            sys.stdout.write(f"avg size: {scan['stats']['mean_size_mb']:.1f} mb{Colors.RESET}")
            y += 2
        
        move_cursor(self.content_x + 2, self.lines - 6)
        sys.stdout.write(f"{Colors.DIM}enter number to view details | q to go back{Colors.RESET}")
        sys.stdout.flush()
        
        # Wait for selection
        key = get_single_key()
        if key.isdigit() and 1 <= int(key) <= min(5, len(history)):
            self.display_scan_results(history[int(key) - 1])
    
    def display_scan_results(self, scan_result):
        """Display detailed scan results"""
        from main import Colors, move_cursor, get_single_key
        
        # Clear and show results
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        y = 5
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}📊 scan results{Colors.RESET}")
        y += 2
        
        # Summary
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"total archives: {Colors.GREEN}{scan_result['total_archives']}{Colors.RESET}")
        y += 1
        
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"anomalies detected: {Colors.YELLOW}{scan_result['stats']['anomaly_count']}{Colors.RESET}")
        y += 1
        
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"average size: {Colors.CYAN}{scan_result['stats']['mean_size_mb']:.1f} mb{Colors.RESET}")
        y += 2
        
        # Show anomalies
        if scan_result['stats']['anomaly_count'] > 0:
            move_cursor(self.content_x + 2, y)
            sys.stdout.write(f"{Colors.YELLOW}anomalies found:{Colors.RESET}")
            y += 1
            
            for archive in scan_result['archives']:
                if archive.get('is_anomaly'):
                    move_cursor(self.content_x + 4, y)
                    z_score = archive['z_score']
                    color = Colors.RED if abs(z_score) > 3 else Colors.YELLOW
                    sys.stdout.write(f"{color}• v{archive['version']}: {archive['size_mb']:.1f} mb (z={z_score:.2f}){Colors.RESET}")
                    y += 1
                    
                    if y >= self.lines - 6:
                        break
        
        move_cursor(self.content_x + 2, self.lines - 4)
        sys.stdout.write(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        sys.stdout.flush()
        get_single_key()
    
    def run_anomaly_detection(self):
        """Run advanced anomaly detection using Claude agent"""
        from main import Colors, move_cursor, get_single_key
        
        # Clear screen
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        move_cursor(self.content_x + 2, 5)
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}🔎 anomaly detection agent{Colors.RESET}")
        
        move_cursor(self.content_x + 2, 8)
        sys.stdout.write(f"{Colors.YELLOW}launching claude-powered anomaly analysis...{Colors.RESET}")
        sys.stdout.flush()
        
        # Create and run the anomaly detection agent
        from archive_anomaly_agent import ArchiveAnomalyAgent
        
        agent = ArchiveAnomalyAgent()
        move_cursor(self.content_x + 2, 10)
        sys.stdout.write(f"{Colors.DIM}analyzing archive patterns...{Colors.RESET}")
        sys.stdout.flush()
        
        results = agent.analyze()
        
        # Display results
        self.display_anomaly_results(results)
    
    def display_anomaly_results(self, results):
        """Display anomaly detection results"""
        from main import Colors, move_cursor, get_single_key
        
        # Clear and show results
        for y in range(3, self.lines - 2):
            move_cursor(self.content_x, y)
            sys.stdout.write('\033[K')
        
        y = 5
        move_cursor(self.content_x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}🔎 anomaly analysis results{Colors.RESET}")
        y += 3
        
        if results:
            for key, value in results.items():
                if y >= self.lines - 6:
                    break
                    
                move_cursor(self.content_x + 2, y)
                sys.stdout.write(f"{Colors.YELLOW}{key}:{Colors.RESET} {value}")
                y += 1
        else:
            move_cursor(self.content_x + 2, y)
            sys.stdout.write(f"{Colors.GREEN}no anomalies detected{Colors.RESET}")
        
        move_cursor(self.content_x + 2, self.lines - 4)
        sys.stdout.write(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        sys.stdout.flush()
        get_single_key()


def enhanced_archive_analyzer(content_x, lines, cols):
    """Entry point for enhanced archive analyzer"""
    menu = ArchiveAnalyzerMenu(content_x, lines, cols)
    menu.show_menu()