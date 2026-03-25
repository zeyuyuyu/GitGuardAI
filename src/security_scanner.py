import os
import subprocess
import json

class SecurityScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def scan_for_vulnerabilities(self):
        """Scans the Git repository for known security vulnerabilities."""
        vulns = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    vuln_data = self._scan_file(os.path.join(root, file))
                    if vuln_data:
                        vulns.append(vuln_data)
        return vulns

    def _scan_file(self, file_path):
        """Scans a single file for security vulnerabilities using a third-party tool."""
        try:
            output = subprocess.check_output(['bandit', '-f', 'json', file_path])
            data = json.loads(output)
            if data['results']:
                return {
                    'file': file_path,
                    'vulnerabilities': data['results']
                }
        except subprocess.CalledProcessError:
            return None
