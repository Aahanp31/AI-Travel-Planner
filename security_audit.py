#!/usr/bin/env python3
"""
Security Audit Script
====================
Scans the codebase for exposed API keys, secrets, and sensitive data.

Usage:
    python security_audit.py
    python security_audit.py --fix  # Attempt to fix some issues
"""

import os
import re
import sys
from pathlib import Path

# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    # API Keys
    (r'(api[_-]?key|apikey)\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']', 'API Key'),
    (r'(secret[_-]?key|secretkey)\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']', 'Secret Key'),

    # Google/Firebase
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
    (r'"type":\s*"service_account"', 'Google Service Account'),

    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'aws[_-]?secret[_-]?access[_-]?key', 'AWS Secret'),

    # Generic secrets
    (r'(password|passwd|pwd)\s*[:=]\s*["\'][^"\']{8,}["\']', 'Password'),
    (r'(token|auth)\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']', 'Auth Token'),
    (r'(private[_-]?key|privatekey)\s*[:=]', 'Private Key'),

    # Database URLs with credentials
    (r'(postgres|mysql|mongodb)://[^:]+:[^@]+@', 'Database URL with credentials'),

    # JWT secrets
    (r'(jwt[_-]?secret|jwtsecret)\s*[:=]\s*["\']([^"\']{8,})["\']', 'JWT Secret'),
]

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    '.git/',
    '__pycache__/',
    'node_modules/',
    '.next/',
    'build/',
    'dist/',
    '.env.example',
    'security_audit.py',
    '.gitignore',
    '*.md',
    '*.json.example',
]

# Files that should ONLY contain environment variables
ALLOWED_SECRET_FILES = [
    '.env',
    '.env.local',
    '.env.development',
    '.env.production',
]


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def should_exclude(file_path):
    """Check if file should be excluded from scanning"""
    file_str = str(file_path)
    return any(pattern in file_str for pattern in EXCLUDE_PATTERNS)


def is_allowed_secret_file(file_path):
    """Check if this file is allowed to contain secrets"""
    return file_path.name in ALLOWED_SECRET_FILES


def scan_file(file_path):
    """
    Scan a single file for secrets.

    Returns:
        list: List of (line_number, pattern_name, match) tuples
    """
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern, name in SECRET_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        findings.append((line_num, name, match.group(0)))
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Could not read {file_path}: {e}{Colors.RESET}")

    return findings


def scan_directory(directory):
    """
    Scan all files in directory recursively.

    Returns:
        dict: {file_path: [(line_num, pattern_name, match), ...]}
    """
    results = {}

    for file_path in Path(directory).rglob('*'):
        if not file_path.is_file():
            continue

        if should_exclude(file_path):
            continue

        # Skip binary files
        try:
            with open(file_path, 'rb') as f:
                if b'\x00' in f.read(1024):
                    continue
        except:
            continue

        findings = scan_file(file_path)
        if findings:
            # If this is an allowed secret file (.env), just note it
            if is_allowed_secret_file(file_path):
                results[file_path] = [(0, 'INFO', '.env file (expected to contain secrets)')]
            else:
                results[file_path] = findings

    return results


def check_gitignore():
    """Check if .gitignore properly excludes secret files"""
    gitignore_path = Path('.gitignore')

    if not gitignore_path.exists():
        return False, "No .gitignore found"

    with open(gitignore_path, 'r') as f:
        content = f.read()

    required_patterns = ['.env', '*.key', '*_secret*', 'credentials.json']
    missing = [p for p in required_patterns if p not in content]

    if missing:
        return False, f"Missing patterns: {', '.join(missing)}"

    return True, "All critical patterns present"


def check_env_example():
    """Check that .env.example has no real secrets"""
    env_example = Path('backend/.env.example')

    if not env_example.exists():
        return False, "No .env.example found"

    with open(env_example, 'r') as f:
        content = f.read()

    # Check for patterns that look like real secrets
    suspicious = []

    if re.search(r'AIza[0-9A-Za-z_-]{35}', content):
        suspicious.append("Real Google API key detected")

    if re.search(r'AKIA[0-9A-Z]{16}', content):
        suspicious.append("Real AWS key detected")

    # Check if example values are used
    if 'your-' not in content and 'example' not in content.lower():
        suspicious.append("No placeholder values found")

    if suspicious:
        return False, "; ".join(suspicious)

    return True, "Only placeholder values present"


def main():
    """Main audit function"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔒 Security Audit - Scanning for Exposed Secrets{Colors.RESET}\n")
    print("="*60 + "\n")

    # Check current directory
    if not Path('.git').exists():
        print(f"{Colors.YELLOW}⚠️  Warning: Not in a git repository{Colors.RESET}\n")

    # Check .gitignore
    print(f"{Colors.BOLD}1. Checking .gitignore...{Colors.RESET}")
    gitignore_ok, gitignore_msg = check_gitignore()
    if gitignore_ok:
        print(f"   {Colors.GREEN}✓ {gitignore_msg}{Colors.RESET}")
    else:
        print(f"   {Colors.RED}✗ {gitignore_msg}{Colors.RESET}")

    # Check .env.example
    print(f"\n{Colors.BOLD}2. Checking .env.example...{Colors.RESET}")
    env_ok, env_msg = check_env_example()
    if env_ok:
        print(f"   {Colors.GREEN}✓ {env_msg}{Colors.RESET}")
    else:
        print(f"   {Colors.RED}✗ {env_msg}{Colors.RESET}")

    # Scan codebase
    print(f"\n{Colors.BOLD}3. Scanning codebase for secrets...{Colors.RESET}")
    results = scan_directory('.')

    # Remove .env files from results (they're expected to have secrets)
    code_results = {k: v for k, v in results.items()
                    if not is_allowed_secret_file(k)}

    if not code_results:
        print(f"   {Colors.GREEN}✓ No exposed secrets found in code{Colors.RESET}")
    else:
        print(f"   {Colors.RED}✗ Found {len(code_results)} files with potential secrets{Colors.RESET}\n")

        for file_path, findings in code_results.items():
            print(f"\n   {Colors.BOLD}{file_path}{Colors.RESET}")
            for line_num, pattern_name, match in findings:
                # Truncate long matches
                display_match = match if len(match) < 50 else match[:47] + '...'
                print(f"      Line {line_num}: {Colors.YELLOW}{pattern_name}{Colors.RESET}")
                print(f"      → {display_match}")

    # Summary
    print(f"\n{'='*60}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")

    issues = []
    if not gitignore_ok:
        issues.append(".gitignore incomplete")
    if not env_ok:
        issues.append(".env.example has real secrets")
    if code_results:
        issues.append(f"{len(code_results)} files with exposed secrets")

    if issues:
        print(f"   {Colors.RED}✗ {len(issues)} issue(s) found:{Colors.RESET}")
        for issue in issues:
            print(f"      - {issue}")
        print(f"\n{Colors.YELLOW}⚠️  Action Required:{Colors.RESET}")
        print("   1. Move all secrets to .env file")
        print("   2. Update .env.example with placeholder values only")
        print("   3. Ensure .gitignore excludes all secret files")
        print("   4. Run: git diff --staged (before committing)")
        return 1
    else:
        print(f"   {Colors.GREEN}✓ No security issues found!{Colors.RESET}")
        print(f"   {Colors.GREEN}✓ API keys are properly secured{Colors.RESET}")
        return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        print()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Audit cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error during audit: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
