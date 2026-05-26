"""
Map env-configured class names to model indices for waste-style detection
without retraining. COCO models use labels like bottle, cup, bowl (not "waste").
"""

import os
from typing import Optional

# Default when neither WASTE_CLASSES nor WASTE_PRESET is set.
_DEFAULT_NAMES = "bottle,cup,bowl"

# Presets map friendly waste-focused names to COCO labels this stack uses as proxies.
_PRESETS = {
    "bottles": "bottle",
    "bottle_only": "bottle",
    "waste_bottles": "bottle",
    "plastic_bottles": "bottle",  # legacy preset name
    "disposables": "bottle,cup,bowl",
    "default": "bottle,cup,bowl",
    "cups": "cup,bowl",
}


def _explicit_class_names_from_env() -> Optional[str]:
    """If user set explicit classes, return stripped string (possibly empty). Else None."""
    if "WASTE_CLASSES" in os.environ:
        return os.environ["WASTE_CLASSES"].strip()
    if "PLASTIC_WASTE_CLASSES" in os.environ:
        return os.environ["PLASTIC_WASTE_CLASSES"].strip()
    return None


def _preset_from_env() -> str:
    return (
        os.getenv("WASTE_PRESET")
        or os.getenv("PLASTIC_WASTE_PRESET")
        or ""
    ).strip().lower()


def _detect_all_classes_requested() -> bool:
    for key in ("WASTE_DETECT_ALL", "PLASTIC_WASTE_ALL"):
        if os.getenv(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


def _resolved_class_names() -> str:
    """Class list string before splitting; empty string => no class filter."""
    explicit = _explicit_class_names_from_env()
    if explicit is not None:
        return explicit

    preset = _preset_from_env()
    if preset:
        if preset not in _PRESETS:
            print(
                f"[waste_classes] Unknown WASTE_PRESET '{preset}'. "
                f"Try: {', '.join(sorted(set(_PRESETS)))}. Using '{_DEFAULT_NAMES}'."
            )
        return _PRESETS.get(preset, _DEFAULT_NAMES)
    return _DEFAULT_NAMES


def waste_class_indices(names: dict) -> Optional[list[int]]:
    """
    Resolve configured class names to indices for model(..., classes=[...]).

    Environment (new names; legacy PLASTIC_* still supported):

    - WASTE_DETECT_ALL=1 : no filter (all model classes).
    - WASTE_CLASSES : comma-separated names (overrides WASTE_PRESET).
    - WASTE_PRESET : bottles | disposables | cups | ...
    """
    if _detect_all_classes_requested():
        return None

    raw = _resolved_class_names()
    if not raw:
        return None

    wanted = [w.strip().lower() for w in raw.split(",") if w.strip()]
    rev = {str(v).lower(): int(k) for k, v in names.items()}
    indices: list[int] = []
    for w in wanted:
        if w in rev:
            indices.append(rev[w])
        else:
            print(f"[waste_classes] Unknown class name '{w}' for this model — skipping.")
    if wanted and not indices:
        print("[waste_classes] No valid names matched the model; falling back to all classes.")
        return None
    return indices if indices else None


def predict_kwargs(class_indices: Optional[list[int]]) -> dict:
    """Keyword args for model() / model.predict() when filtering classes."""
    if class_indices is None:
        return {}
    return {"classes": class_indices}
