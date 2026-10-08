"""Memoise a value for the lifetime of one request.

Context processors run for every template rendered in a response, and this
project has fourteen of them. Several issue queries for the navbar and sidebar
badges — numbers that cannot change mid-request, but were being recomputed each
time a template was rendered.

:func:`cached_per_request` stashes the result on the request object, which the
garbage collector disposes of at the end of the response. No cross-request
leakage, no cache backend, no invalidation to get wrong.

    stats = cached_per_request(request, 'comm_stats', build_comm_stats)

When there is no request (a management command, a shell), it simply calls
through — correctness first, caching second.
"""

_PREFIX = '_ucs_cache__'


def cached_per_request(request, key, builder):
    """Return ``builder()``, computing it at most once per request.

    ``builder`` is only called on a miss, so an expensive query is skipped
    entirely on the second and later reads.
    """
    if request is None:
        return builder()

    attr = _PREFIX + key
    # A sentinel rather than a None check: None, 0 and {} are all legitimate
    # cached values and must not be recomputed on every subsequent read.
    missing = object()
    value = getattr(request, attr, missing)
    if value is missing:
        value = builder()
        try:
            setattr(request, attr, value)
        except Exception:  # pragma: no cover - exotic request objects
            pass
    return value
