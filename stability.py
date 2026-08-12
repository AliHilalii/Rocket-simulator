import numpy as np

# Fraction of nose cone length where ITS OWN center of pressure sits,
# per the Barrowman method (depends only on nose shape).
NOSE_CP_FRACTION = {
    "conical": 0.666,
    "ogive": 0.466,
}


def fin_normal_coefficient(fin_count, span, body_radius, root_chord, tip_chord, sweep_length):
    """CN_alpha contribution of a set of trapezoidal fins (Barrowman method)."""
    numerator = 4 * fin_count * (span / (2 * body_radius)) ** 2
    denominator = 1 + np.sqrt(1 + (2 * sweep_length / (root_chord + tip_chord)) ** 2)
    body_interference = 1 + body_radius / (span + body_radius)
    return body_interference * numerator / denominator


def fin_cp_offset(root_chord, tip_chord, sweep_length):
    """Distance from the fin ROOT leading edge back to the fins' own center of pressure."""
    term1 = sweep_length * (root_chord + 2 * tip_chord) / (3 * (root_chord + tip_chord))
    term2 = (root_chord + tip_chord - (root_chord * tip_chord) / (root_chord + tip_chord)) / 6
    return term1 + term2


def calculate_cp(rocket):
    """Estimate the rocket's overall center of pressure (Barrowman method),
    measured in meters from the nose tip. `rocket` describes its geometry."""
    R = rocket["body_diameter"] / 2

    CN_nose = 2.0
    X_nose = NOSE_CP_FRACTION[rocket["nose_type"]] * rocket["nose_length"]

    CN_fins = fin_normal_coefficient(
        rocket["fin_count"], rocket["fin_span"], R,
        rocket["fin_root_chord"], rocket["fin_tip_chord"], rocket["fin_sweep_length"],
    )
    X_fins = rocket["fin_position"] + fin_cp_offset(
        rocket["fin_root_chord"], rocket["fin_tip_chord"], rocket["fin_sweep_length"],
    )

    CN_total = CN_nose + CN_fins
    return (CN_nose * X_nose + CN_fins * X_fins) / CN_total


def static_margin(cp, cg, diameter):
    """Static margin in calibers (body diameters). Stable if positive;
    1-2 calibers is the typical safe target."""
    return (cp - cg) / diameter


def describe_stability(margin):
    if margin < 0:
        return "UNSTABLE - center of pressure is ahead of center of gravity, rocket will tumble"
    if margin < 1.0:
        return "MARGINAL - technically stable but not enough margin for a safe flight"
    if margin <= 2.0:
        return "STABLE - good margin, typical safe design target"
    return "OVERSTABLE - very stable but will weathercock heavily into wind"
