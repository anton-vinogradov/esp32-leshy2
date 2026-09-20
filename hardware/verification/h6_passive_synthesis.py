"""Exact inverse divider bounds; no preferred-value or component acceptance.

Inputs describe independent Cartesian bounds for the conditional equation
V = Vref * (1 + Rnom * factor / Rbottom) + Ileak * Rnom * factor.
Positive leakage flows into the IC. The caller supplies leakage explicitly,
including an explicit zero interval for a diagnostic that excludes it.
Top factors must include every modeled multiplicative tolerance and drift;
absolute-ohm drift is not represented by a nominal-independent factor.

Finite Decimal inputs become exact rational numbers before inversion. This
does not improve the accuracy or applicability of the supplied source bounds,
select a preferred value, or qualify a physical feedback loop.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Optional

from h6_power_corner_math import Interval, Scalar, _decimal, _physical_interval


@dataclass(frozen=True)
class NominalWindow:
    """Inclusive bounds intersected with the strictly positive resistor domain.

Zero is an excluded lower endpoint when minimum_ohm is zero. None means no
upper bound. Incompatible bounds are retained, never reordered into a range.
"""

    minimum_ohm: Fraction
    maximum_ohm: Optional[Fraction]
    infeasible_reason: Optional[str] = None

    @property
    def feasible(self) -> bool:
        return self.infeasible_reason is None and (
            self.maximum_ohm is None
            or self.maximum_ohm > 0 and self.minimum_ohm <= self.maximum_ohm
        )


def feedback_top_window(
    reference_v: Interval,
    bottom_ohm: Interval,
    top_factors: Interval,
    required_min_v: Scalar,
    required_max_v: Scalar,
    leakage_a: Interval,
) -> NominalWindow:
    """Intersect both voltage inequalities at every independent corner.

Signed or zero slopes are handled without assuming that increasing the top
resistor increases voltage. Inverted requirements are valid infeasibility
evidence; malformed/nonfinite inputs and nonpositive physical bounds raise.
"""
    reference = _physical_interval(reference_v, "reference voltage")
    bottom = _physical_interval(bottom_ohm, "bottom resistance")
    factors = _physical_interval(top_factors, "top resistance factor")
    if not isinstance(leakage_a, Interval):
        raise ValueError("signed leakage must be an Interval")
    required_min = Fraction(_decimal(required_min_v, "required minimum voltage"))
    required_max = Fraction(_decimal(required_max_v, "required maximum voltage"))
    if required_min > required_max:
        return NominalWindow(Fraction(0), Fraction(0), "required_minimum_exceeds_maximum")

    lower, upper = Fraction(0), None
    corners = product(*[(Fraction(interval.minimum), Fraction(interval.maximum))
                        for interval in (reference, bottom, factors, leakage_a)])
    for vref, rb, factor, leakage in corners:
        slope = factor * (vref / rb + leakage)
        if slope == 0:
            if not required_min <= vref <= required_max:
                return NominalWindow(Fraction(0), Fraction(0), "zero_slope_corner_outside_requirements")
            continue
        corner_lower = (required_min - vref) / slope
        corner_upper = (required_max - vref) / slope
        if slope < 0:
            corner_lower, corner_upper = corner_upper, corner_lower
        lower = max(lower, corner_lower)
        upper = corner_upper if upper is None else min(upper, corner_upper)

    reason = None
    if upper is not None and upper <= 0:
        reason = "no_strictly_positive_resistance"
    elif upper is not None and lower > upper:
        reason = "incompatible_corner_bounds"
    return NominalWindow(lower, upper, reason)
