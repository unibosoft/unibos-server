"""
Archive Anomaly Detection Agent
Analyzes archive patterns and detects anomalies using statistical methods
"""

import os
import glob
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ArchiveAnomalyAgent:
    """Advanced anomaly detection for UNIBOS archives"""
    
    def __init__(self):
        self.archive_path = "/Users/berkhatirli/Desktop/unibos/archive/versions"
        self.compressed_path = "/Users/berkhatirli/Desktop/unibos/archive/compressed"
        self.anomalies_found = []
        self.recommendations = []
        
    def analyze(self) -> Dict:
        """Run comprehensive anomaly analysis"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'anomalies': [],
            'recommendations': [],
            'statistics': {},
            'patterns': []
        }
        
        # Collect archive data
        archives = self._collect_archive_data()
        
        if not archives:
            return {
                'error': 'no archives found',
                'path': self.archive_path
            }
        
        # Run various anomaly detection methods
        results['statistics'] = self._calculate_statistics(archives)
        
        # 1. Size anomalies (Z-score based)
        size_anomalies = self._detect_size_anomalies(archives)
        results['anomalies'].extend(size_anomalies)
        
        # 2. Missing version detection
        missing_versions = self._detect_missing_versions(archives)
        if missing_versions:
            results['anomalies'].append({
                'type': 'missing_versions',
                'severity': 'medium',
                'versions': missing_versions,
                'message': f"detected {len(missing_versions)} missing version(s)"
            })
        
        # 3. Duplicate detection
        duplicates = self._detect_duplicates(archives)
        if duplicates:
            results['anomalies'].extend(duplicates)
        
        # 4. Growth pattern analysis
        growth_anomalies = self._analyze_growth_patterns(archives)
        if growth_anomalies:
            results['anomalies'].extend(growth_anomalies)
        
        # 5. File structure anomalies
        structure_anomalies = self._detect_structure_anomalies(archives)
        results['anomalies'].extend(structure_anomalies)
        
        # 6. Timestamp anomalies
        time_anomalies = self._detect_timestamp_anomalies(archives)
        results['anomalies'].extend(time_anomalies)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results['anomalies'])
        
        # Identify patterns
        results['patterns'] = self._identify_patterns(archives)
        
        return results
    
    def _collect_archive_data(self) -> List[Dict]:
        """Collect comprehensive data about all archives"""
        archives = []
        
        # Get all version directories
        version_dirs = sorted(glob.glob(f"{self.archive_path}/unibos_v*"))
        
        for version_dir in version_dirs:
            if os.path.isdir(version_dir):
                dirname = os.path.basename(version_dir)
                parts = dirname.split('_')
                
                if len(parts) >= 2:
                    version_str = parts[1]
                    try:
                        version_num = int(version_str[1:]) if version_str.startswith('v') else int(version_str)
                    except ValueError:
                        # Skip non-version directories
                        continue
                    
                    # Get directory stats
                    stat = os.stat(version_dir)
                    
                    # Calculate size and file count
                    total_size = 0
                    file_count = 0
                    file_types = {}
                    
                    for dirpath, dirnames, filenames in os.walk(version_dir):
                        # Skip certain directories
                        dirnames[:] = [d for d in dirnames if d not in ['venv', '__pycache__', '.git']]
                        
                        file_count += len(filenames)
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                size = os.path.getsize(filepath)
                                total_size += size
                                
                                # Track file types
                                ext = os.path.splitext(filename)[1].lower()
                                if ext:
                                    file_types[ext] = file_types.get(ext, 0) + 1
                            except:
                                pass
                    
                    # Build timestamp if available
                    build_time = None
                    if len(parts) >= 3:
                        try:
                            build_str = f"{parts[2]}_{parts[3]}" if len(parts) > 3 else parts[2]
                            build_time = datetime.strptime(build_str, "%Y%m%d_%H%M")
                        except:
                            pass
                    
                    archives.append({
                        'version': version_num,
                        'name': dirname,
                        'path': version_dir,
                        'size': total_size,
                        'size_mb': total_size / (1024 * 1024),
                        'file_count': file_count,
                        'file_types': file_types,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'build_time': build_time
                    })
        
        return sorted(archives, key=lambda x: x['version'])
    
    def _calculate_statistics(self, archives: List[Dict]) -> Dict:
        """Calculate statistical measures"""
        if not archives:
            return {}
        
        sizes = [a['size'] for a in archives]
        file_counts = [a['file_count'] for a in archives]
        
        stats = {
            'total_archives': len(archives),
            'total_size_gb': sum(sizes) / (1024 * 1024 * 1024),
            'size_stats': {
                'mean_mb': statistics.mean(sizes) / (1024 * 1024),
                'median_mb': statistics.median(sizes) / (1024 * 1024),
                'stdev_mb': statistics.stdev(sizes) / (1024 * 1024) if len(sizes) > 1 else 0,
                'min_mb': min(sizes) / (1024 * 1024),
                'max_mb': max(sizes) / (1024 * 1024)
            },
            'file_stats': {
                'mean': statistics.mean(file_counts),
                'median': statistics.median(file_counts),
                'min': min(file_counts),
                'max': max(file_counts)
            },
            'version_range': {
                'first': archives[0]['version'],
                'last': archives[-1]['version'],
                'gaps': []
            }
        }
        
        # Find version gaps
        for i in range(1, len(archives)):
            expected = archives[i-1]['version'] + 1
            actual = archives[i]['version']
            if actual > expected:
                stats['version_range']['gaps'].append({
                    'after': archives[i-1]['version'],
                    'before': actual,
                    'missing_count': actual - expected
                })
        
        return stats
    
    def _detect_size_anomalies(self, archives: List[Dict]) -> List[Dict]:
        """Detect size-based anomalies using Z-score"""
        if len(archives) < 3:
            return []
        
        anomalies = []
        sizes = [a['size'] for a in archives]
        mean_size = statistics.mean(sizes)
        stdev_size = statistics.stdev(sizes)
        
        if stdev_size == 0:
            return []
        
        for archive in archives:
            z_score = (archive['size'] - mean_size) / stdev_size
            
            if abs(z_score) > 2:
                severity = 'high' if abs(z_score) > 3 else 'medium'
                anomalies.append({
                    'type': 'size_anomaly',
                    'severity': severity,
                    'version': archive['version'],
                    'name': archive['name'],
                    'size_mb': archive['size_mb'],
                    'z_score': round(z_score, 2),
                    'message': f"v{archive['version']} size is {'unusually large' if z_score > 0 else 'unusually small'} (z={z_score:.2f})"
                })
        
        return anomalies
    
    def _detect_missing_versions(self, archives: List[Dict]) -> List[int]:
        """Detect missing version numbers"""
        if not archives:
            return []
        
        versions = [a['version'] for a in archives]
        min_version = min(versions)
        max_version = max(versions)
        
        expected = set(range(min_version, max_version + 1))
        actual = set(versions)
        missing = sorted(expected - actual)
        
        return missing
    
    def _detect_duplicates(self, archives: List[Dict]) -> List[Dict]:
        """Detect duplicate archives"""
        duplicates = []
        version_counts = {}
        
        for archive in archives:
            version = archive['version']
            if version not in version_counts:
                version_counts[version] = []
            version_counts[version].append(archive)
        
        for version, items in version_counts.items():
            if len(items) > 1:
                duplicates.append({
                    'type': 'duplicate_version',
                    'severity': 'high',
                    'version': version,
                    'count': len(items),
                    'paths': [item['path'] for item in items],
                    'message': f"v{version} has {len(items)} duplicate archives"
                })
        
        return duplicates
    
    def _analyze_growth_patterns(self, archives: List[Dict]) -> List[Dict]:
        """Analyze growth patterns for anomalies"""
        if len(archives) < 3:
            return []
        
        anomalies = []
        
        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(archives)):
            prev_size = archives[i-1]['size']
            curr_size = archives[i]['size']
            if prev_size > 0:
                growth_rate = ((curr_size - prev_size) / prev_size) * 100
                growth_rates.append({
                    'from_version': archives[i-1]['version'],
                    'to_version': archives[i]['version'],
                    'rate': growth_rate
                })
        
        if growth_rates:
            # Find unusual growth
            rates = [g['rate'] for g in growth_rates]
            mean_rate = statistics.mean(rates)
            
            if len(rates) > 1:
                stdev_rate = statistics.stdev(rates)
                
                for growth in growth_rates:
                    if stdev_rate > 0:
                        z_score = (growth['rate'] - mean_rate) / stdev_rate
                        
                        if abs(z_score) > 2:
                            anomalies.append({
                                'type': 'growth_anomaly',
                                'severity': 'medium',
                                'from_version': growth['from_version'],
                                'to_version': growth['to_version'],
                                'growth_rate': round(growth['rate'], 1),
                                'message': f"unusual growth from v{growth['from_version']} to v{growth['to_version']}: {growth['rate']:.1f}%"
                            })
        
        # Check for sudden shrinkage
        for i in range(1, len(archives)):
            if archives[i]['size'] < archives[i-1]['size'] * 0.5:
                anomalies.append({
                    'type': 'sudden_shrinkage',
                    'severity': 'high',
                    'version': archives[i]['version'],
                    'prev_version': archives[i-1]['version'],
                    'size_reduction': round((1 - archives[i]['size']/archives[i-1]['size']) * 100, 1),
                    'message': f"v{archives[i]['version']} is significantly smaller than v{archives[i-1]['version']}"
                })
        
        return anomalies
    
    def _detect_structure_anomalies(self, archives: List[Dict]) -> List[Dict]:
        """Detect anomalies in file structure"""
        anomalies = []
        
        # Check for archives with unusual file counts
        if len(archives) > 2:
            file_counts = [a['file_count'] for a in archives]
            mean_count = statistics.mean(file_counts)
            stdev_count = statistics.stdev(file_counts) if len(file_counts) > 1 else 0
            
            if stdev_count > 0:
                for archive in archives:
                    z_score = (archive['file_count'] - mean_count) / stdev_count
                    
                    if abs(z_score) > 2:
                        anomalies.append({
                            'type': 'file_count_anomaly',
                            'severity': 'low',
                            'version': archive['version'],
                            'file_count': archive['file_count'],
                            'z_score': round(z_score, 2),
                            'message': f"v{archive['version']} has unusual file count: {archive['file_count']} files"
                        })
        
        # Check for archives with no Python files
        for archive in archives:
            if '.py' not in archive.get('file_types', {}):
                anomalies.append({
                    'type': 'missing_python_files',
                    'severity': 'high',
                    'version': archive['version'],
                    'message': f"v{archive['version']} contains no Python files"
                })
        
        return anomalies
    
    def _detect_timestamp_anomalies(self, archives: List[Dict]) -> List[Dict]:
        """Detect timestamp-related anomalies"""
        anomalies = []
        
        # Check for out-of-order timestamps
        for i in range(1, len(archives)):
            if archives[i]['created'] < archives[i-1]['created']:
                anomalies.append({
                    'type': 'timestamp_order',
                    'severity': 'low',
                    'version': archives[i]['version'],
                    'prev_version': archives[i-1]['version'],
                    'message': f"v{archives[i]['version']} created before v{archives[i-1]['version']}"
                })
        
        # Check for future timestamps
        now = datetime.now()
        for archive in archives:
            if archive['created'] > now:
                anomalies.append({
                    'type': 'future_timestamp',
                    'severity': 'medium',
                    'version': archive['version'],
                    'timestamp': archive['created'].isoformat(),
                    'message': f"v{archive['version']} has future timestamp"
                })
        
        return anomalies
    
    def _generate_recommendations(self, anomalies: List[Dict]) -> List[Dict]:
        """Generate recommendations based on anomalies"""
        recommendations = []
        
        # Count anomaly types
        anomaly_types = {}
        for anomaly in anomalies:
            atype = anomaly['type']
            anomaly_types[atype] = anomaly_types.get(atype, 0) + 1
        
        # Size anomalies
        if 'size_anomaly' in anomaly_types:
            large_archives = [a for a in anomalies if a['type'] == 'size_anomaly' and a.get('z_score', 0) > 0]
            if large_archives:
                recommendations.append({
                    'priority': 'high',
                    'action': 'review_large_archives',
                    'message': f"review {len(large_archives)} unusually large archive(s) for cleanup opportunities",
                    'details': [f"v{a['version']}: {a['size_mb']:.1f} mb" for a in large_archives[:3]]
                })
        
        # Missing versions
        if 'missing_versions' in anomaly_types:
            missing = [a for a in anomalies if a['type'] == 'missing_versions']
            if missing:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'restore_missing',
                    'message': f"restore {len(missing[0]['versions'])} missing version(s) from git history",
                    'details': [f"v{v}" for v in missing[0]['versions'][:5]]
                })
        
        # Duplicates
        if 'duplicate_version' in anomaly_types:
            duplicates = [a for a in anomalies if a['type'] == 'duplicate_version']
            recommendations.append({
                'priority': 'high',
                'action': 'remove_duplicates',
                'message': f"remove duplicate archives for {len(duplicates)} version(s)",
                'details': [f"v{d['version']}: {d['count']} copies" for d in duplicates]
            })
        
        # Structure issues
        if 'missing_python_files' in anomaly_types:
            recommendations.append({
                'priority': 'critical',
                'action': 'verify_archives',
                'message': "verify archive integrity - some archives missing core files",
                'details': ["run archive validation tool", "check for corruption"]
            })
        
        return recommendations
    
    def _identify_patterns(self, archives: List[Dict]) -> List[Dict]:
        """Identify patterns in archive data"""
        patterns = []
        
        if len(archives) < 5:
            return patterns
        
        # Growth trend
        sizes = [a['size_mb'] for a in archives]
        recent_sizes = sizes[-10:]
        older_sizes = sizes[-20:-10] if len(sizes) > 20 else sizes[:len(sizes)-10]
        
        if older_sizes:
            recent_avg = statistics.mean(recent_sizes)
            older_avg = statistics.mean(older_sizes)
            growth_pct = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
            
            patterns.append({
                'type': 'growth_trend',
                'trend': 'increasing' if growth_pct > 10 else 'decreasing' if growth_pct < -10 else 'stable',
                'change_percent': round(growth_pct, 1),
                'recent_avg_mb': round(recent_avg, 1),
                'older_avg_mb': round(older_avg, 1)
            })
        
        # Release frequency
        if len(archives) > 10:
            recent_archives = archives[-10:]
            time_diffs = []
            
            for i in range(1, len(recent_archives)):
                if recent_archives[i]['build_time'] and recent_archives[i-1]['build_time']:
                    diff = (recent_archives[i]['build_time'] - recent_archives[i-1]['build_time']).total_seconds() / 3600
                    time_diffs.append(diff)
            
            if time_diffs:
                avg_hours = statistics.mean(time_diffs)
                patterns.append({
                    'type': 'release_frequency',
                    'avg_hours_between': round(avg_hours, 1),
                    'releases_per_day': round(24 / avg_hours, 1) if avg_hours > 0 else 0
                })
        
        # File type distribution
        all_types = {}
        for archive in archives[-5:]:  # Last 5 versions
            for ext, count in archive.get('file_types', {}).items():
                all_types[ext] = all_types.get(ext, 0) + count
        
        if all_types:
            sorted_types = sorted(all_types.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns.append({
                'type': 'file_distribution',
                'top_types': [{'extension': ext, 'count': count} for ext, count in sorted_types]
            })
        
        return patterns


def main():
    """Test the anomaly agent"""
    agent = ArchiveAnomalyAgent()
    results = agent.analyze()
    
    print("Archive Anomaly Analysis Results")
    print("=" * 50)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"\nTimestamp: {results['timestamp']}")
    
    # Statistics
    if results.get('statistics'):
        stats = results['statistics']
        print(f"\nStatistics:")
        print(f"  Total archives: {stats.get('total_archives', 0)}")
        print(f"  Total size: {stats.get('total_size_gb', 0):.2f} GB")
        if 'size_stats' in stats:
            print(f"  Average size: {stats['size_stats']['mean_mb']:.1f} MB")
            print(f"  Size range: {stats['size_stats']['min_mb']:.1f} - {stats['size_stats']['max_mb']:.1f} MB")
    
    # Anomalies
    print(f"\nAnomalies Found: {len(results.get('anomalies', []))}")
    for anomaly in results.get('anomalies', [])[:10]:
        severity_color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(anomaly.get('severity', 'low'))
        print(f"  {severity_color} [{anomaly['type']}] {anomaly['message']}")
    
    # Recommendations
    if results.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in results['recommendations']:
            priority_icon = {'critical': '🚨', 'high': '⚠️', 'medium': '📋', 'low': 'ℹ️'}.get(rec['priority'])
            print(f"  {priority_icon} {rec['message']}")
            for detail in rec.get('details', [])[:3]:
                print(f"      • {detail}")
    
    # Patterns
    if results.get('patterns'):
        print(f"\nPatterns Identified:")
        for pattern in results['patterns']:
            if pattern['type'] == 'growth_trend':
                print(f"  📈 Growth trend: {pattern['trend']} ({pattern['change_percent']:+.1f}%)")
            elif pattern['type'] == 'release_frequency':
                print(f"  ⏱️ Release frequency: {pattern['releases_per_day']:.1f} per day")
            elif pattern['type'] == 'file_distribution':
                print(f"  📁 Top file types: {', '.join([f'{t['extension']} ({t['count']})' for t in pattern['top_types'][:3]])}")


if __name__ == '__main__':
    main()