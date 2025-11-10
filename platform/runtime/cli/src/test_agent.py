#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Test Agent - Intelligent Testing Framework
Automated testing agent for UNIBOS development workflow

Author: berk hatırlı
Version: v1.0
Purpose: Automated testing before version delivery
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unibos_logger import logger, LogCategory, LogLevel

# Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'


class TestAgent:
    """Intelligent testing agent for UNIBOS"""
    
    def __init__(self):
        self.base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_results = []
        self.test_suite = self._initialize_test_suite()
        
        logger.info("Test Agent initialized", category=LogCategory.MODULE)
    
    def _initialize_test_suite(self) -> Dict[str, List[Dict]]:
        """Initialize the test suite with various test categories"""
        return {
            "syntax": [
                {
                    "name": "Python Syntax Check",
                    "command": "python -m py_compile",
                    "pattern": "*.py",
                    "critical": True
                }
            ],
            "imports": [
                {
                    "name": "Import Validation",
                    "function": self._test_imports,
                    "critical": True
                }
            ],
            "core_functions": [
                {
                    "name": "Main Menu Navigation",
                    "function": self._test_main_navigation,
                    "critical": True
                },
                {
                    "name": "Claude CLI Integration",
                    "function": self._test_claude_cli,
                    "critical": False
                }
            ],
            "database": [
                {
                    "name": "Database Connection",
                    "function": self._test_database,
                    "critical": False
                }
            ],
            "ui": [
                {
                    "name": "Terminal Compatibility",
                    "function": self._test_terminal,
                    "critical": True
                }
            ],
            "integration": [
                {
                    "name": "Module Integration",
                    "function": self._test_module_integration,
                    "critical": True
                }
            ]
        }
    
    def run_all_tests(self, verbose: bool = True) -> Tuple[bool, List[Dict]]:
        """Run all tests and return results"""
        self.test_results = []
        total_tests = sum(len(tests) for tests in self.test_suite.values())
        passed_tests = 0
        failed_critical = False
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}🧪 UNIBOS Test Suite{Colors.RESET}")
        print(f"{Colors.DIM}Running {total_tests} tests...{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        for category, tests in self.test_suite.items():
            print(f"\n{Colors.BOLD}{category.upper()} TESTS:{Colors.RESET}")
            
            for test in tests:
                test_name = test['name']
                is_critical = test.get('critical', False)
                
                # Run the test
                if 'command' in test:
                    success, message = self._run_command_test(test)
                elif 'function' in test:
                    success, message = test['function']()
                else:
                    success, message = False, "Invalid test configuration"
                
                # Record result
                result = {
                    "category": category,
                    "name": test_name,
                    "success": success,
                    "message": message,
                    "critical": is_critical,
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(result)
                
                # Display result
                if success:
                    print(f"  {Colors.GREEN}✅{Colors.RESET} {test_name}")
                    passed_tests += 1
                else:
                    icon = "❌" if is_critical else "⚠️"
                    color = Colors.RED if is_critical else Colors.YELLOW
                    print(f"  {color}{icon}{Colors.RESET} {test_name}")
                    if verbose and message:
                        print(f"     {Colors.DIM}{message}{Colors.RESET}")
                    
                    if is_critical:
                        failed_critical = True
        
        # Summary
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary:{Colors.RESET}")
        print(f"  Total: {total_tests}")
        print(f"  {Colors.GREEN}Passed: {passed_tests}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {total_tests - passed_tests}{Colors.RESET}")
        
        if failed_critical:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  CRITICAL TESTS FAILED!{Colors.RESET}")
            print(f"{Colors.YELLOW}Fix critical issues before version delivery.{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All critical tests passed!{Colors.RESET}")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        return not failed_critical, self.test_results
    
    def _run_command_test(self, test: Dict) -> Tuple[bool, str]:
        """Run a command-based test"""
        try:
            pattern = test.get('pattern', '*.py')
            files = list(self.base_path.rglob(pattern))
            
            if not files:
                return True, "No files to test"
            
            failed_files = []
            for file in files[:10]:  # Test max 10 files for performance
                cmd = f"{test['command']} {file}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    failed_files.append(file.name)
            
            if failed_files:
                return False, f"Failed for: {', '.join(failed_files[:3])}"
            
            return True, f"Tested {len(files)} files"
            
        except Exception as e:
            return False, str(e)
    
    def _test_imports(self) -> Tuple[bool, str]:
        """Test critical imports"""
        critical_imports = [
            "unibos_logger",
            "database.models",
            "claude_cli",
            "ai_builder",
            "development_manager"
        ]
        
        failed_imports = []
        for module in critical_imports:
            try:
                __import__(module)
            except ImportError:
                failed_imports.append(module)
        
        if failed_imports:
            return False, f"Failed imports: {', '.join(failed_imports)}"
        
        return True, "All critical imports successful"
    
    def _test_main_navigation(self) -> Tuple[bool, str]:
        """Test main menu navigation system"""
        try:
            # Check if main.py has required functions
            main_path = self.base_path / "src" / "main.py"
            if not main_path.exists():
                return False, "main.py not found"
            
            content = main_path.read_text()
            required_functions = [
                "draw_main_screen",
                "update_module_selection", 
                "update_tool_selection",
                "get_single_key"
            ]
            
            missing = [f for f in required_functions if f"def {f}" not in content]
            if missing:
                return False, f"Missing functions: {', '.join(missing)}"
                
            return True, "Navigation system intact"
            
        except Exception as e:
            return False, str(e)
    
    def _test_claude_cli(self) -> Tuple[bool, str]:
        """Test Claude CLI availability"""
        try:
            result = subprocess.run(
                "claude --version", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, "Claude CLI available"
            else:
                return False, "Claude CLI not found or not configured"
                
        except subprocess.TimeoutExpired:
            return False, "Claude CLI timeout"
        except Exception as e:
            return False, str(e)
    
    def _test_database(self) -> Tuple[bool, str]:
        """Test database connectivity"""
        try:
            from database.db_manager import Session, ENGINE
            
            # Try to create a session
            session = Session()
            session.close()
            
            return True, f"Database connected ({ENGINE.name})"
            
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def _test_terminal(self) -> Tuple[bool, str]:
        """Test terminal compatibility"""
        try:
            size = os.get_terminal_size()
            if size.columns < 80 or size.lines < 24:
                return False, f"Terminal too small: {size.columns}x{size.lines}"
            
            # Test UTF-8 support
            test_chars = "ç ğ ı ö ş ü"
            encoded = test_chars.encode('utf-8').decode('utf-8')
            if encoded != test_chars:
                return False, "UTF-8 encoding issue"
                
            return True, f"Terminal OK: {size.columns}x{size.lines}"
            
        except Exception as e:
            return False, str(e)
    
    def _test_module_integration(self) -> Tuple[bool, str]:
        """Test module integration"""
        try:
            # Check if all required modules exist
            required_modules = [
                "currencies", 
                "birlikteyiz",
                "recaria",
                "kisiselenflasyon"
            ]
            
            modules_dir = self.base_path / "modules"
            missing = []
            
            for module in required_modules:
                module_path = modules_dir / module
                if not module_path.exists() or not (module_path / "__init__.py").exists():
                    missing.append(module)
            
            if missing:
                return False, f"Missing modules: {', '.join(missing)}"
                
            return True, "All modules present"
            
        except Exception as e:
            return False, str(e)
    
    def get_test_report(self) -> str:
        """Generate a detailed test report"""
        if not self.test_results:
            return "No test results available"
        
        report = []
        report.append("# UNIBOS Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Group by category
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Generate report for each category
        for category, results in categories.items():
            report.append(f"## {category.upper()}")
            for r in results:
                status = "✅ PASS" if r['success'] else ("❌ FAIL" if r['critical'] else "⚠️ WARN")
                report.append(f"- {status} {r['name']}")
                if not r['success'] and r['message']:
                    report.append(f"  - {r['message']}")
            report.append("")
        
        # Summary
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        critical_failed = sum(1 for r in self.test_results if not r['success'] and r['critical'])
        
        report.append("## Summary")
        report.append(f"- Total Tests: {total}")
        report.append(f"- Passed: {passed}")
        report.append(f"- Failed: {total - passed}")
        report.append(f"- Critical Failures: {critical_failed}")
        
        return "\n".join(report)
    
    def save_test_report(self, filepath: Optional[Path] = None) -> Path:
        """Save test report to file"""
        if filepath is None:
            reports_dir = self.base_path / "reports" / "tests"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = reports_dir / f"test_report_{timestamp}.md"
        
        report = self.get_test_report()
        filepath.write_text(report, encoding='utf-8')
        
        logger.info(f"Test report saved to: {filepath}", category=LogCategory.MODULE)
        return filepath


def run_tests(verbose: bool = True) -> bool:
    """Main entry point for running tests"""
    agent = TestAgent()
    success, results = agent.run_all_tests(verbose=verbose)
    
    # Save report
    report_path = agent.save_test_report()
    print(f"\n📄 Test report saved to: {report_path}")
    
    return success


if __name__ == "__main__":
    # Run tests when module is executed directly
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    success = run_tests(verbose=verbose)
    sys.exit(0 if success else 1)