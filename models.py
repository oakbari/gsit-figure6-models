"""Analytic models for generic ngSIT parameter sweeps.

No functions in this module read experimental data or fit parameters.
Inputs may be scalars or NumPy-broadcastable arrays.
"""
import numpy as np


def _finite(name, value, lower=0.0, upper=None):
    value = np.asarray(value, dtype=float)
    if np.any(~np.isfinite(value)) or np.any(value < lower):
        raise ValueError(f"{name} must be finite and >= {lower}")
    if upper is not None and np.any(value > upper):
        raise ValueError(f"{name} must be <= {upper}")
    return value


def reproductive_output(c, r, f):
    """Relative viable-offspring output G=(1+crf)/(1+cr)."""
    c = _finite("c", c)
    r = _finite("r", r)
    f = _finite("f", f, upper=1.0)
    return (1.0 + c * r * f) / (1.0 + c * r)


def reproductive_threshold(c, f, target):
    """Minimum r for a target reproductive reduction; infinity if infeasible.

    Floating-point margins within eight machine epsilons of zero are treated
    as the analytic feasibility boundary, including f=0.05 for target=0.95.
    """
    c = _finite("c", c)
    f = _finite("f", f, upper=1.0)
    target = _finite("target", target, upper=1.0)
    if np.any((target <= 0) | (target >= 1)):
        raise ValueError("target must be strictly between 0 and 1")
    c, f, target = np.broadcast_arrays(c, f, target)
    margin = 1.0 - target - f
    valid = (c > 0) & (margin > 8 * np.finfo(float).eps)
    return np.divide(target, c * margin,
                     out=np.full(c.shape, np.inf), where=valid)


def population_threshold(c, f, R0, a=None):
    """Maintained-ratio boundary for the illustrative population model.

    a=None: require r STRICTLY GREATER than the returned boundary for R0*G<1.
    0<a<1: require r AT LEAST the returned ratio for equilibrium F*/K<=a.
    Infinity means no finite ratio meets the stated condition.
    """
    R0 = _finite("R0", R0, lower=1.0)
    if np.any(R0 <= 1):
        raise ValueError("R0 must be greater than 1")
    if a is None:
        H = R0
    else:
        a = _finite("a", a, upper=1.0)
        if np.any((a <= 0) | (a >= 1)):
            raise ValueError("a must be strictly between 0 and 1")
        H = R0 - a * (R0 - 1.0)
    return reproductive_threshold(c, f, 1.0 - 1.0 / H)


def population_equilibrium(g, R0):
    """Nonnegative equilibrium female fraction F*/K, with no immigration.

    Uses recruitment F_next=R0*g*F/[1+(R0-1)*g*F/K]. A zero equilibrium
    is a deterministic model result, not an extinction probability.
    """
    g = _finite("g", g, upper=1.0)
    R0 = _finite("R0", R0, lower=1.0)
    if np.any(R0 <= 1):
        raise ValueError("R0 must be greater than 1")
    g, R0 = np.broadcast_arrays(g, R0)
    value = np.divide(R0 * g - 1, (R0 - 1) * g,
                      out=np.zeros(g.shape), where=g > 0)
    return np.maximum(0.0, value)
