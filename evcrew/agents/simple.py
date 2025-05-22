class EvaluatorAgent:
    def __init__(self, memory_id: str):
        self.memory_id = memory_id

    def evaluate(self, text):
        # Dummy implementation for demonstration
        score = 0.8
        feedback = "Good job, but could be improved."
        return {"score": score, "feedback": feedback}

    def save_memory(self):
        pass

class ImproverAgent:
    def __init__(self, memory_id: str):
        self.memory_id = memory_id

    def improve(self, text):
        # Dummy implementation for demonstration
        return text + "\n\n[Improved]"

    def save_memory(self):
        pass

def get_evaluator_agent(memory_id: str):
    return EvaluatorAgent(memory_id=memory_id)

def get_improver_agent(memory_id: str):
    return ImproverAgent(memory_id=memory_id)

def get_auto_improver_agents(memory_id: str):
    return {
        "evaluator": EvaluatorAgent(memory_id=memory_id),
        "improver": ImproverAgent(memory_id=memory_id),
    }
