"""AutoDocEval *CrewAI flavour*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concrete implementation relies on the external *CrewAI* package.  When it
is available everything is re-exported from :pymod:`autodoceval_crewai.core` as
originally intended.

However, importing the sub-modules would raise an ``ImportError`` in
environments where *CrewAI* (or any of its transitive dependencies) is not
installed.  That, in turn, prevents sibling packages such as
:pymod:`autodoceval.benchmark` from even **detecting** the flavour – it simply
shows up as *“package not installed”*.

To provide a smoother developer experience we fall back to *stub* implementations
whenever the real dependencies are missing.  The stubs keep the public API
intact so other tools can import the module without crashing while still
signalling clearly that full functionality is unavailable.
"""

from __future__ import annotations

import warnings
from typing import Tuple, Optional

__all__ = [
    "evaluate_document",
    "improve_document",
    "auto_improve_document",
]

__version__ = "0.1.0"


# ---------------------------------------------------------------------------
# Try to import the *real* implementation
# ---------------------------------------------------------------------------

try:
    # Importing `.core` will transitively import `.agents` which pulls in the
    # external ``crewai`` package.  If that import succeeds we simply re-export
    # everything from there.
    from .core import (  # type: ignore  # noqa: WPS433 (re-export)
        auto_improve_document,
        evaluate_document,
        improve_document,
    )

    from .agents import (  # type: ignore  # noqa: WPS433 (re-export)
        DocumentEvaluator,
        DocumentImprover,
    )
    __all__.extend(["DocumentEvaluator", "DocumentImprover"])

except ModuleNotFoundError as exc:
    # Detect *direct* or *transitive* missing dependencies (most likely the
    # ``crewai`` package).  Anything else should surface as usual because it
    # represents a real bug rather than an optional dependency.
    if exc.name and (
        exc.name.startswith("crewai")
        or exc.name.startswith("langchain")
        or exc.name.startswith("openai")
    ):
        warnings.warn(
            "Optional dependency missing – falling back to stubbed "
            "autodoceval_crewai implementation.  Install the 'crewai' extra "
            "to unlock full functionality.",
            stacklevel=2,
        )

        # -------------------------------------------------------------------
        # All public API now raises a clear error if CrewAI is missing.
        # -------------------------------------------------------------------

        def _not_available(*_args, **_kwargs):  # noqa: D401,WPS110
            """Inform the caller that CrewAI is required."""
            raise RuntimeError(
                "CrewAI (and its deps) are not installed. "
                "Install with:\n\n"
                "    pip install autodoceval-crewai[crewai]\n"
            )

        evaluate_document = _not_available  # type: ignore[assignment]
        improve_document  = _not_available  # type: ignore[assignment]
        auto_improve_document = _not_available  # type: ignore[assignment]
        DocumentEvaluator   = _not_available  # type: ignore[assignment]
        DocumentImprover    = _not_available  # type: ignore[assignment]

    else:  # pragma: no cover – re-raise *other* import problems unchanged
        raise
