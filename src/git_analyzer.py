import git
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.risk_patterns = {
            'high': [
                r'password',
                r'secret',
                r'token',
                r'api[_-]key',
                r'credential'
            ],
            'medium': [
                r'auth',
                r'config',
                r'private',
                r'ssh'
            ]
        }

    def analyze_commit_history(self) -> Dict:
        commits = list(self.repo.iter_commits('master'))
        analysis = {
            'total_commits': len(commits),
            'risk_score': 0,
            'high_risk_commits': [],
            'medium_risk_commits': [],
            'commit_frequency': self._calculate_commit_frequency(commits),
            'author_stats': self._get_author_statistics(commits)
        }
        
        for commit in commits:
            risk_level = self._assess_commit_risk(commit)
            if risk_level == 'high':
                analysis['risk_score'] += 10
                analysis['high_risk_commits'].append({
                    'hash': commit.hexsha,
                    'message': commit.message,
                    'author': commit.author.name,
                    'date': commit.committed_datetime.isoformat()
                })
            elif risk_level == 'medium':
                analysis['risk_score'] += 5
                analysis['medium_risk_commits'].append({
                    'hash': commit.hexsha,
                    'message': commit.message,
                    'author': commit.author.name,
                    'date': commit.committed_datetime.isoformat()
                })
        
        return analysis

    def _assess_commit_risk(self, commit) -> str:
        message = commit.message.lower()
        diffs = commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE)
        
        # Check commit message and changes for risk patterns
        for pattern in self.risk_patterns['high']:
            if re.search(pattern, message) or any(
                re.search(pattern, diff.diff.decode('utf-8', errors='ignore'))
                for diff in diffs
            ):
                return 'high'
        
        for pattern in self.risk_patterns['medium']:
            if re.search(pattern, message) or any(
                re.search(pattern, diff.diff.decode('utf-8', errors='ignore'))
                for diff in diffs
            ):
                return 'medium'
        
        return 'low'

    def _calculate_commit_frequency(self, commits: List) -> Dict:
        if not commits:
            return {'commits_per_day': 0, 'days_since_last_commit': 0}
        
        first_commit = commits[-1]
        last_commit = commits[0]
        days_diff = (last_commit.committed_datetime - first_commit.committed_datetime).days
        
        if days_diff == 0:
            commits_per_day = len(commits)
        else:
            commits_per_day = len(commits) / days_diff
        
        days_since_last = (datetime.now(timezone.utc) - last_commit.committed_datetime).days
        
        return {
            'commits_per_day': round(commits_per_day, 2),
            'days_since_last_commit': days_since_last
        }

    def _get_author_statistics(self, commits: List) -> Dict:
        authors = {}
        for commit in commits:
            author = commit.author.name
            if author not in authors:
                authors[author] = {
                    'commit_count': 0,
                    'first_commit': commit.committed_datetime,
                    'last_commit': commit.committed_datetime
                }
            authors[author]['commit_count'] += 1
            authors[author]['last_commit'] = max(
                authors[author]['last_commit'],
                commit.committed_datetime
            )
            authors[author]['first_commit'] = min(
                authors[author]['first_commit'],
                commit.committed_datetime
            )
        
        return authors

    def get_large_files(self, size_threshold_mb: float = 100) -> List[Tuple[str, float]]:
        large_files = []
        for blob in self.repo.git.ls_files('-z').split('\0')[:-1]:
            try:
                size_mb = self.repo.git.cat_file('-s', blob).strip()
                size_mb = float(size_mb) / (1024 * 1024)  # Convert to MB
                if size_mb > size_threshold_mb:
                    large_files.append((blob, size_mb))
            except git.exc.GitCommandError:
                continue
        return sorted(large_files, key=lambda x: x[1], reverse=True)