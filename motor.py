import numpy as np


def load_motor(filepath):
    """Parse a RASP-format (.eng) solid motor thrust-curve file.

    RASP is the standard format used by thrustcurve.org and most rocketry
    simulation software. Format:
        ; comment lines start with a semicolon and are ignored
        name diameter_mm length_mm delays prop_mass_kg total_mass_kg manufacturer
        time_s thrust_N
        time_s thrust_N
        ...
    """
    times = []
    thrusts = []
    header = None

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith(";"):
                continue

            if header is None:
                header = line.split()
                continue

            time_str, thrust_str = line.split()[:2]
            times.append(float(time_str))
            thrusts.append(float(thrust_str))

    name, diameter_mm, length_mm, delays, prop_mass_kg, total_mass_kg, manufacturer = header

    times = np.array(times)
    thrusts = np.array(thrusts)

    # Total impulse = area under the thrust-vs-time curve (trapezoidal rule):
    # approximate each segment between two data points as a trapezoid and
    # sum their areas.
    dt = np.diff(times)
    avg_thrust = (thrusts[:-1] + thrusts[1:]) / 2
    segment_impulse = avg_thrust * dt

    # Cumulative impulse delivered by each point in time (running total),
    # so we can look up "how much impulse has been delivered by time t" at
    # ANY t, not just the coarse steps of one particular simulation's dt.
    cumulative_impulse = np.concatenate(([0.0], np.cumsum(segment_impulse)))
    total_impulse = cumulative_impulse[-1]

    return {
        "name": name,
        "diameter_mm": float(diameter_mm),
        "length_mm": float(length_mm),
        "prop_mass_kg": float(prop_mass_kg),
        "total_mass_kg": float(total_mass_kg),
        "manufacturer": manufacturer,
        "times": times,
        "thrusts": thrusts,
        "cumulative_impulse": cumulative_impulse,
        "total_impulse": total_impulse,
        "burn_time": times[-1],
    }


def thrust_at(t, motor):
    """Look up thrust at time t by interpolating the motor's thrust curve."""
    return np.interp(t, motor["times"], motor["thrusts"], left=0.0, right=0.0)


def mass_at(t, motor, airframe_mass):
    """Total vehicle mass at time t: fixed airframe + motor casing + remaining propellant."""
    cum_impulse = np.interp(
        t, motor["times"], motor["cumulative_impulse"],
        left=0.0, right=motor["total_impulse"],
    )
    propellant_burned = motor["prop_mass_kg"] * min(1.0, cum_impulse / motor["total_impulse"])
    return airframe_mass + motor["total_mass_kg"] - propellant_burned
