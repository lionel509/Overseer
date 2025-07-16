# GitHub Repository Structure

This document explains the structure and purpose of files in the `.github` directory.

## Directory Structure

```
.github/
├── ISSUE_TEMPLATE/          # Issue templates
│   ├── bug_report.md       # Bug report template
│   └── feature_request.md  # Feature request template
├── DISCUSSION_TEMPLATE/     # Discussion templates
│   ├── general.md          # General discussion template
│   ├── ideas.md            # Ideas and suggestions template
│   └── questions.md        # Q&A template
├── workflows/              # GitHub Actions workflows
│   ├── ci.yml             # Continuous Integration
│   ├── release.yml        # Release automation
│   └── security.yml       # Security checks
├── scripts/               # Utility scripts
│   ├── maintenance.sh     # Repository maintenance
│   └── health_check.py    # Repository health check
├── docs/                  # Documentation
│   └── structure.md       # This file
├── CODEOWNERS            # Code ownership rules
├── CONTRIBUTING.md       # Contributing guidelines
├── SECURITY.md          # Security policy
├── SUPPORT.md           # Support information
└── pull_request_template.md  # PR template
```

## File Purposes

### Templates

- **ISSUE_TEMPLATE/**: Provides structured templates for different types of issues
- **DISCUSSION_TEMPLATE/**: Templates for GitHub Discussions
- **pull_request_template.md**: Template for pull requests

### Documentation

- **CONTRIBUTING.md**: Guidelines for contributors
- **SECURITY.md**: Security policy and vulnerability reporting
- **SUPPORT.md**: Information on getting help

### Configuration

- **CODEOWNERS**: Defines who owns different parts of the codebase
- **workflows/**: GitHub Actions for automation

### Scripts

- **scripts/**: Utility scripts for repository maintenance
- **docs/**: Additional documentation

## Best Practices

1. Keep templates up to date with project needs
2. Review and update CODEOWNERS regularly
3. Ensure security policy is current
4. Test GitHub Actions workflows
5. Update documentation as the project evolves

## Customization

Feel free to modify these templates and files to match your project's specific needs. The structure provided here follows GitHub's recommendations and community best practices.
