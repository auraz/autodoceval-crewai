import json
from contextlib import suppress

from pydantic import BaseModel


class AgentResult(BaseModel):
    score: float = 0.0
    content: str = ""
    feedback: str = ""


def parse_agent_response(response: str) -> tuple[float, str]:
    """Parse JSON agent response to extract score and feedback."""
    try:
        data = json.loads(response.strip())
        score = float(data.get("score", 0.0))
        feedback = str(data.get("feedback", ""))
        return score, feedback
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback to old format for compatibility
        lines = response.splitlines()
        score = 0.0
        feedback_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith("Score:"):
                with suppress(ValueError):
                    score = float(line[len("Score:"):].strip())
            elif line.startswith("Feedback:"):
                feedback_lines = [line[len("Feedback:"):].strip()]
                feedback_lines.extend(line.strip() for line in lines[i + 1:] if line.strip())
                break
        
        return score, "\n".join(feedback_lines)


def parse_improver_response(response: str) -> str:
    """Parse JSON improver response to extract improved content."""
    try:
        data = json.loads(response.strip())
        return str(data.get("improved_content", response))
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback to raw response if not JSON
        return response.strip()
