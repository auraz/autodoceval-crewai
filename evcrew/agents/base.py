from pydantic import BaseModel


class AgentResult(BaseModel):
    score: float = 0.0
    content: str = ""
    feedback: str = ""


def parse_agent_response(response: str) -> tuple[float, str]:
    """Parse agent response to extract score and feedback."""
    lines = response.splitlines()
    
    def extract_score(line: str) -> float:
        """Extract score from line if it starts with 'Score:'."""
        if line.startswith("Score:"):
            try:
                return float(line[len("Score:"):].strip())
            except ValueError:
                return 0.0
        return 0.0
    
    score = next((extract_score(line) for line in lines if line.startswith("Score:")), 0.0)
    
    feedback_start = next((i for i, line in enumerate(lines) if line.startswith("Feedback:")), -1)
    if feedback_start >= 0:
        feedback_lines = [lines[feedback_start][len("Feedback:"):].strip()]
        feedback_lines.extend(line.strip() for line in lines[feedback_start + 1:] if line.strip())
        return score, "\n".join(feedback_lines)
    
    return score, ""
