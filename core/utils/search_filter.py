from functools import wraps
from typing import Callable, List, Optional
from django.db.models import Q, QuerySet
import re
from urllib.parse import unquote_plus
import inspect
from inspect import Parameter, Signature


def search_filter(fields: List[str], min_chars: int = 2):
    """Decorator factory that applies a simple icontains search over given model fields.

    Usage:
        @router.get("/", response=list[Schema])
        @paginate
        @search_filter(["nombre", "nif"])
        def listar(request):
            return Model.objects.all()

    The decorator expects the decorated function to return a Django QuerySet.
    It accepts an optional query param named `busqueda` (string). If `busqueda` is present
    and its length >= `min_chars`, the returned QuerySet will be filtered using
    `field__icontains=busqueda` ORed across all provided fields.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request, *args, busqueda: Optional[str] = None, **kwargs):
            # Call the original view to obtain the base QuerySet (or result)
            result = func(request, *args, **kwargs)

            # Only apply search when the result is a QuerySet
            if not isinstance(result, QuerySet):
                return result

            # Decode URL-encoded input and normalize whitespace
            q = unquote_plus(busqueda or "").strip()
            # Replace sequences of non-word characters (punctuation) with a space
            # Keep unicode letters/digits and underscores; turn other punctuation into spaces
            q = re.sub(r"[^\w\sÀ-ÿ]", " ", q)
            # Collapse multiple spaces and trim
            q = re.sub(r"\s+", " ", q).strip()
            if not q or len(q) < min_chars:
                return result

            filter_q = Q()
            for field in fields:
                filter_q |= Q(**{f"{field}__icontains": q})

            return result.filter(filter_q)

        # Expose `busqueda` in the wrapper signature so OpenAPI (Ninja) documents it.
        try:
            orig_sig = inspect.signature(func)
            params = list(orig_sig.parameters.values())
            # Only add if not present
            if 'busqueda' not in orig_sig.parameters:
                # Add as keyword-only parameter
                busq_param = Parameter('busqueda', kind=Parameter.KEYWORD_ONLY, annotation=Optional[str], default=None)
                params.append(busq_param)
            wrapper.__signature__ = Signature(parameters=params, return_annotation=orig_sig.return_annotation)
        except Exception:
            # If anything fails, do not break execution; leave wrapper as-is
            pass

        return wrapper

    return decorator
from functools import wraps
from ninja.responses import Response

def superuser_required(func):
    """Decorador que requiere que el usuario sea superusuario"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "Solo los superusuarios pueden realizar esta acción"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

