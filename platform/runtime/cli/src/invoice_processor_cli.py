#!/usr/bin/env python3
"""
Invoice Processor CLI Module
============================
CLI interface for the invoice processing system.
Provides a terminal-based UI for processing invoices with OCR and AI.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil

# Import color definitions
try:
    from cli_context_manager import Colors
except ImportError:
    # Fallback color definitions
    class Colors:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        GRAY = "\033[90m"
        BG_CYAN = "\033[46m"


class InvoiceProcessorCLI:
    """CLI interface for invoice processing"""
    
    def __init__(self):
        # Set CLI mode to suppress logs
        os.environ['UNIBOS_CLI_MODE'] = '1'
        
        # Default to the invoice directory
        self.input_dir = "/Users/berkhatirli/Desktop/unibos/berk_claude_file_pool_DONT_DELETE/input/kesilen_faturalar"
        self.output_dir = "/Users/berkhatirli/Desktop/unibos/berk_claude_file_pool_DONT_DELETE/output"
        self.processor = None
        self.processing_active = False
        self.processed_files = []
        self.current_file = None
        self.progress = 0
        self.total_files = 0
        self.results = []
        self.errors = []
        self.selected_option = 0  # For arrow key navigation
        self.total_options = 6    # Total number of menu options (including back)
        
        # Try to import the processor
        self.init_processor()
    
    def init_processor(self):
        """Initialize the invoice processor"""
        try:
            # Try to import the perfect processor
            from invoice_processor_perfect import PerfectInvoiceProcessor
            self.processor = PerfectInvoiceProcessor()
            self.processor_available = True
        except ImportError:
            self.processor_available = False
            self.processor = None
    
    def render_main_menu(self, x: int, y: int, width: int, height: int):
        """Render the main invoice processor menu"""
        # First, clear from x=27 to handle any leftover characters from main CLI
        for row in range(y, min(y + height, 35)):
            sys.stdout.write(f"\033[{row};27H\033[K")
        
        # Then clear the actual content area properly
        self.clear_area(x, y, width, min(height, 35))
        sys.stdout.flush()  # Ensure clearing is complete
        
        # Title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}invoice processor{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        y_pos = y + 3
        
        # Status
        if not self.processor_available:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.RED}⚠ processor not available{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}install required packages first{Colors.RESET}")
            y_pos += 2
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}required packages:{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}• pdfplumber{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}• pytesseract{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}• pillow{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}• pdf2image{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}• requests{Colors.RESET}")
            return
        
        # Show current configuration
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}configuration:{Colors.RESET}")
        y_pos += 1
        
        # Input directory
        input_status = f"{Colors.GREEN}✓{Colors.RESET}" if self.input_dir else f"{Colors.RED}✗{Colors.RESET}"
        if self.input_dir and len(self.input_dir) > 45:
            input_path = "..." + self.input_dir[-42:]
        else:
            input_path = self.input_dir if self.input_dir else "not set"
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{input_status} input: {Colors.CYAN}{input_path}{Colors.RESET}")
        y_pos += 1
        
        # Output directory
        output_status = f"{Colors.GREEN}✓{Colors.RESET}" if self.output_dir else f"{Colors.RED}✗{Colors.RESET}"
        if self.output_dir and len(self.output_dir) > 45:
            output_path = "..." + self.output_dir[-42:]
        else:
            output_path = self.output_dir if self.output_dir else "not set"
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{output_status} output: {Colors.CYAN}{output_path}{Colors.RESET}")
        y_pos += 2
        
        # Options
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}options:{Colors.RESET}")
        y_pos += 1
        
        # Option 1: Set input directory
        option_text = "1. set input directory"
        if self.selected_option == 0:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
        else:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
        y_pos += 1
        
        # Option 2: Set output directory
        option_text = "2. set output directory"
        if self.selected_option == 1:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
        else:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
        y_pos += 1
        
        # Option 3: Scan for invoices
        option_text = "3. scan for invoices"
        if self.selected_option == 2:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
        else:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
        y_pos += 1
        
        # Option 4: Start processing (only if directories are set)
        if self.input_dir and self.output_dir:
            option_text = "4. start processing"
            if self.selected_option == 3:
                sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
            else:
                sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
            y_pos += 1
            self.total_options = 6  # Include processing option
        else:
            self.total_options = 5  # No processing option
        
        # Option 5: View results
        option_text = "5. view results"
        view_results_index = 4 if (self.input_dir and self.output_dir) else 3
        if self.selected_option == view_results_index:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
        else:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
        y_pos += 1
        
        # Option 6: Back to menu (always show, adjusted index)
        option_text = "q. back to menu"
        back_option_index = 5 if (self.input_dir and self.output_dir) else 4
        if self.selected_option == back_option_index:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}{Colors.CYAN}▶ {option_text}{Colors.RESET}")
        else:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}  {option_text}{Colors.RESET}")
        y_pos += 2
        
        # Show current status (limit y position)
        if y_pos < y + height - 5:
            if self.processing_active:
                self.render_progress(x, y_pos, width)
            elif self.results:
                sys.stdout.write(f"\033[{y_pos};{x}H{Colors.GREEN}last run: {len(self.results)} files processed{Colors.RESET}")
        
        # Show navigation hint at bottom of content area
        nav_y = min(y + height - 2, 38)
        sys.stdout.write(f"\033[{nav_y};{x}H{Colors.DIM}↑↓ navigate | enter/→ select | ← back | 1-5 direct{Colors.RESET}")
        
        sys.stdout.flush()
    
    def render_progress(self, x: int, y: int, width: int):
        """Render processing progress"""
        if self.total_files > 0:
            percent = int((self.progress / self.total_files) * 100)
            bar_width = min(40, width - 20)
            filled = int(bar_width * (self.progress / self.total_files))
            bar = "█" * filled + "░" * (bar_width - filled)
            
            sys.stdout.write(f"\033[{y};{x}H{Colors.YELLOW}processing:{Colors.RESET}")
            sys.stdout.write(f"\033[{y + 1};{x + 2}H{Colors.DIM}[{Colors.CYAN}{bar}{Colors.DIM}]{Colors.RESET} {percent}%")
            
            if self.current_file:
                filename = Path(self.current_file).name
                if len(filename) > width - 10:
                    filename = filename[:width - 13] + "..."
                sys.stdout.write(f"\033[{y + 2};{x + 2}H{Colors.DIM}→ {filename}{Colors.RESET}")
            
            sys.stdout.write(f"\033[{y + 3};{x + 2}H{Colors.DIM}{self.progress}/{self.total_files} files{Colors.RESET}")
    
    def render_results(self, x: int, y: int, width: int, height: int):
        """Render processing results"""
        self.clear_area(x, y, width, height)
        
        # Title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}processing results{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        y_pos = y + 3
        
        if not self.results:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}no results yet{Colors.RESET}")
            sys.stdout.write(f"\033[{y_pos + 2};{x}H{Colors.DIM}q: back to menu{Colors.RESET}")
            sys.stdout.flush()
            return
        
        # Summary
        total = len(self.results)
        successful = len([r for r in self.results if r.get('status') == 'success'])
        failed = total - successful
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}summary:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.GREEN}✓ successful: {successful}{Colors.RESET}")
        y_pos += 1
        if failed > 0:
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.RED}✗ failed: {failed}{Colors.RESET}")
            y_pos += 1
        y_pos += 1
        
        # Results table header
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}processed files:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}{'─' * min(60, width - 2)}{Colors.RESET}")
        y_pos += 1
        
        # Show recent results (limited by height)
        max_items = min(len(self.results), height - y_pos - 3)
        for i, result in enumerate(self.results[-max_items:]):
            if y_pos >= y + height - 2:
                break
                
            filename = Path(result.get('file', '')).name
            if len(filename) > 30:
                filename = filename[:27] + "..."
            
            status = result.get('status', 'unknown')
            if status == 'success':
                status_icon = f"{Colors.GREEN}✓{Colors.RESET}"
                data = result.get('data', {})
                amount = data.get('total_amount', 'n/a')
                info = f"amount: {amount}"
            else:
                status_icon = f"{Colors.RED}✗{Colors.RESET}"
                info = result.get('error', 'unknown error')[:20]
            
            sys.stdout.write(f"\033[{y_pos};{x}H{status_icon} {filename}")
            sys.stdout.write(f"\033[{y_pos};{x + 35}H{Colors.DIM}{info}{Colors.RESET}")
            y_pos += 1
        
        # Footer
        sys.stdout.write(f"\033[{y + height - 2};{x}H{Colors.DIM}q: back to menu  e: export results{Colors.RESET}")
        sys.stdout.flush()
    
    def clear_area(self, x: int, y: int, width: int, height: int):
        """Clear a specific area of the screen"""
        for row in range(y, min(y + height, 60)):
            # Move to position and clear entire line from that position to end
            sys.stdout.write(f"\033[{row};{x}H\033[K")
            # Write spaces to ensure area is clean
            sys.stdout.write(' ' * width)
        sys.stdout.flush()
    
    def set_input_directory(self):
        """Set the input directory for invoice files"""
        # Clear line and prompt
        sys.stdout.write("\033[25;1H\033[K")
        sys.stdout.write(f"{Colors.CYAN}enter input directory path: {Colors.RESET}")
        sys.stdout.flush()
        
        # Get input
        path = input().strip()
        if path:
            if os.path.exists(path) and os.path.isdir(path):
                self.input_dir = path
                return True, f"input directory set to: {path}"
            else:
                return False, "invalid directory path"
        return False, "no path provided"
    
    def set_output_directory(self):
        """Set the output directory for processed invoices"""
        # Clear line and prompt
        sys.stdout.write("\033[25;1H\033[K")
        sys.stdout.write(f"{Colors.CYAN}enter output directory path: {Colors.RESET}")
        sys.stdout.flush()
        
        # Get input
        path = input().strip()
        if path:
            # Create directory if it doesn't exist
            try:
                os.makedirs(path, exist_ok=True)
                self.output_dir = path
                return True, f"output directory set to: {path}"
            except Exception as e:
                return False, f"failed to create directory: {e}"
        return False, "no path provided"
    
    def scan_for_invoices(self):
        """Scan input directory for invoice files"""
        if not self.input_dir:
            return False, "input directory not set"
        
        try:
            # Find PDF files
            pdf_files = list(Path(self.input_dir).glob("*.pdf"))
            # Find image files
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']
            image_files = []
            for ext in image_extensions:
                image_files.extend(list(Path(self.input_dir).glob(ext)))
            
            total = len(pdf_files) + len(image_files)
            
            if total > 0:
                return True, f"found {total} files ({len(pdf_files)} pdfs, {len(image_files)} images)"
            else:
                return False, "no invoice files found"
        except Exception as e:
            return False, f"scan failed: {e}"
    
    def start_processing(self):
        """Start processing invoices in a background thread"""
        if not self.input_dir or not self.output_dir:
            return False, "directories not configured"
        
        if self.processing_active:
            return False, "processing already in progress"
        
        if not self.processor:
            return False, "processor not available"
        
        # Start processing in background
        self.processing_active = True
        self.results = []
        self.errors = []
        
        thread = threading.Thread(target=self.process_invoices)
        thread.daemon = True
        thread.start()
        
        return True, "processing started"
    
    def process_invoices(self):
        """Process all invoices in the input directory"""
        try:
            # Get all files
            files = []
            for ext in ['*.pdf', '*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']:
                files.extend(list(Path(self.input_dir).glob(ext)))
            
            self.total_files = len(files)
            self.progress = 0
            
            for file_path in files:
                self.current_file = str(file_path)
                
                try:
                    # Process the file - check if processor exists and has valid result
                    if self.processor and hasattr(self.processor, 'process_invoice'):
                        result = self.processor.process_invoice(str(file_path), self.output_dir)
                        
                        # Check if result is valid - process_invoice returns (success, filename/error)
                        if result and isinstance(result, tuple) and len(result) == 2:
                            success, output = result
                            
                            if success:
                                # Create result data
                                result_data = {
                                    'original': file_path.name,
                                    'processed': output,
                                    'success': True
                                }
                                
                                # Save result
                                output_file = Path(self.output_dir) / f"{file_path.stem}_result.json"
                                with open(output_file, 'w', encoding='utf-8') as f:
                                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                                
                                self.results.append({
                                    'file': str(file_path),
                                    'status': 'success',
                                    'data': result_data,
                                    'output': str(output_file)
                                })
                                
                                # Log success silently
                                pass  # print(f"✓ Success: {output}")
                            else:
                                # Processing failed
                                self.results.append({
                                    'file': str(file_path),
                                    'status': 'error',
                                    'error': output  # output contains error message
                                })
                                pass  # print(f"✗ Failed: {file_path.name}: {output}")
                        else:
                            # Invalid result
                            self.results.append({
                                'file': str(file_path),
                                'status': 'error',
                                'error': 'Invalid processing result format'
                            })
                    else:
                        # No processor available
                        self.results.append({
                            'file': str(file_path),
                            'status': 'error',
                            'error': 'Processor not available'
                        })
                    
                except Exception as e:
                    self.results.append({
                        'file': str(file_path),
                        'status': 'error',
                        'error': str(e)
                    })
                    self.errors.append(str(e))
                    pass  # print(f"✗ Error processing {file_path.name}: {str(e)[:50]}")
                
                self.progress += 1
                
                # Small delay to prevent UI flooding
                time.sleep(0.1)
                
        except Exception as e:
            self.errors.append(f"processing failed: {e}")
            pass  # print(f"✗ Processing failed: {e}")
        
        finally:
            self.processing_active = False
            self.current_file = None
            pass  # print(f"\n✓ Processing complete: {len(self.results)} files processed")
    
    def export_results(self):
        """Export results to a summary file"""
        if not self.results:
            return False, "no results to export"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = Path(self.output_dir) / f"invoice_summary_{timestamp}.json"
            
            summary = {
                'timestamp': timestamp,
                'input_dir': self.input_dir,
                'output_dir': self.output_dir,
                'total_processed': len(self.results),
                'successful': len([r for r in self.results if r.get('status') == 'success']),
                'failed': len([r for r in self.results if r.get('status') != 'success']),
                'results': self.results
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            return True, f"results exported to: {export_file.name}"
            
        except Exception as e:
            return False, f"export failed: {e}"


    def render_main_interface(self):
        """Render the main interface"""
        # Clear screen
        sys.stdout.write("\033[2J\033[H")
        
        # Title
        sys.stdout.write(f"\033[1;1H{Colors.BOLD}{Colors.CYAN}Invoice Processor{Colors.RESET}")
        sys.stdout.write(f"\033[2;1H{'=' * 60}")
        
        # Configuration
        y_pos = 4
        sys.stdout.write(f"\033[{y_pos};1H{Colors.YELLOW}Configuration:{Colors.RESET}")
        
        y_pos += 1
        # Input directory
        input_status = f"{Colors.GREEN}✓{Colors.RESET}" if self.input_dir else f"{Colors.RED}✗{Colors.RESET}"
        if self.input_dir and len(self.input_dir) > 45:
            input_path = "..." + self.input_dir[-42:]
        else:
            input_path = self.input_dir if self.input_dir else "not set"
        sys.stdout.write(f"\033[{y_pos};3H{input_status} Input: {Colors.CYAN}{input_path}{Colors.RESET}")
        
        y_pos += 1
        # Output directory
        output_status = f"{Colors.GREEN}✓{Colors.RESET}" if self.output_dir else f"{Colors.RED}✗{Colors.RESET}"
        if self.output_dir and len(self.output_dir) > 45:
            output_path = "..." + self.output_dir[-42:]
        else:
            output_path = self.output_dir if self.output_dir else "not set"
        sys.stdout.write(f"\033[{y_pos};3H{output_status} Output: {Colors.CYAN}{output_path}{Colors.RESET}")
        
        # Options
        y_pos += 2
        sys.stdout.write(f"\033[{y_pos};1H{Colors.YELLOW}Options:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[1] Set input directory")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[2] Set output directory")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[3] Scan for invoices")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[4] Process all invoices")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[5] View results")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[e] Export results")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};3H[q] Back to menu")
        
        # Footer
        sys.stdout.write(f"\033[24;1H{Colors.DIM}Select an option...{Colors.RESET}")
        sys.stdout.flush()
    
    def run(self):
        """Main run loop for the invoice processor CLI"""
        import termios
        import tty
        
        # Clear screen
        sys.stdout.write("\033[2J\033[H")
        
        while True:
            # Render main interface
            self.render_main_interface()
            
            # Get key input
            key = self.get_key()
            
            if key == 'q' or key == '\x1b':  # q or ESC to quit
                break
            elif key == '1':
                success, msg = self.set_input_directory()
                self.show_message(msg, success)
            elif key == '2':
                success, msg = self.set_output_directory()
                self.show_message(msg, success)
            elif key == '3':
                success, msg = self.scan_for_invoices()
                self.show_message(msg, success)
            elif key == '4':
                success, msg = self.start_processing()
                if success:
                    # Show processing screen
                    while self.processing_active:
                        self.render_processing_status()
                        time.sleep(0.5)
                    self.show_message("processing complete!", True)
                else:
                    self.show_message(msg, False)
            elif key == '5':
                # Show results
                self.show_results_screen()
            elif key == 'e':
                success, msg = self.export_results()
                self.show_message(msg, success)
        
        # Clear screen on exit
        sys.stdout.write("\033[2J\033[H")
    
    def get_key(self):
        """Get single key press or escape sequence"""
        import termios
        import tty
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            
            # Read first character
            key = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys, etc.)
            if key == '\x1b':
                # For escape sequences, we need to read the full sequence
                try:
                    # Set a short timeout for reading additional characters
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        second = sys.stdin.read(1)
                        if second == '[':
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                third = sys.stdin.read(1)
                                return f'\x1b[{third}'
                except:
                    pass
                # If we can't read a complete sequence, just return ESC
                return '\x1b'
            
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def run_in_content_area(self, x: int = 31, y: int = 3, width: int = 88, height: int = 40):
        """Run invoice processor in content area (for integration with main CLI)"""
        # Import get_single_key from main if available
        try:
            from main import get_single_key
            use_main_key_handler = True
        except ImportError:
            use_main_key_handler = False
            
        self.selected_option = 0  # Initialize selection
        # Set total options based on configuration
        self.total_options = 6 if (self.input_dir and self.output_dir) else 5
        
        while True:
            # Render menu in content area
            self.render_main_menu(x, y, width, height)
            
            # Get key input using main's handler if available
            if use_main_key_handler:
                key = get_single_key(timeout=0.1)
                if not key:
                    continue
            else:
                key = self.get_key()
            
            if key == 'q' or key == '\x1b' or key == '\x1b[D':  # q, ESC, or Left arrow to quit
                break
            elif key == '\x1b[A':  # Up arrow
                if self.selected_option > 0:
                    self.selected_option -= 1
                else:
                    self.selected_option = self.total_options - 1
                # Debug: print selected option
                # sys.stdout.write(f"\033[40;{x}HDebug: Up arrow, selected={self.selected_option}\033[K")
            elif key == '\x1b[B':  # Down arrow
                if self.selected_option < self.total_options - 1:
                    self.selected_option += 1
                else:
                    self.selected_option = 0
                # Debug: print selected option
                # sys.stdout.write(f"\033[40;{x}HDebug: Down arrow, selected={self.selected_option}\033[K")
            elif key == '\r' or key == '\n' or key == '\x1b[C':  # Enter, newline, or Right arrow
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == '1':
                self.selected_option = 0
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == '2':
                self.selected_option = 1
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == '3':
                self.selected_option = 2
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == '4' and self.input_dir and self.output_dir:
                self.selected_option = 3
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == '5':
                # View results is always at index 4
                self.selected_option = 4
                self.handle_menu_selection(x, y, width, height, use_main_key_handler)
            elif key == 'e':
                success, msg = self.export_results()
                self.show_message_at(x, y + height - 1, msg, success)
    
    def handle_menu_selection(self, x: int, y: int, width: int, height: int, use_main_key_handler=False):
        """Handle menu selection based on current selected option"""
        # Import get_single_key if needed
        if use_main_key_handler:
            try:
                from main import get_single_key
            except ImportError:
                use_main_key_handler = False
                
        if self.selected_option == 0:  # Set input directory
            success, msg = self.set_input_directory()
            self.show_message_at(x, y + height - 1, msg, success)
        elif self.selected_option == 1:  # Set output directory
            success, msg = self.set_output_directory()
            self.show_message_at(x, y + height - 1, msg, success)
        elif self.selected_option == 2:  # Scan for invoices
            success, msg = self.scan_for_invoices()
            self.show_message_at(x, y + height - 1, msg, success)
        elif self.selected_option == 3 and self.input_dir and self.output_dir:  # Start processing
            success, msg = self.start_processing()
            if success:
                # Show processing in content area
                while self.processing_active:
                    self.render_progress(x, y + 15, width)
                    time.sleep(0.5)
                # Clear the processing complete message after a short delay
                self.show_message_at(x, y + height - 1, "processing complete!", True)
                # Clear message after delay
                threading.Timer(3.0, lambda: self.clear_message_at(x, y + height - 1)).start()
            else:
                self.show_message_at(x, y + height - 1, msg, False)
        elif self.selected_option == 4 and self.input_dir and self.output_dir:  # View results (when all options)
            # Show results in content area
            self.render_results(x, y, width, height)
            if use_main_key_handler:
                get_single_key(timeout=None)
            else:
                self.get_key()  # Wait for key to return
        elif self.selected_option == 3 and not (self.input_dir and self.output_dir):  # View results (limited options)
            # Show results in content area
            self.render_results(x, y, width, height)
            if use_main_key_handler:
                get_single_key(timeout=None)
            else:
                self.get_key()  # Wait for key to return
        elif self.selected_option == 5 and self.input_dir and self.output_dir:  # Back to menu (all options)
            return  # This will break the while loop in run_in_content_area
        elif self.selected_option == 4 and not (self.input_dir and self.output_dir):  # Back to menu (limited options)
            return  # This will break the while loop in run_in_content_area
    
    def clear_message_at(self, x: int, y: int):
        """Clear message at specific position"""
        sys.stdout.write(f"\033[{y};{x}H\033[K")
        sys.stdout.flush()
    
    def show_message_at(self, x: int, y: int, msg: str, success: bool):
        """Show a message at specific position"""
        color = Colors.GREEN if success else Colors.RED
        sys.stdout.write(f"\033[{y};{x}H\033[K{color}{msg}{Colors.RESET}")
        sys.stdout.flush()
        # Auto-clear after 3 seconds
        threading.Timer(3.0, lambda: self.clear_message_at(x, y)).start()
    
    def show_message(self, msg: str, success: bool):
        """Show a temporary message"""
        color = Colors.GREEN if success else Colors.RED
        sys.stdout.write(f"\033[25;1H\033[K{color}{msg}{Colors.RESET}")
        sys.stdout.flush()
        # Auto-clear message after 3 seconds
        threading.Timer(3.0, lambda: sys.stdout.write("\033[25;1H\033[K") or sys.stdout.flush()).start()
    
    def render_processing_status(self):
        """Render the processing status screen"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(f"\033[1;1H{Colors.BOLD}{Colors.CYAN}Processing Invoices...{Colors.RESET}")
        sys.stdout.write(f"\033[2;1H{'=' * 60}")
        
        # Progress
        if self.total_files > 0:
            progress_pct = (self.progress / self.total_files) * 100
            bar_width = 40
            filled = int(bar_width * self.progress / self.total_files)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            sys.stdout.write(f"\033[4;1HProgress: {Colors.DIM}[{Colors.CYAN}{bar}{Colors.DIM}]{Colors.RESET} {progress_pct:.1f}%")
            sys.stdout.write(f"\033[5;1HProcessing: {self.progress}/{self.total_files} files")
            
            if self.current_file:
                filename = Path(self.current_file).name[:50]
                sys.stdout.write(f"\033[7;1HCurrent: {filename}")
        
        # Show recent results
        if self.results:
            y_pos = 9
            sys.stdout.write(f"\033[{y_pos};1H{Colors.BOLD}Recent Results:{Colors.RESET}")
            y_pos += 1
            for result in self.results[-5:]:  # Show last 5
                status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if result.get('status') == 'success' else f"{Colors.RED}✗{Colors.RESET}"
                filename = Path(result.get('file', '')).name[:40]
                sys.stdout.write(f"\033[{y_pos};1H  {status_icon} {filename}")
                y_pos += 1
        
        sys.stdout.write(f"\033[24;1H{Colors.DIM}Processing... Press Ctrl+C to cancel{Colors.RESET}")
        sys.stdout.flush()
    
    def show_results_screen(self):
        """Show results in a separate screen"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(f"\033[1;1H{Colors.BOLD}{Colors.CYAN}Processing Results{Colors.RESET}")
        sys.stdout.write(f"\033[2;1H{'=' * 60}")
        
        if not self.results:
            sys.stdout.write(f"\033[4;1H{Colors.DIM}No results available yet{Colors.RESET}")
        else:
            y_pos = 4
            sys.stdout.write(f"\033[{y_pos};1HProcessed {len(self.results)} files:")
            y_pos += 2
            
            for i, result in enumerate(self.results[:15], 1):  # Show first 15
                # Fix: Check 'status' field properly
                status = "✓" if result.get('status') == 'success' else "✗"
                color = Colors.GREEN if result.get('status') == 'success' else Colors.RED
                filename = Path(result.get('file', 'unknown')).name[:50]
                
                sys.stdout.write(f"\033[{y_pos};1H{color}{status}{Colors.RESET} {filename}")
                y_pos += 1
                
                if y_pos > 20:
                    break
        
        sys.stdout.write(f"\033[24;1H{Colors.DIM}Press any key to return{Colors.RESET}")
        sys.stdout.flush()
        self.get_key()


# Global instance
invoice_processor_cli = InvoiceProcessorCLI()