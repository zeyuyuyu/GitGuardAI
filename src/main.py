import os
import git
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List, Dict

class Guardian:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.security_model = self._load_security_model()
        self.workflow_model = self._load_workflow_model()

    def _load_security_model(self) -> AutoModelForSequenceClassification:
        model_path = os.getenv('GITGUARD_SECURITY_MODEL', 'gitguard/security-v1')
        return AutoModelForSequenceClassification.from_pretrained(model_path)

    def _load_workflow_model(self) -> AutoModelForSequenceClassification:
        model_path = os.getenv('GITGUARD_WORKFLOW_MODEL', 'gitguard/workflow-v1')
        return AutoModelForSequenceClassification.from_pretrained(model_path)

    def watch(self):
        """Start monitoring git operations"""
        self.repo.git.hooks_path = self._install_hooks()
        print('GitGuardAI is now watching your repository')

    def analyze_diff(self, diff: str) -> Dict[str, float]:
        """Analyze git diff for security issues and workflow optimizations"""
        security_score = self._analyze_security(diff)
        workflow_score = self._analyze_workflow(diff)
        
        return {
            'security_risk': security_score,
            'workflow_efficiency': workflow_score
        }
