"""Small Decimal corner calculations; no device adoption or readiness verdict.

Inputs are independent Cartesian bounds. Correlated temperatures or parameters
can make these conservative, not optimistic. Units are SI (ohm, A, V, F, V/s),
except explicitly named Celsius and ppm/C arguments. Strings, integers and
Decimal values are accepted; binary floats and nonfinite values are rejected.
Calculations use 50 significant digits with round-half-even; these are corner
estimates, not formally outward-rounded interval arithmetic at a zero margin.

Sources used for the equations, not a claim of complete circuit qualification:
* TI TPS2597 Rev D, sections 6.5 and 7.3.4.2 (Eq 5: RILM=5747/ILIM),
  and 7.3.8 PGTH: https://www.ti.com/lit/ds/symlink/tps2597.pdf
* UNI-ROYAL thick film V10, section 10: TCR relative to 25 C, separately
  specified soldering/load-life changes of +/-(1%+0.05 ohm):
  https://www.uni-royal.cn/en/images/userfile/file/1753752986c56505e6d9ab55c7.pdf

Stress-test limits are named engineering allowances, not an assertion that a
manufacturer guarantees arbitrary combinations of lifetime environments.
No filesystem reads, source selection, pass flag or release gate is provided.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from itertools import product
from typing import Sequence, Union


Scalar = Union[Decimal, str, int]
PRECISION = 50
ONE = Decimal("1")
ZERO = Decimal("0")


def _decimal(value: Scalar, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, str, int)):
        raise ValueError(f"{name} must be a Decimal, decimal string or integer")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name} is not a decimal number") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def _nonnegative(value: Scalar, name: str) -> Decimal:
    result = _decimal(value, name)
    if result < ZERO:
        raise ValueError(f"{name} must be nonnegative")
    return result


def _positive(value: Scalar, name: str) -> Decimal:
    result = _decimal(value, name)
    if result <= ZERO:
        raise ValueError(f"{name} must be positive")
    return result


def _fraction(value: Scalar, name: str) -> Decimal:
    result = _nonnegative(value, name)
    if result >= ONE:
        raise ValueError(f"{name} must be less than one")
    return result


@dataclass(frozen=True)
class Interval:
    """Finite ordered bounds. Point intervals are valid exact inputs.

Signed intervals are needed for leakage and algebraic voltage residuals;
individual functions enforce positive denominator/physical-input domains.
"""

    minimum: Decimal
    maximum: Decimal

    def __post_init__(self):
        minimum = _decimal(self.minimum, "interval minimum")
        maximum = _decimal(self.maximum, "interval maximum")
        if minimum > maximum:
            raise ValueError("interval minimum exceeds maximum")
        object.__setattr__(self, "minimum", minimum)
        object.__setattr__(self, "maximum", maximum)


def _physical_interval(value: Interval, name: str, allow_zero: bool = False) -> Interval:
    if not isinstance(value, Interval):
        raise ValueError(f"{name} must be an Interval")
    if value.minimum < ZERO or (not allow_zero and value.minimum == ZERO):
        raise ValueError(f"{name} interval must be {'nonnegative' if allow_zero else 'positive'}")
    return value


@dataclass(frozen=True)
class ResistanceDriftBudget:
    """One named sequential +/- (fraction * current resistance + absolute ohm)."""

    name: str
    fraction: Decimal
    absolute_ohm: Decimal = ZERO

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("drift budget needs a nonempty name")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "fraction", _fraction(self.fraction, "drift fraction"))
        object.__setattr__(self, "absolute_ohm", _nonnegative(self.absolute_ohm, "drift absolute ohm"))


def resistor_interval(
    nominal_ohm: Scalar,
    initial_tolerance_fraction: Scalar,
    tcr_ppm_per_c: Scalar,
    temperature_min_c: Scalar,
    temperature_max_c: Scalar,
    drift_budgets: Sequence[ResistanceDriftBudget] = (),
    reference_temperature_c: Scalar = "25",
) -> Interval:
    """Compose initial tolerance, named permanent changes, then TCR once.

Each stress is applied in the declared order at the reference temperature;
its absolute-ohm term is not accidentally converted into a percentage. The
maximum temperature excursion uses both ends, not merely the hot endpoint.
Caller owns valid component temperature range and the chosen stress budget.
"""
    nominal = _positive(nominal_ohm, "nominal resistance")
    tolerance = _fraction(initial_tolerance_fraction, "initial tolerance")
    tcr = _nonnegative(tcr_ppm_per_c, "TCR magnitude")
    cold = _decimal(temperature_min_c, "minimum temperature")
    hot = _decimal(temperature_max_c, "maximum temperature")
    reference = _decimal(reference_temperature_c, "reference temperature")
    if cold > hot:
        raise ValueError("minimum temperature exceeds maximum")
    if not isinstance(drift_budgets, (tuple, list)) or any(not isinstance(b, ResistanceDriftBudget) for b in drift_budgets):
        raise ValueError("drift budgets must be a sequence of named ResistanceDriftBudget values")
    if len({b.name for b in drift_budgets}) != len(drift_budgets):
        raise ValueError("duplicate drift budget name")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        thermal_fraction = tcr * Decimal("0.000001") * max(abs(cold - reference), abs(hot - reference))
        if thermal_fraction >= ONE:
            raise ValueError("TCR excursion must be less than one")
        low, high = nominal * (ONE - tolerance), nominal * (ONE + tolerance)
        for budget in drift_budgets:
            low = low * (ONE - budget.fraction) - budget.absolute_ohm
            high = high * (ONE + budget.fraction) + budget.absolute_ohm
            if low <= ZERO:
                raise ValueError(f"drift budget {budget.name!r} makes resistance nonpositive")
        return Interval(low * (ONE - thermal_fraction), high * (ONE + thermal_fraction))


def efuse_current_interval(
    resistance_ohm: Interval,
    gain_tolerance_fraction: Scalar = "0.10",
    equation_constant_a_ohm: Scalar = "5747",
) -> Interval:
    """TPS2597 Eq 5 with independent gain and resistor corners, in amperes.

The default 10% uses TI's published accuracy claim above ILIM=1.74 A. Caller
must establish that domain and the exact part; this does not promote the
tighter 1.65-kohm datasheet row into an arbitrary-resistance guarantee.
"""
    resistance = _physical_interval(resistance_ohm, "RILM")
    tolerance = _fraction(gain_tolerance_fraction, "gain tolerance")
    constant = _positive(equation_constant_a_ohm, "equation constant")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return Interval(constant * (ONE - tolerance) / resistance.maximum,
                        constant * (ONE + tolerance) / resistance.minimum)


def divider_threshold_interval(
    reference_v: Interval,
    top_ohm: Interval,
    bottom_ohm: Interval,
    leakage_a: Interval = Interval(ZERO, ZERO),
) -> Interval:
    """Rail threshold Vref*(1+Rtop/Rbottom) + Ileak*Rtop.

Positive leakage flows from the divider node into the IC. Enumerate all
corners: with negative leakage, the Rtop derivative can reverse sign. Do not
assume Rtop_max always produces the highest threshold. Results are algebraic;
a nonpositive result exposes an invalid operating assumption, not a clamp.
"""
    reference = _physical_interval(reference_v, "reference voltage")
    top = _physical_interval(top_ohm, "top resistance")
    bottom = _physical_interval(bottom_ohm, "bottom resistance")
    if not isinstance(leakage_a, Interval):
        raise ValueError("signed leakage must be an Interval")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        values = [v * (ONE + rt / rb) + current * rt for v, rt, rb, current in product(
            (reference.minimum, reference.maximum), (top.minimum, top.maximum),
            (bottom.minimum, bottom.maximum), (leakage_a.minimum, leakage_a.maximum),
        )]
        return Interval(min(values), max(values))


@dataclass(frozen=True)
class PowerGoodThresholds:
    rising_v: Interval
    falling_v: Interval


def power_good_thresholds(
    rising_reference_v: Interval,
    falling_reference_v: Interval,
    top_ohm: Interval,
    bottom_ohm: Interval,
    leakage_a: Interval = Interval(ZERO, ZERO),
) -> PowerGoodThresholds:
    """Independent PG rising/falling envelopes, not same-device hysteresis.

Cartesian envelopes may overlap even with positive physical hysteresis;
do not subtract them as if their extreme corners described the same part.
"""
    return PowerGoodThresholds(
        divider_threshold_interval(rising_reference_v, top_ohm, bottom_ohm, leakage_a),
        divider_threshold_interval(falling_reference_v, top_ohm, bottom_ohm, leakage_a),
    )


def rail_series_drop_interval(
    source_v: Interval,
    load_current_a: Interval,
    series_resistance_ohm: Interval,
    distribution_drop_v: Interval = Interval(ZERO, ZERO),
) -> Interval:
    """Residual source voltage minus I*R and independently bounded wiring drop.

Zero current, resistance or distribution drop is valid. Negative inputs are
not; a negative *result* is retained to expose an undeliverable load model.
"""
    source = _physical_interval(source_v, "source voltage")
    current = _physical_interval(load_current_a, "load current", allow_zero=True)
    resistance = _physical_interval(series_resistance_ohm, "series resistance", allow_zero=True)
    drop = _physical_interval(distribution_drop_v, "distribution drop", allow_zero=True)
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return Interval(source.minimum - current.maximum * resistance.maximum - drop.maximum,
                        source.maximum - current.minimum * resistance.minimum - drop.minimum)


def capacitance_interval(
    nominal_f: Scalar,
    initial_tolerance_fraction: Scalar,
    temperature_fraction: Scalar = "0",
) -> Interval:
    """Independent initial and temperature factors, in farads.

No DC-bias retention, aging or effective-capacitance qualification is inferred.
These must be supplied separately by the caller's component model.
"""
    nominal = _positive(nominal_f, "nominal capacitance")
    tolerance = _fraction(initial_tolerance_fraction, "capacitance tolerance")
    temperature = _fraction(temperature_fraction, "capacitance temperature fraction")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return Interval(nominal * (ONE - tolerance) * (ONE - temperature),
                        nominal * (ONE + tolerance) * (ONE + temperature))


def capacitor_slew_interval(charging_current_a: Interval, capacitance_f: Interval) -> Interval:
    """I/C bounds on the charged capacitor's voltage ramp, in V/s.

TPS2597 section 6.5 specifies IdVdt=1.4..5.7 uA. These bounds replace the
nominal 3300/C shortcut; mapping DVDT voltage to OUT slew is a separate
source-follower/transfer assumption, not a guaranteed gain invented here.
"""
    current = _physical_interval(charging_current_a, "charging current")
    capacitance = _physical_interval(capacitance_f, "control capacitance")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return Interval(current.minimum / capacitance.maximum, current.maximum / capacitance.minimum)


def inrush_current_interval(load_capacitance_f: Interval, output_slew_v_per_s: Interval) -> Interval:
    """Cload*dVout/dt, in amperes; excludes live loads and converter startup."""
    capacitance = _physical_interval(load_capacitance_f, "load capacitance")
    slew = _physical_interval(output_slew_v_per_s, "output slew")
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        return Interval(capacitance.minimum * slew.minimum, capacitance.maximum * slew.maximum)
