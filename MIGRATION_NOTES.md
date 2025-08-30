# Migration from setup.py to pyproject.toml

This document outlines the migration of the `djangorestframework-simplejwt` project from the legacy `setup.py`-based build system to the modern `pyproject.toml`-based build system.

## Overview

The migration addresses several limitations of the old build system while maintaining backward compatibility. The new system provides better tool integration, centralized configuration, and follows current Python packaging standards.

## Changes Made

### New Files Created
- `pyproject.toml` - Centralized project configuration following PEP 517/518 standards
- `rest_framework_simplejwt/_version.py` - Version management file for setuptools_scm
- `requirements-dev.txt` - Development dependencies specification
- `MIGRATION_NOTES.md` - This documentation file

### Files Modified
- `rest_framework_simplejwt/__init__.py` - Updated version management to use `_version.py`
- `tox.ini` - Added `setuptools_scm[toml]>=6.2` dependency for version handling
- `Makefile` - Updated build commands to use `python -m build`
- `.gitignore` - Added `pyproject.toml.lock` to ignore list

### Files Temporarily Kept
Several legacy configuration files are temporarily retained to ensure a smooth transition:
- `setup.py` - Replaced by `pyproject.toml` but kept for compatibility
- `setup.cfg` - Configuration moved to `pyproject.toml`
- `MANIFEST.in` - Package data configuration moved to `pyproject.toml`
- `pytest.ini` - Test configuration moved to `pyproject.toml`
- `.coveragerc` - Coverage configuration moved to `pyproject.toml`

These files will be removed in a subsequent pull request after the main migration is stable.

## Benefits of the New System

### Modern Standards Compliance
The new system follows PEP 517/518 build system standards, providing better integration with modern Python tools and improved dependency specification.

### Centralized Configuration
All project configuration is now consolidated in a single `pyproject.toml` file, making it easier to maintain and understand. This also improves tool integration across the development ecosystem.

### Enhanced Build Process
The build process now uses `python -m build` instead of `setup.py`, providing better isolation during builds and more reliable dependency resolution.

### Improved Tool Configuration
Tool configurations for linting (Ruff), testing (pytest), and coverage are now centralized in the project configuration file.

## Usage Examples

### Building the Package
```bash
python -m build
```

### Development Installation
```bash
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

### Running with Tox
```bash
tox -e py310-dj42-drf314-pyjwt171-tests
```

### Code Quality Checks
```bash
ruff check rest_framework_simplejwt tests/
```

## Dependencies

The project now requires these core build dependencies:
- `setuptools>=61.0`
- `setuptools_scm[toml]>=6.2`
- `wheel`

## Version Management

Version management is now handled by `setuptools_scm`, which automatically generates version numbers from git tags and writes version information to `rest_framework_simplejwt/_version.py`. The system supports the post-release versioning scheme used by the project.

## Migration Notes

The migration maintains full backward compatibility while introducing improvements:
- All existing functionality is preserved
- The test suite passes with the new configuration
- Tox environments work correctly
- Build artifacts are functionally identical to the old system

## Future Improvements

The new system provides a foundation for easier:
- Integration of new development tools
- Configuration of additional linting rules
- Setup of CI/CD pipelines
- Management of project metadata
- Addition of new optional dependencies

## Implementation Phases

### Phase 1: Initial Migration (Current)
- Add `pyproject.toml` with modern configuration
- Update `__init__.py` to use new version management
- Update `tox.ini` and `Makefile`
- Maintain legacy files for compatibility
- Ensure all tests pass with new system

### Phase 2: Cleanup (Future)
- Remove `setup.py`
- Remove `setup.cfg`
- Remove `MANIFEST.in`
- Remove `pytest.ini`
- Remove `.coveragerc`
- Clean up any remaining references to legacy files

This phased approach ensures a smooth transition without disrupting existing development workflows.
