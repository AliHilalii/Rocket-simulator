import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (registers 3D projection)

from phase1_vertical_launch import gravity
from atmosphere import air_density
from motor import load_motor, thrust_at, mass_at

# --- Airframe properties ---
AIRFRAME_MASS = 1.2   # kg
CD     = 0.5
RADIUS = 0.04         # m
AREA   = 3.14159265 * RADIUS ** 2

MOTOR_FILE = "motors/sample_motor.eng"

# --- Launch conditions ---
RAIL_ANGLE_DEG = 5.0            # tilt from vertical, degrees
WIND = np.array([5.0, 0.0, 0.0])  # constant horizontal wind vector, m/s

DT    = 0.01
T_MAX = 1000.0

_angle = np.radians(RAIL_ANGLE_DEG)
LAUNCH_DIRECTION = np.array([np.sin(_angle), 0.0, np.cos(_angle)])


def derivatives(t, state, motor):
    """Given [x, y, z, vx, vy, vz] at time t, return its rate of change."""
    position = state[:3]
    velocity = state[3:]
    altitude = max(position[2], 0.0)

    mass = mass_at(t, motor, AIRFRAME_MASS)

    F_thrust = thrust_at(t, motor) * LAUNCH_DIRECTION

    v_rel = velocity - WIND
    speed_rel = np.linalg.norm(v_rel)
    rho = air_density(altitude)
    if speed_rel > 0:
        F_drag = -0.5 * rho * speed_rel * CD * AREA * v_rel
    else:
        F_drag = np.zeros(3)

    F_gravity = np.array([0.0, 0.0, -mass * gravity(altitude)])

    acceleration = (F_thrust + F_drag + F_gravity) / mass

    return np.concatenate([velocity, acceleration])


def rk4_step(t, state, dt, motor):
    """One 4th-order Runge-Kutta integration step."""
    k1 = derivatives(t, state, motor)
    k2 = derivatives(t + dt / 2, state + dt / 2 * k1, motor)
    k3 = derivatives(t + dt / 2, state + dt / 2 * k2, motor)
    k4 = derivatives(t + dt, state + dt * k3, motor)
    return state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(motor):
    t = 0.0
    state = np.zeros(6)  # x, y, z, vx, vy, vz

    history = {"time": [], "x": [], "y": [], "z": [], "speed": []}

    while t < T_MAX:
        state = rk4_step(t, state, DT, motor)
        t += DT

        if state[2] < 0 and t > DT:
            break

        history["time"].append(t)
        history["x"].append(state[0])
        history["y"].append(state[1])
        history["z"].append(state[2])
        history["speed"].append(np.linalg.norm(state[3:]))

    return history


def print_summary(history):
    z = history["z"]
    x = history["x"]
    times = history["time"]
    apogee_idx = z.index(max(z))

    print(f"Max altitude:    {max(z):.1f} m")
    print(f"Max speed:       {max(history['speed']):.1f} m/s")
    print(f"Apogee at:       {times[apogee_idx]:.2f} s")
    print(f"Downrange drift: {x[-1]:.1f} m (due to launch angle + wind)")
    print(f"Flight time:     {times[-1]:.2f} s")


def plot_results(history, save_path="rocket_phase4_results.png"):
    times = history["time"]
    fig = plt.figure(figsize=(12, 8))

    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    ax1.plot(history["x"], history["y"], history["z"])
    ax1.set(xlabel="X (m)", ylabel="Y (m)", zlabel="Altitude (m)", title="3D Trajectory")

    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(times, history["z"])
    ax2.set(xlabel="Time (s)", ylabel="Altitude (m)", title="Altitude")
    ax2.grid(True)

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(times, history["speed"], color="orange")
    ax3.set(xlabel="Time (s)", ylabel="Speed (m/s)", title="Speed")
    ax3.grid(True)

    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(history["x"], history["z"], color="green")
    ax4.set(xlabel="Downrange X (m)", ylabel="Altitude (m)", title="Side Profile")
    ax4.grid(True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()


def main():
    motor = load_motor(MOTOR_FILE)
    history = simulate(motor)
    print_summary(history)
    plot_results(history)


if __name__ == "__main__":
    main()
