import importlib
import logging
from functools import lru_cache
from typing import Optional, Type

from .registry import REPORTS

logger = logging.getLogger(__name__)


def get_report_meta(slug: str) -> Optional[dict]:
    """
    Return the metadata dict for a report slug from REPORTS, or None if not found.
    Lightweight lookup — no imports or side-effects.
    """
    return REPORTS.get(slug)


def import_class(dotted_path: str) -> Optional[type]:
    """
    Import and return a class (or attribute) given a dotted path like
    "myapp.module.ClassName". Returns None on failure and logs the error.

    This helper is intentionally tolerant (returns None rather than raising),
    so callers can gracefully handle missing classes (e.g., show a disabled Configure button).
    """
    if not dotted_path or not isinstance(dotted_path, str):
        return None

    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError:
        logger.warning(
            "Invalid dotted path (no dot) provided to import_class: %r", dotted_path)
        return None

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        logger.exception(
            "Failed to import module %r for dotted path %r: %s", module_path, dotted_path, e)
        return None

    try:
        cls = getattr(module, class_name)
    except AttributeError:
        logger.exception("Module %r does not define attribute %r (dotted path %r)",
                         module_path, class_name, dotted_path)
        return None

    return cls


@lru_cache(maxsize=128)
def get_form_class_for_report(slug: str) -> Optional[Type]:
    """
    Return the form class for a report slug by reading REPORTS[slug]['form_class']
    and importing it. Uses LRU cache to avoid repeated imports.

    Returns None if:
      - report slug not found in registry
      - 'form_class' not provided
      - import fails
    """
    meta = get_report_meta(slug)
    if not meta:
        logger.debug("No registry entry for report slug %r", slug)
        return None

    dotted = meta.get("form_class")
    if not dotted:
        logger.debug("No 'form_class' defined for report slug %r", slug)
        return None

    cls = import_class(dotted)
    if cls is None:
        logger.warning(
            "Could not import form_class %r for report slug %r", dotted, slug)
    return cls
