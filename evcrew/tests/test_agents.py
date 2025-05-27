"""Test agent classes."""


from evcrew.agents import DocumentEvaluator, DocumentImprover


def test_evaluator_agent_creation():
    """Test DocumentEvaluator agent creation."""
    evaluator = DocumentEvaluator()
    assert evaluator.agent is not None
    assert evaluator.agent.role == "Document Quality Evaluator"


def test_evaluator_with_extra_prompt():
    """Test DocumentEvaluator with extra prompt."""
    extra = "Focus on API documentation"
    evaluator = DocumentEvaluator(extra_prompt=extra)
    assert evaluator.extra_prompt == extra


def test_evaluator_create_task():
    """Test creating evaluation task."""
    evaluator = DocumentEvaluator()
    task = evaluator.create_task("# Test Doc", doc_name="test")
    
    assert task is not None
    assert task.agent == evaluator.agent
    assert "document" in task.description.lower()


def test_improver_agent_creation():
    """Test DocumentImprover agent creation."""
    improver = DocumentImprover()
    assert improver.agent is not None
    assert improver.agent.role == "Documentation Improver"


def test_improver_with_extra_prompt():
    """Test DocumentImprover with extra prompt."""
    extra = "Add more examples"
    improver = DocumentImprover(extra_prompt=extra)
    assert improver.extra_prompt == extra


def test_improver_create_task():
    """Test creating improvement task."""
    improver = DocumentImprover()
    task = improver.create_task("# Test Doc", doc_name="test")
    
    assert task is not None
    assert task.agent == improver.agent
    assert "improve" in task.description.lower()


def test_evaluator_base_methods():
    """Test evaluator base methods."""
    evaluator = DocumentEvaluator()
    
    # Test that evaluator has the required methods
    assert hasattr(evaluator, 'execute')
    assert hasattr(evaluator, 'create_task')
    assert hasattr(evaluator, 'save')
    
    # Test API key is set
    assert evaluator.api_key is not None


def test_improver_base_methods():
    """Test improver base methods."""
    improver = DocumentImprover()
    
    # Test that improver has the required methods
    assert hasattr(improver, 'execute')
    assert hasattr(improver, 'create_task')
    assert hasattr(improver, 'save')
    
    # Test API key is set
    assert improver.api_key is not None