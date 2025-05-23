from crewai.memory import Memory as CrewMemory
from pydantic import BaseModel


class AgentResult(BaseModel):
    score: float = 0.0
    content: str = ""
    feedback: str = ""


def create_memory_instance(memory_id: str) -> CrewMemory:
    """Return a CrewMemory instance. Memory is always required."""
    return CrewMemory(memory_id=memory_id)


def parse_agent_response(response: str) -> tuple[float, str]:
    lines = response.splitlines()
    score = 0.0
    feedback_lines: list[str] = []
    for line in lines:
        if line.startswith("Score:"):
            try:
                score = float(line[len("Score:") :].strip())
            except ValueError:
                score = 0.0
        elif line.startswith("Feedback:"):
            feedback_lines.append(line[len("Feedback:") :].strip())
        elif feedback_lines:
            feedback_lines.append(line.strip())
    return score, "\n".join(feedback_lines)
