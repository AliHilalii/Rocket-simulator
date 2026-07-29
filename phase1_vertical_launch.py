import numpy as np
import matplotlib.pyplot as plt

# --- Rocket properties ---
DRY_MASS  = 500.0      # kg
FUEL_MASS = 2000.0     # kg
THRUST    = 60000.0    # N
BURN_RATE = 20.0       # kg/s

CD     = 0.3
RADIUS = 0.5                  # m
AREA   = np.pi * RADIUS ** 2  # m^2

# --- Environment properties ---
G0      = 9.81       # m/s^2, surface gravity
R_EARTH = 6.371e6    # m, Earth's radius
RHO0    = 1.225      # kg/m^3, sea-level air density
H       = 8500.0     # m, atmospheric scale height

# --- Simulation settings ---
DT    = 0.01
T_MAX = 1000.0


def gravity(altitude):
    """Gravitational acceleration at a given altitude (inverse-square law)."""
    return G0 * (R_EARTH / (R_EARTH + altitude)) ** 2


def air_density(altitude):
    """Air density at a given altitude (exponential atmosphere model)."""
    return RHO0 * np.exp(-altitude / H)


def drag_force(velocity, altitude):
    """Aerodynamic drag force, always opposing the current velocity."""
    rho = air_density(altitude)
    return -0.5 * rho * velocity * abs(velocity) * CD * AREA


def thrust_force(fuel_remaining):
    """Engine thrust: full thrust while fuel remains, zero once empty."""
    return THRUST if fuel_remaining > 0 else 0.0


def simulate():
    """Run the 1D vertical flight simulation and return the recorded history."""
    t = 0.0
    altitude = 0.0
    velocity = 0.0
    fuel = FUEL_MASS

    history = {
        "time": [], "altitude": [], "velocity": [], "mass": [],
        "drag": [], "density": [], "gravity": [],
    }

    while t < T_MAX:
        mass = DRY_MASS + fuel
        g = gravity(altitude)
        F_drag = drag_force(velocity, altitude)
        F_thrust = thrust_force(fuel)

        if fuel > 0:
            fuel = max(0.0, fuel - BURN_RATE * DT)

        F_net = F_thrust + F_drag - mass * g
        acceleration = F_net / mass

        velocity += acceleration * DT
        altitude += velocity * DT

        if altitude < 0:
            break

        history["time"].append(t)
        history["altitude"].append(altitude)
        history["velocity"].append(velocity)
        history["mass"].append(mass)
        history["drag"].append(F_drag)
        history["density"].append(air_density(altitude))
        history["gravity"].append(g)

        t += DT

    return history


def print_summary(history):
    """Print key flight statistics from a simulation history."""
    altitudes = history["altitude"]
    velocities = history["velocity"]
    times = history["time"]
    drags = history["drag"]

    apogee_idx = altitudes.index(max(altitudes))

    print(f"Max altitude:  {max(altitudes) / 1000:.2f} km")
    print(f"Max velocity:  {max(velocities):.2f} m/s")
    print(f"Apogee at:     {times[apogee_idx]:.1f} s")
    print(f"Flight time:   {times[-1]:.1f} s")
    print(f"Peak drag:     {min(drags) / 1000:.1f} kN")


def plot_results(history, save_path="rocket_v2_results.png"):
    """Plot altitude, velocity, mass, drag, density, and gravity vs time."""
    times = history["time"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))

    axes[0, 0].plot(times, np.array(history["altitude"]) / 1000)
    axes[0, 0].set(xlabel="Time (s)", ylabel="Altitude (km)", title="Altitude")
    axes[0, 0].grid(True)

    axes[0, 1].plot(times, history["velocity"], color="orange")
    axes[0, 1].set(xlabel="Time (s)", ylabel="Velocity (m/s)", title="Velocity")
    axes[0, 1].grid(True)

    axes[0, 2].plot(times, history["mass"], color="green")
    axes[0, 2].set(xlabel="Time (s)", ylabel="Mass (kg)", title="Mass")
    axes[0, 2].grid(True)

    axes[1, 0].plot(times, np.array(history["drag"]) / 1000, color="red")
    axes[1, 0].set(xlabel="Time (s)", ylabel="Drag (kN)", title="Drag force")
    axes[1, 0].grid(True)

    axes[1, 1].plot(times, history["density"], color="purple")
    axes[1, 1].set(xlabel="Time (s)", ylabel="Density (kg/m³)", title="Air density")
    axes[1, 1].grid(True)

    axes[1, 2].plot(times, history["gravity"], color="brown")
    axes[1, 2].set(xlabel="Time (s)", ylabel="g (m/s²)", title="Gravity")
    axes[1, 2].grid(True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()


def main():
    history = simulate()
    print_summary(history)
    plot_results(history)


if __name__ == "__main__":
    main()
