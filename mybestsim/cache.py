"""Empreinte du code de calcul, pour invalider le cache Streamlit."""

import hashlib
import inspect

from mybestsim import etl, metrics


def version_donnees() -> str:
    """12 premiers caractères du SHA-256 de etl.py et metrics.py.

    `st.cache_data` ne hache que le code de la fonction décorée. Passer cette
    empreinte en argument force le recalcul dès qu'un module de calcul change.
    """
    source = inspect.getsource(etl) + inspect.getsource(metrics)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
