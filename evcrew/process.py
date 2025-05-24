"""Document processing iterators and workflows."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agents import DocumentEvaluator, DocumentImprover


@dataclass
class DocumentIterator:
    """Iterator for document improvement iterations."""
    
    evaluator: "DocumentEvaluator"
    improver: "DocumentImprover"
    initial_content: str
    max_iterations: int = 2
    target_score: float = 85
    current_content: str = field(init=False)
    current_feedback: str = field(default="", init=False)
    iteration_count: int = field(default=0, init=False)
    scores: list[float] = field(default_factory=list, init=False)
    contents: list[str] = field(default_factory=list, init=False)
    feedbacks: list[str] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Initialize mutable state after dataclass init."""
        self.current_content = self.initial_content
        self.contents = [self.initial_content]
        
    def __iter__(self):
        """Return iterator instance."""
        return self
        
    def __next__(self) -> tuple[int, str, float, str]:
        """Return (iteration_number, content, score, feedback) for each iteration."""
        if self.iteration_count == 0:
            # Initial evaluation
            score, feedback = self.evaluator.execute(self.initial_content)
            self.scores.append(score)
            self.feedbacks.append(feedback)
            self.current_feedback = feedback
            self.iteration_count += 1
            
            if score >= self.target_score:
                raise StopIteration("Target score met on initial evaluation")
                
            return (0, self.initial_content, score, feedback)
            
        elif self.iteration_count <= self.max_iterations:
            # Improvement iteration
            improved_content = self.improver.execute(self.current_content, self.current_feedback)
            score, feedback = self.evaluator.execute(improved_content)
            
            self.current_content = improved_content
            self.current_feedback = feedback
            self.contents.append(improved_content)
            self.scores.append(score)
            self.feedbacks.append(feedback)
            
            iteration_num = self.iteration_count
            self.iteration_count += 1
            
            if score >= self.target_score:
                raise StopIteration("Target score reached")
                
            return (iteration_num, improved_content, score, feedback)
            
        else:
            raise StopIteration("Max iterations reached")
            
    def get_final_content(self) -> str:
        """Get the final improved content."""
        return self.contents[-1] if len(self.contents) > 1 else self.initial_content
        
    def get_final_score(self) -> float:
        """Get the final score."""
        return self.scores[-1] if self.scores else 0.0
        
    def get_improvement_delta(self) -> float:
        """Get total improvement from initial to final."""
        if len(self.scores) > 1:
            return self.scores[-1] - self.scores[0]
        return 0.0