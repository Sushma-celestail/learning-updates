def compare_with_baseline(*args, **kwargs):
    from experiments.baseline import compare_with_baseline as _compare

    return _compare(*args, **kwargs)


__all__ = ["compare_with_baseline"]
