import git
import re
from datetime import datetime, timezone
from typing import List, Dict, Tuple

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.risk_patterns = {
            'api_key': r'(?i)(api[_-]key|apikey|secret[_-]key|token)',
            'password': r'(?i)(password|passwd|pwd)',
            'certificate': r'(?i)(-----BEGIN .*PRIVATE KEY-----|-----BEGIN CERTIFICATE-----)',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

    def analyze_commit_patterns(self) -> List[Dict]:
        suspicious_commits = []
        for commit in self.repo.iter_commits():
            risk_score = 0
            findings = []
            
            # Analyze commit message
            for pattern_name, pattern in self.risk_patterns.items():
                if re.search(pattern, commit.message):
                    risk_score += 5
                    findings.append(f'Suspicious pattern {pattern_name} in commit message')

            # Analyze diff content
            if len(commit.parents) > 0:
                diff = commit.parents[0].diff(commit, create_patch=True)
                for d in diff:
                    if hasattr(d, 'diff'):
                        diff_text = d.diff.decode('utf-8', errors='ignore')
                        for pattern_name, pattern in self.risk_patterns.items():
                            matches = re.finditer(pattern, diff_text)
                            for match in matches:
                                risk_score += 8
                                findings.append(f'Suspicious pattern {pattern_name} in file {d.a_path}')

            # Analyze commit timing
            commit_time = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)
            if commit_time.hour < 5 or commit_time.hour > 22:  # Suspicious hours
                risk_score += 3
                findings.append('Commit made during suspicious hours')

            if risk_score > 5:
                suspicious_commits.append({
                    'commit_hash': commit.hexsha,
                    'author': commit.author.email,
                    'date': commit_time.isoformat(),
                    'risk_score': risk_score,
                    'findings': findings
                })

        return suspicious_commits

    def get_commit_velocity(self, days: int = 30) -> Dict:
        current_time = datetime.now(timezone.utc)
        commits = list(self.repo.iter_commits())
        recent_commits = [c for c in commits if 
            (current_time - datetime.fromtimestamp(c.committed_date, tz=timezone.utc)).days <= days]
        
        return {
            'total_commits': len(recent_commits),
            'commits_per_day': len(recent_commits) / days,
            'unique_authors': len(set(c.author.email for c in recent_commits))
        }

    def find_large_changes(self, line_threshold: int = 100) -> List[Dict]:
        large_commits = []
        for commit in self.repo.iter_commits():
            if len(commit.parents) > 0:
                diff = commit.parents[0].diff(commit, create_patch=True)
                lines_changed = sum(
                    len(d.diff.decode('utf-8').split('\n')) 
                    for d in diff 
                    if hasattr(d, 'diff')
                )
                
                if lines_changed > line_threshold:
                    large_commits.append({
                        'commit_hash': commit.hexsha,
                        'author': commit.author.email,
                        'date': datetime.fromtimestamp(commit.committed_date, tz=timezone.utc).isoformat(),
                        'lines_changed': lines_changed
                    })
        
        return large_commits