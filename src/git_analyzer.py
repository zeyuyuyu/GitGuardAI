import git
import pandas as pd
from datetime import datetime
from collections import defaultdict

class GitAnalyzer:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)
        self.commit_data = []
        self.contributor_stats = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'files_modified': set(),
            'last_active': None
        })

    def analyze_repository(self):
        """Analyze the git repository and gather comprehensive metrics"""
        for commit in self.repo.iter_commits():
            stats = commit.stats.total
            author = commit.author.name
            date = datetime.fromtimestamp(commit.committed_date)
            
            # Update contributor stats
            self.contributor_stats[author]['commits'] += 1
            self.contributor_stats[author]['additions'] += stats['insertions']
            self.contributor_stats[author]['deletions'] += stats['deletions']
            self.contributor_stats[author]['last_active'] = max(
                date,
                self.contributor_stats[author]['last_active'] or date
            )
            
            # Track modified files
            for file in commit.stats.files:
                self.contributor_stats[author]['files_modified'].add(file)
            
            # Store commit data
            self.commit_data.append({
                'hash': commit.hexsha,
                'author': author,
                'date': date,
                'message': commit.message.strip(),
                'additions': stats['insertions'],
                'deletions': stats['deletions'],
                'files_changed': len(commit.stats.files)
            })
    
    def get_contributor_metrics(self):
        """Return detailed contributor metrics as a DataFrame"""
        metrics = []
        for author, stats in self.contributor_stats.items():
            metrics.append({
                'author': author,
                'total_commits': stats['commits'],
                'total_additions': stats['additions'],
                'total_deletions': stats['deletions'],
                'files_touched': len(stats['files_modified']),
                'last_active': stats['last_active'],
                'impact_score': stats['additions'] + stats['deletions'] * 0.5
            })
        return pd.DataFrame(metrics)
    
    def get_activity_timeline(self):
        """Generate a timeline of repository activity"""
        df = pd.DataFrame(self.commit_data)
        return df.set_index('date').sort_index()
    
    def get_hotspots(self):
        """Identify code hotspots - files with most changes"""
        file_changes = defaultdict(lambda: {'changes': 0, 'authors': set()})
        
        for commit in self.repo.iter_commits():
            for file in commit.stats.files:
                file_changes[file]['changes'] += 1
                file_changes[file]['authors'].add(commit.author.name)
        
        hotspots = [{
            'file': file,
            'total_changes': stats['changes'],
            'unique_authors': len(stats['authors'])
        } for file, stats in file_changes.items()]
        
        return pd.DataFrame(hotspots).sort_values('total_changes', ascending=False)
