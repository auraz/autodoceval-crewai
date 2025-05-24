# Document evaluation and improvement workflow using Just

# Default settings
max_iterations := "2"
input_dir := "docs/input"
output_dir := "docs/output"

# Default recipe - show available commands
default:
    @just --list

# Auto-improve all documents in input directory
all: 
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    input_dir = Path("{{input_dir}}")
    output_dir = Path("{{output_dir}}")
    max_iterations = int("{{max_iterations}}")
    
    for doc_path in sorted(input_dir.glob("*.md")):
        doc_name = doc_path.stem
        print(f"\n🔄 Processing {doc_name}...")
        
        crew = DocumentCrew()
        content = read_file(doc_path)
        output_path = output_dir / doc_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        iterator = crew.auto_improve_one(content, output_path, doc_name, str(doc_path), max_iterations)

# Evaluate all documents without improvement
evaluate-all:
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    input_dir = Path("{{input_dir}}")
    output_dir = Path("{{output_dir}}")
    
    for doc_path in sorted(input_dir.glob("*.md")):
        doc_name = doc_path.stem
        output_path = output_dir / doc_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        crew = DocumentCrew()
        content = read_file(doc_path)
        score, feedback = crew.evaluate_one(content)
        print(f"📊 {doc_name}: {score:.0f}%")
        crew.evaluator.save(score, feedback, content, output_path, doc_name, doc_path)

# Evaluate single document
evaluate-one name:
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    doc_path = Path("{{input_dir}}") / "{{name}}.md"
    output_path = Path("{{output_dir}}") / "{{name}}"
    output_path.mkdir(parents=True, exist_ok=True)
    
    crew = DocumentCrew()
    content = read_file(doc_path)
    score, feedback = crew.evaluate_one(content)
    print(f"📊 {{name}}: {score:.0f}%")
    crew.evaluator.save(score, feedback, content, output_path, "{{name}}", doc_path)

# Evaluate and improve all documents
evaluate-and-improve-all:
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    input_dir = Path("{{input_dir}}")
    output_dir = Path("{{output_dir}}")
    
    for doc_path in sorted(input_dir.glob("*.md")):
        doc_name = doc_path.stem
        print(f"🔄 {doc_name}: evaluating and improving...")
        
        output_path = output_dir / doc_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        crew = DocumentCrew()
        content = read_file(doc_path)
        improved_content, score, feedback = crew.evaluate_and_improve_one(content, doc_name)
        print(f"   → Final: {score:.0f}%")
        crew.improver.save(content, improved_content, score, feedback, output_path, doc_name, doc_path)

# Evaluate and improve single document
evaluate-and-improve-one name:
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    doc_path = Path("{{input_dir}}") / "{{name}}.md"
    output_path = Path("{{output_dir}}") / "{{name}}"
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 {{name}}: evaluating and improving...")
    crew = DocumentCrew()
    content = read_file(doc_path)
    improved_content, score, feedback = crew.evaluate_and_improve_one(content, "{{name}}")
    print(f"   → Final: {score:.0f}%")
    crew.improver.save(content, improved_content, score, feedback, output_path, "{{name}}", doc_path)

# Auto-improve all documents
auto-improve-all:
    @just all

# Auto-improve single document from custom path
auto-improve-one doc name:
    #!/usr/bin/env python3
    from pathlib import Path
    from evcrew import DocumentCrew
    from evcrew.utils import read_file
    
    doc_path = Path("{{doc}}")
    output_path = Path("{{output_dir}}") / "custom"
    output_path.mkdir(parents=True, exist_ok=True)
    
    crew = DocumentCrew()
    content = read_file(doc_path)
    iterator = crew.auto_improve_one(content, output_path, "{{name}}", str(doc_path), int("{{max_iterations}}"))

# Clean all outputs
clean:
    #!/usr/bin/env bash
    rm -rf {{output_dir}}/*
    echo "✨ Cleaned output directory"

# Run tests
test:
    uv run pytest evcrew/tests/ -v

# Run linter
lint:
    uv run ruff check evcrew/

# Format code
format:
    uv run ruff format evcrew/

# Show project structure
structure:
    tree -I '__pycache__|*.pyc|.git|venv|.venv|*.egg-info' .