"""Command-line interface for AutoDocEval."""

import argparse
import sys
from pathlib import Path

from .core import auto_improve_document, evaluate_document, improve_document
from .file_utils import read_file


def main() -> None:
    """Main CLI entry point for AutoDocEval."""
    parser = argparse.ArgumentParser(description="Document evaluation and improvement using CrewAI agents")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    grade_parser = subparsers.add_parser("grade", help="Evaluate document clarity")  # grade command
    grade_parser.add_argument("document", help="Path to document to evaluate")
    grade_parser.add_argument("--memory-id", help="Custom memory ID for persistent context")

    improve_parser = subparsers.add_parser("improve", help="Improve a document")  # improve command
    improve_parser.add_argument("document", help="Path to document to improve")
    improve_parser.add_argument("--memory-id", help="Custom memory ID for persistent context")

    auto_parser = subparsers.add_parser("auto-improve", help="Auto-improve document iteratively")  # auto-improve command
    auto_parser.add_argument("document", help="Path to document to improve")
    auto_parser.add_argument("--iterations", type=int, default=3, help="Max improvement iterations")
    auto_parser.add_argument("--target", type=float, default=0.7, help="Target clarity score (0-1)")
    auto_parser.add_argument("--memory-id", help="Custom memory ID for persistent context")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "grade":
        content = read_file(args.document)
        memory_id = args.memory_id or f"autodoceval_grade_{Path(args.document).stem}"
        score, feedback = evaluate_document(content, memory_id)
        print(f"\n📊 Clarity Score: {score:.2f}/1.0")
        print(f"\n💬 Feedback:\n{feedback}")

    elif args.command == "improve":
        content = read_file(args.document)
        memory_id = args.memory_id or f"autodoceval_improve_{Path(args.document).stem}"
        score, feedback = evaluate_document(content, memory_id + "_eval")  # First evaluate to get feedback
        improved = improve_document(content, feedback, memory_id)
        print(f"\n✨ Improved Document:\n\n{improved}")

    elif args.command == "auto-improve":
        memory_id = args.memory_id or f"autodoceval_auto_{Path(args.document).stem}"
        final_path = auto_improve_document(args.document, args.iterations, args.target, memory_id)
        print(f"\n📄 Final improved document saved to: {final_path}")


if __name__ == "__main__":
    main()