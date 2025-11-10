#!/usr/bin/env python3
"""
System Scrolls Integration Example for UNIBOS
Shows how to integrate the system_scrolls module into the main application
"""

from system_scrolls import SystemScrolls
import json
from datetime import datetime


class SystemScrollsIntegration:
    """Integration helper for System Scrolls feature"""
    
    def __init__(self):
        self.scrolls = SystemScrolls()
    
    def get_menu_display_info(self) -> dict:
        """Get formatted info for menu display"""
        info = self.scrolls.get_all_info()
        
        # Extract key metrics for menu display
        cpu_usage = info.get("cpu", {}).get("usage_percent", "N/A")
        mem_info = info.get("memory", {}).get("virtual", {})
        mem_percent = mem_info.get("percent", "N/A")
        
        return {
            "cpu_usage": f"{cpu_usage}%" if cpu_usage != "N/A" else "N/A",
            "memory_usage": f"{mem_percent}%" if mem_percent != "N/A" else "N/A",
            "uptime": info.get("system", {}).get("uptime", "Unknown"),
            "processes": info.get("system", {}).get("process_count", "Unknown")
        }
    
    def get_detailed_report(self) -> str:
        """Get detailed system report as formatted string"""
        from io import StringIO
        import sys
        
        # Capture the display output
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        
        try:
            self.scrolls.display_info()
            output = buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return output
    
    def monitor_resources(self, threshold_cpu: float = 80.0, threshold_mem: float = 90.0) -> dict:
        """Monitor system resources and return alerts if thresholds exceeded"""
        info = self.scrolls.get_all_info()
        alerts = []
        
        # Check CPU usage
        cpu_usage = info.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > threshold_cpu:
            alerts.append({
                "type": "CPU",
                "severity": "WARNING",
                "message": f"CPU usage is high: {cpu_usage}%",
                "value": cpu_usage
            })
        
        # Check memory usage
        mem_percent = info.get("memory", {}).get("virtual", {}).get("percent", 0)
        if mem_percent > threshold_mem:
            alerts.append({
                "type": "MEMORY",
                "severity": "CRITICAL" if mem_percent > 95 else "WARNING",
                "message": f"Memory usage is high: {mem_percent}%",
                "value": mem_percent
            })
        
        # Check disk usage
        disk_info = info.get("disk", {})
        for partition in disk_info.get("partitions", []):
            if isinstance(partition.get("percent"), (int, float)) and partition["percent"] > 90:
                alerts.append({
                    "type": "DISK",
                    "severity": "WARNING",
                    "message": f"Disk {partition['device']} is {partition['percent']}% full",
                    "value": partition["percent"]
                })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "status": "HEALTHY" if not alerts else "NEEDS_ATTENTION"
        }
    
    def get_system_health_score(self) -> dict:
        """Calculate overall system health score (0-100)"""
        info = self.scrolls.get_all_info()
        scores = []
        
        # CPU score (100 - usage%)
        cpu_usage = info.get("cpu", {}).get("usage_percent")
        if cpu_usage is not None:
            cpu_score = max(0, 100 - cpu_usage)
            scores.append(("CPU", cpu_score))
        
        # Memory score (100 - usage%)
        mem_percent = info.get("memory", {}).get("virtual", {}).get("percent")
        if mem_percent is not None:
            mem_score = max(0, 100 - mem_percent)
            scores.append(("Memory", mem_score))
        
        # Disk score (average of all partitions)
        disk_scores = []
        for partition in info.get("disk", {}).get("partitions", []):
            if isinstance(partition.get("percent"), (int, float)):
                disk_scores.append(max(0, 100 - partition["percent"]))
        if disk_scores:
            disk_score = sum(disk_scores) / len(disk_scores)
            scores.append(("Disk", disk_score))
        
        # Calculate overall score
        if scores:
            overall_score = sum(score for _, score in scores) / len(scores)
        else:
            overall_score = 0
        
        return {
            "overall": round(overall_score, 1),
            "components": {name: round(score, 1) for name, score in scores},
            "grade": self._get_health_grade(overall_score)
        }
    
    def _get_health_grade(self, score: float) -> str:
        """Convert health score to grade"""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "GOOD"
        elif score >= 60:
            return "FAIR"
        elif score >= 40:
            return "POOR"
        else:
            return "CRITICAL"
    
    def export_diagnostic_package(self, filename: str = "unibos_diagnostics.json") -> str:
        """Export complete diagnostic package"""
        package = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.scrolls.get_all_info(),
            "health_score": self.get_system_health_score(),
            "resource_alerts": self.monitor_resources(),
            "summary": self.scrolls.get_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        return f"Diagnostic package exported to: {filename}"


# Example usage in UNIBOS menu system
def display_system_scrolls_menu():
    """Example function showing how to integrate with UNIBOS menu"""
    integration = SystemScrollsIntegration()
    
    print("\n╔════════════════════════════════════════╗")
    print("║        SYSTEM SCROLLS - UNIBOS         ║")
    print("╚════════════════════════════════════════╝")
    
    # Quick stats
    menu_info = integration.get_menu_display_info()
    print(f"\n CPU Usage: {menu_info['cpu_usage']}")
    print(f" Memory Usage: {menu_info['memory_usage']}")
    print(f" Uptime: {menu_info['uptime']}")
    print(f" Processes: {menu_info['processes']}")
    
    # Health score
    health = integration.get_system_health_score()
    print(f"\n System Health: {health['overall']}% ({health['grade']})")
    
    # Resource alerts
    monitoring = integration.monitor_resources()
    if monitoring['alerts']:
        print("\n ⚠️  ALERTS:")
        for alert in monitoring['alerts']:
            print(f"  - {alert['severity']}: {alert['message']}")
    else:
        print("\n ✅ All systems operating normally")
    
    print("\n Options:")
    print(" 1. View Detailed Report")
    print(" 2. Export Diagnostics")
    print(" 3. Monitor Resources")
    print(" 4. Return to Main Menu")
    print("\n" + "─" * 42)


if __name__ == "__main__":
    # Demo the integration
    display_system_scrolls_menu()
    
    # Show how to get specific data
    integration = SystemScrollsIntegration()
    print("\n\nQuick System Summary:")
    print(integration.scrolls.get_summary())
    
    # Show health score
    health = integration.get_system_health_score()
    print(f"\nSystem Health Score: {health['overall']}% ({health['grade']})")
    for component, score in health['components'].items():
        print(f"  - {component}: {score}%")