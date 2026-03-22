import os
import re
import subprocess

class SecurityScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def scan_for_vulnerabilities(self):
        """Scan the repository for known vulnerabilities and security issues."""
        # Perform static code analysis
        self.static_code_analysis()
        
        # Check for known security vulnerabilities
        self.check_for_vulnerabilities()
        
        # Scan for sensitive information leaks
        self.scan_for_sensitive_data()

    def static_code_analysis(self):
        """Perform static code analysis using tools like bandit, flake8, and pylint."""
        # Run bandit to check for security issues
        subprocess.run(["bandit", "-r", self.repo_path], check=True)
        
        # Run flake8 to check for code style and quality issues
        subprocess.run(["flake8", self.repo_path], check=True)
        
        # Run pylint to check for code quality and maintainability issues
        subprocess.run(["pylint", self.repo_path], check=True)

    def check_for_vulnerabilities(self):
        """Check the repository for known security vulnerabilities using tools like OWASP dependency check."""
        # Run OWASP dependency check to scan for vulnerable dependencies
        subprocess.run(["dependency-check", "--out", "dependency-check-report.xml", "--scan", self.repo_path], check=True)
        
        # Parse the dependency check report and report any found vulnerabilities
        self.parse_dependency_check_report()

    def scan_for_sensitive_data(self):
        """Scan the repository for sensitive information like API keys, passwords, and other credentials."""
        # Define a list of patterns to search for sensitive information
        sensitive_patterns = [
            r"\b(password|secret|key|token)\s*[=:]+\s*['\"]([^'\"]+)['\"]\b",
            r"\b(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY)\s*[=:]+\s*['\"]([^'\"]+)['\"]\b",
            r"\b(GITHUB_TOKEN|GITHUB_SECRET)\s*[=:]+\s*['\"]([^'\"]+)['\"]\b"
        ]
        
        # Scan the repository for sensitive information
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    for pattern in sensitive_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            for match in matches:
                                print(f"Potential sensitive information found in {file_path}: {match[1]}")
