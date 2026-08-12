import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from phase1_vertical_launch import gravity
from atmosphere import air_density
from motor import load_motor, thrust_at, mass_at

# --- Airframe properties ---
AIRFRAME_MASS = 1.2
CD     = 0.5
RADIUS = 0.04
AREA   = 3.14159265 * RADIUS ** 2

# --- Parachute properties ---
CHUTE_CD       = 1.5
CHUTE_DIAMETER = 1.0   # m
CHUTE_AREA     = 3.14159265 * (CHUTE_DIAMETER / 2) ** 2

MOTOR_FILE = "motors/sample_motor.eng"

RAIL_ANGLE_DEG = 5.0
WIND = np.array([5.0, 0.0, 0.0])

DT    = 0.01
T_MAX = 1000.0

_angle = np.radians(RAIL_ANGLE_DEG)
LAUNCH_DIRECTION = np.array([np.sin(_angle), 0.0, np.cos(_angle)])


def derivatives(t, state, motor, chute_deployed):
    position = state[:3]
    velocity = state[3:]
    altitude = max(position[2], 0.0)

    mass = mass_at(t, motor, AIRFRAME_MASS)
    F_thrust = thrust_at(t, motor) * LAUNCH_DIRECTION

    v_rel = velocity - WIND
    speed_rel = np.linalg.norm(v_rel)
    rho = air_density(altitude)

    Cd_eff, area_eff = (CHUTE_CD, CHUTE_AREA) if chute_deployed else (CD, AREA)
    if speed_rel > 0:
        F_drag = -0.5 * rho * speed_rel * Cd_eff * area_eff * v_rel
    else:
        F_drag = np.zeros(3)

    F_gravity = np.array([0.0, 0.0, -mass * gravity(altitude)])
    acceleration = (F_thrust + F_drag + F_gravity) / mass

    return np.concatenate([velocity, acceleration])


def rk4_step(t, state, dt, motor, chute_deployed):
    k1 = derivatives(t, state, motor, chute_deployed)
    k2 = derivatives(t + dt / 2, state + dt / 2 * k1, motor, chute_deployed)
    k3 = derivatives(t + dt / 2, state + dt / 2 * k2, motor, chute_deployed)
    k4 = derivatives(t + dt, state + dt * k3, motor, chute_deployed)
    return state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(motor):
    t = 0.0
    state = np.zeros(6)
    chute_deployed = False
    chute_deploy_time = None

    history = {"time": [], "x": [], "y": [], "z": [], "speed": [], "chute": []}

    while t < T_MAX:
        prev_z = state[2]
        state = rk4_step(t, state, DT, motor, chute_deployed)
        t += DT

        if not chute_deployed and t > motor["burn_time"] and state[2] < prev_z:
            chute_deployed = True
            chute_deploy_time = t

        if state[2] < 0 and t > DT:
            break

        history["time"].append(t)
        history["x"].append(state[0])
        history["y"].append(state[1])
        history["z"].append(state[2])
        history["speed"].append(np.linalg.norm(state[3:]))
        history["chute"].append(chute_deployed)

    history["chute_deploy_time"] = chute_deploy_time
    return history


def print_summary(history):
    z = history["z"]
    times = history["time"]
    apogee_idx = z.index(max(z))

    landing_speed = history["speed"][-1]

    print(f"Max altitude:        {max(z):.1f} m")
    print(f"Apogee at:           {times[apogee_idx]:.2f} s")
    print(f"Chute deployed at:   {history['chute_deploy_time']:.2f} s")
    print(f"Landing speed:       {landing_speed:.1f} m/s "
          f"({'SAFE' if landing_speed < 10 else 'TOO FAST - increase chute size'})")
    print(f"Flight time:         {times[-1]:.2f} s")


def plot_results(history, save_path="rocket_phase6_results.png"):
    times = history["time"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(times, history["z"])
    axes[0].axvline(history["chute_deploy_time"], color="red", linestyle="--", label="Chute deploy")
    axes[0].set(xlabel="Time (s)", ylabel="Altitude (m)", title="Altitude (with recovery)")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(times, history["speed"], color="orange")
    axes[1].axvline(history["chute_deploy_time"], color="red", linestyle="--", label="Chute deploy")
    axes[1].set(xlabel="Time (s)", ylabel="Speed (m/s)", title="Speed (with recovery)")
    axes[1].legend()
    axes[1].grid(True)

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
