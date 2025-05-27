# Document evaluation and improvement workflow using Just

# Settings
input_dir := "docs/input"
output_dir := "docs/output"

# Default: show available commands
default:
    @just --list

# Auto-improve all documents
all: 
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    for doc_path in sorted(Path("{{input_dir}}").glob("*.md")):
        name = doc_path.stem
        print(f"\n🔄 Processing {name}...")
        crew = DocumentCrew()
        output_path = Path("{{output_dir}}") / name
        output_path.mkdir(parents=True, exist_ok=True)
        crew.auto_improve_one(read_file(doc_path), output_path, name, str(doc_path))

# Evaluate all documents
evaluate-all:
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    crew = DocumentCrew()
    for doc_path in sorted(Path("{{input_dir}}").glob("*.md")):
        name = doc_path.stem
        output_path = Path("{{output_dir}}") / name
        output_path.mkdir(parents=True, exist_ok=True)
        content = read_file(doc_path)
        score, feedback = crew.evaluate_one(content)
        print(f"📊 {name}: {score:.0f}%")
        crew.evaluator.save(score, feedback, content, output_path, name, doc_path)

# Evaluate single document
evaluate-one name:
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    doc_path = Path("{{input_dir}}/{{name}}.md")
    output_path = Path("{{output_dir}}/{{name}}")
    output_path.mkdir(parents=True, exist_ok=True)
    
    crew = DocumentCrew()
    content = read_file(doc_path)
    score, feedback = crew.evaluate_one(content)
    print(f"📊 {{name}}: {score:.0f}%")
    crew.evaluator.save(score, feedback, content, output_path, "{{name}}", doc_path)

# Evaluate and improve all documents
evaluate-and-improve-all:
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    crew = DocumentCrew()
    for doc_path in sorted(Path("{{input_dir}}").glob("*.md")):
        name = doc_path.stem
        print(f"🔄 {name}: evaluating and improving...")
        output_path = Path("{{output_dir}}") / name
        output_path.mkdir(parents=True, exist_ok=True)
        content = read_file(doc_path)
        improved, score, feedback = crew.evaluate_and_improve_one(content, name)
        print(f"   → Final: {score:.0f}%")
        crew.improver.save(content, improved, score, feedback, output_path, name, doc_path)

# Evaluate and improve single document
evaluate-and-improve-one name:
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    doc_path = Path("{{input_dir}}/{{name}}.md")
    output_path = Path("{{output_dir}}/{{name}}")
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 {{name}}: evaluating and improving...")
    crew = DocumentCrew()
    content = read_file(doc_path)
    improved, score, feedback = crew.evaluate_and_improve_one(content, "{{name}}")
    print(f"   → Final: {score:.0f}%")
    crew.improver.save(content, improved, score, feedback, output_path, "{{name}}", doc_path)

# Auto-improve all documents (alias)
auto-improve-all: all

# Auto-improve single document from custom path
auto-improve-one doc name:
    #!/usr/bin/env python3
    import sys; sys.path.insert(0, '.')
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    crew = DocumentCrew()
    output_path = Path("{{output_dir}}/custom")
    output_path.mkdir(parents=True, exist_ok=True)
    crew.auto_improve_one(read_file("{{doc}}"), output_path, "{{name}}", "{{doc}}")

# Clean all outputs
clean:
    rm -rf {{output_dir}}/*
    @echo "✨ Cleaned output directory"

# Development commands
test: && lint
    uv run pytest evcrew/tests/ -v

lint:
    uv run ruff check evcrew/

format:
    uv run ruff format evcrew/

# Show project structure
structure:
    tree -I '__pycache__|*.pyc|.git|venv|.venv|*.egg-info' .

# Publishing commands
build:
    uv build
    @echo "📦 Package built successfully"

publish-test:
    uv publish --publish-url https://test.pypi.org/legacy/
    @echo "🧪 Published to TestPyPI"

publish:
    uv publish --config-file .pypirc
    @echo "🚀 Published to PyPI"

# GitHub release
release version:
    git tag -a v{{version}} -m "Release v{{version}}"
    git push origin v{{version}}
    @echo "🏷️  Tagged release v{{version}}"

# Create GitHub release with notes
github-release version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    # Check if tag exists
    if ! git rev-parse v{{version}} >/dev/null 2>&1; then
        echo "❌ Tag v{{version}} doesn't exist. Run 'just release {{version}}' first."
        exit 1
    fi
    
    # Generate release notes
    echo "📝 Generating release notes for v{{version}}..."
    
    # Get previous tag
    PREV_TAG=$(git describe --tags --abbrev=0 v{{version}}^ 2>/dev/null || echo "")
    
    # Generate changelog
    if [ -n "$PREV_TAG" ]; then
        CHANGES=$(git log --pretty=format:"- %s" $PREV_TAG..v{{version}} | grep -v "Merge" || true)
    else
        CHANGES=$(git log --pretty=format:"- %s" v{{version}} | grep -v "Merge" || true)
    fi
    
    # Create release notes
    NOTES=$(cat <<'RELEASE_NOTES'
## What's Changed in v{{version}}

CHANGES_PLACEHOLDER

## Installation

    pip install autodoceval-crewai=={{version}}

## Full Changelog

RELEASE_NOTES
)
    # Replace placeholders
    NOTES=$(echo "$NOTES" | sed "s/CHANGES_PLACEHOLDER/$CHANGES/")
    if [ -n "$PREV_TAG" ]; then
        NOTES="${NOTES}https://github.com/kry/autodoceval-crewai/compare/${PREV_TAG}...v{{version}}"
    else
        NOTES="${NOTES}https://github.com/kry/autodoceval-crewai/commits/v{{version}}"
    fi
    
    # Create GitHub release
    gh release create v{{version}} \
        --title "v{{version}}" \
        --notes "$NOTES" \
        --verify-tag
    
    @echo "✅ GitHub release v{{version}} created!"

# Full release workflow: bump version, build, tag, create release, and publish
full-release version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "🚀 Starting full release process for v{{version}}..."
    
    # Update version in pyproject.toml
    sed -i '' 's/version = ".*"/version = "{{version}}"/' pyproject.toml
    
    # Commit version bump
    git add pyproject.toml
    git commit -m "chore: bump version to {{version}}" || true
    
    # Build package
    echo "📦 Building package..."
    rm -rf dist/*
    uv build
    
    # Create and push tag
    echo "🏷️  Creating tag..."
    git tag -a v{{version}} -m "Release v{{version}}"
    git push origin main
    git push origin v{{version}}
    
    # Create GitHub release
    echo "📝 Creating GitHub release..."
    just github-release {{version}}
    
    # Publish to PyPI
    echo "📤 Publishing to PyPI..."
    UV_PUBLISH_USERNAME=__token__ UV_PUBLISH_PASSWORD=$(cat ~/.pypirc | grep password | cut -d' ' -f3) uv publish
    
    echo "✨ Release v{{version}} completed successfully!"