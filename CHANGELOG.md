# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-01-27

### Added
- Comprehensive test suite with 95% code coverage
- GitHub Actions CI/CD pipeline for automated testing
- GitHub Actions workflow for automated PyPI publishing
- Test coverage reporting with Codecov integration
- Support for Python 3.12 (latest version)
- Additional unit tests for all components
- Edge case and error handling tests

### Changed
- Updated .gitignore to remove duplicate entries
- Consolidated virtual environment configurations
- Improved README with badges and development instructions
- Updated project structure documentation

### Fixed
- Test method names to match actual API
- Save method implementations in agents
- Iterator behavior in document processing

### Removed
- Duplicate venv entries in .gitignore
- Unused tracking.py references

## [0.2.0] - Previous release

### Added
- Support for extra prompts in agents
- Initial test suite

## [0.1.0] - Initial release

### Added
- Document evaluation agent
- Document improvement agent
- CrewAI-based multi-agent workflow
- Just command runner integration
- Iteration tracking system
- Python API for programmatic access