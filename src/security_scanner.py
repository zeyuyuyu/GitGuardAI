import ast
import re
from pathlib import Path
from typing import List, Dict, Set

class SecurityScanner:
    def __init__(self):
        self.vulnerability_patterns = {
            'sql_injection': r'.*execute\(.*\%.*\)',
            'command_injection': r'os\.system\(.*\)|subprocess\.run\(.*shell=True.*\)',
            'hardcoded_secrets': r'password\s*=\s*[\'"].*[\'"]|api_key\s*=\s*[\'"].*[\'"]',
            'unsafe_deserialization': r'pickle\.loads|yaml\.load\(',
        }

    def scan_file(self, filepath: Path) -> Dict[str, List[int]]:
        """Scan a single file for security vulnerabilities.

        Args:
            filepath: Path to the file to scan

        Returns:
            Dictionary mapping vulnerability types to line numbers
        """
        findings = {}
        
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            for vuln_type, pattern in self.vulnerability_patterns.items():
                matches = []
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        matches.append(i)
                if matches:
                    findings[vuln_type] = matches

        return findings

    def scan_directory(self, directory: Path) -> Dict[str, Dict[str, List[int]]]:
        """Recursively scan a directory for security vulnerabilities.

        Args:
            directory: Path to directory to scan

        Returns:
            Dictionary mapping filenames to their vulnerability findings
        """
        results = {}
        
        for filepath in directory.rglob('*.py'):
            findings = self.scan_file(filepath)
            if findings:
                results[str(filepath)] = findings
                
        return results

    def generate_report(self, scan_results: Dict[str, Dict[str, List[int]]]) -> str:
        """Generate a formatted report from scan results.

        Args:
            scan_results: Results from scan_directory()

        Returns:
            Formatted string report
        """
        report = ['Security Scan Results', '===================\n']
        
        if not scan_results:
            report.append('No security vulnerabilities found.')
            return '\n'.join(report)
            
        for filepath, findings in scan_results.items():
            report.append(f'File: {filepath}')
            for vuln_type, lines in findings.items():
                report.append(f'  {vuln_type.replace("_", " ").title()}:')
                report.append(f'    Lines: {", ".join(map(str, lines))}\n')
                
        return '\n'.join(report)

    def quick_scan(self, path: Path) -> str:
        """Convenience method to scan and generate report in one step.

        Args:
            path: Path to file or directory to scan

        Returns:
            Formatted scan report
        """
        if path.is_file():
            results = {str(path): self.scan_file(path)}
        else:
            results = self.scan_directory(path)
            
        return self.generate_report(results)

if __name__ == '__main__':
    scanner = SecurityScanner()
    print(scanner.quick_scan(Path('.')))