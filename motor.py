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
    total_impulse = np.sum(avg_thrust * dt)

    return {
        "name": name,
        "diameter_mm": float(diameter_mm),
        "length_mm": float(length_mm),
        "prop_mass_kg": float(prop_mass_kg),
        "total_mass_kg": float(total_mass_kg),
        "manufacturer": manufacturer,
        "times": times,
        "thrusts": thrusts,
        "total_impulse": total_impulse,
        "burn_time": times[-1],
    }


def thrust_at(t, motor):
    """Look up thrust at time t by interpolating the motor's thrust curve."""
    return np.interp(t, motor["times"], motor["thrusts"], left=0.0, right=0.0)
