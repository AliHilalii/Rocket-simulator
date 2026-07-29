import matplotlib.pyplot as plt

from phase1_vertical_launch import gravity, air_density, drag_force
from motor import load_motor, thrust_at

# Airframe properties
AIRFRAME_MASS = 1.2   # kg - body tube, fins, nose cone, recovery gear, payload
CD     = 0.5
RADIUS = 0.04         # m
AREA   = 3.14159265 * RADIUS ** 2

MOTOR_FILE = "motors/sample_motor.eng"

DT    = 0.01
T_MAX = 1000.0


def simulate(motor):
    """Run the 1D vertical flight simulation using a real motor thrust curve."""
    t = 0.0
    altitude = 0.0
    velocity = 0.0
    impulse_so_far = 0.0

    history = {
        "time": [], "altitude": [], "velocity": [],
        "mass": [], "thrust": [], "drag": [],
    }

    while t < T_MAX:
        F_thrust = thrust_at(t, motor)
        impulse_so_far += F_thrust * DT

        propellant_burned = motor["prop_mass_kg"] * min(1.0, impulse_so_far / motor["total_impulse"])
        motor_mass = motor["total_mass_kg"] - propellant_burned
        mass = AIRFRAME_MASS + motor_mass

        g = gravity(altitude)
        F_drag = drag_force(velocity, altitude, Cd=CD, area=AREA)

        F_net = F_thrust + F_drag - mass * g
        acceleration = F_net / mass

        velocity += acceleration * DT
        altitude += velocity * DT

        if altitude < 0 and t > 0:
            break

        history["time"].append(t)
        history["altitude"].append(altitude)
        history["velocity"].append(velocity)
        history["mass"].append(mass)
        history["thrust"].append(F_thrust)
        history["drag"].append(F_drag)

        t += DT

    return history


def print_summary(history, motor):
    altitudes = history["altitude"]
    velocities = history["velocity"]
    times = history["time"]

    apogee_idx = altitudes.index(max(altitudes))

    print(f"Motor:         {motor['name']} ({motor['manufacturer']})")
    print(f"Total impulse: {motor['total_impulse']:.1f} N*s")
    print(f"Burn time:     {motor['burn_time']:.2f} s")
    print(f"Max altitude:  {max(altitudes):.1f} m")
    print(f"Max velocity:  {max(velocities):.1f} m/s")
    print(f"Apogee at:     {times[apogee_idx]:.2f} s")
    print(f"Flight time:   {times[-1]:.2f} s")


def plot_results(history, save_path="rocket_phase2_results.png"):
    times = history["time"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    axes[0, 0].plot(times, history["altitude"])
    axes[0, 0].set(xlabel="Time (s)", ylabel="Altitude (m)", title="Altitude")
    axes[0, 0].grid(True)

    axes[0, 1].plot(times, history["velocity"], color="orange")
    axes[0, 1].set(xlabel="Time (s)", ylabel="Velocity (m/s)", title="Velocity")
    axes[0, 1].grid(True)

    axes[1, 0].plot(times, history["thrust"], color="red")
    axes[1, 0].set(xlabel="Time (s)", ylabel="Thrust (N)", title="Motor Thrust Curve")
    axes[1, 0].grid(True)

    axes[1, 1].plot(times, history["mass"], color="green")
    axes[1, 1].set(xlabel="Time (s)", ylabel="Mass (kg)", title="Vehicle Mass")
    axes[1, 1].grid(True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()


def main():
    motor = load_motor(MOTOR_FILE)
    history = simulate(motor)
    print_summary(history, motor)
    plot_results(history)


if __name__ == "__main__":
    main()
