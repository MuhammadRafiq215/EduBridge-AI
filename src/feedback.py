"""Validation helpers for anonymous student feedback."""
from __future__ import annotations

ALLOWED_CATEGORIES = {"Bug or error", "Confusing instructions", "Design or navigation", "Feature idea", "Something I liked", "Other"}
ALLOWED_WORKSPACES = {"Dashboard", "My learning profile", "Career pathways", "Study planner", "Research insights", "Account & privacy", "About EduBridge", "Overall experience"}

def validate_feedback(category: str, workspace: str, rating: int, message: str) -> tuple[dict | None, str | None]:
    """Validate a feedback record without collecting direct personal identifiers."""
    category, workspace, message = str(category or "").strip(), str(workspace or "").strip(), str(message or "").strip()
    if category not in ALLOWED_CATEGORIES:
        return None, "Choose a feedback category."
    if workspace not in ALLOWED_WORKSPACES:
        return None, "Choose the area of the website you are reviewing."
    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        return None, "Choose a rating from 1 to 5."
    if not 10 <= len(message) <= 1000:
        return None, "Please write between 10 and 1,000 characters."
    return {"category": category, "workspace": workspace, "rating": rating, "message": message}, None
