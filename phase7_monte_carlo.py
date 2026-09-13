import numpy as np
import matplotlib.pyplot as plt

from phase1_vertical_launch import gravity
from atmosphere import air_density
from motor import load_motor, thrust_at, mass_at

# --- Airframe / parachute properties (same as Phase 6) ---
AIRFRAME_MASS = 1.2
CD, RADIUS = 0.5, 0.04
AREA = 3.14159265 * RADIUS ** 2
CHUTE_CD, CHUTE_DIAMETER = 1.5, 1.0
CHUTE_AREA = 3.14159265 * (CHUTE_DIAMETER / 2) ** 2

MOTOR_FILE = "motors/sample_motor.eng"

DT          = 0.02   # timestep during powered flight/coast (needs precision)
DT_DESCENT  = 0.5    # coarser timestep once the chute is out (near-constant velocity,
                      # doesn't need fine resolution - this is what makes 100s of trials feasible)
T_MAX = 1000.0

N_TRIALS = 200
WIND_SPEED_MEAN = 5.0   # m/s
WIND_SPEED_STD  = 2.0   # m/s - trial-to-trial randomness in wind strength
RAIL_ANGLE_MEAN = 5.0   # degrees
RAIL_ANGLE_STD  = 1.0   # degrees - small launch-rail pointing error


def derivatives(t, state, motor, wind, launch_direction, chute_deployed):
    position = state[:3]
    velocity = state[3:]
    altitude = max(position[2], 0.0)

    mass = mass_at(t, motor, AIRFRAME_MASS)
    F_thrust = thrust_at(t, motor) * launch_direction

    v_rel = velocity - wind
    speed_rel = np.linalg.norm(v_rel)
    rho = air_density(altitude)
    Cd_eff, area_eff = (CHUTE_CD, CHUTE_AREA) if chute_deployed else (CD, AREA)
    F_drag = -0.5 * rho * speed_rel * Cd_eff * area_eff * v_rel if speed_rel > 0 else np.zeros(3)

    F_gravity = np.array([0.0, 0.0, -mass * gravity(altitude)])
    return np.concatenate([velocity, (F_thrust + F_drag + F_gravity) / mass])


def rk4_step(t, state, dt, motor, wind, launch_direction, chute_deployed):
    k1 = derivatives(t, state, motor, wind, launch_direction, chute_deployed)
    k2 = derivatives(t + dt / 2, state + dt / 2 * k1, motor, wind, launch_direction, chute_deployed)
    k3 = derivatives(t + dt / 2, state + dt / 2 * k2, motor, wind, launch_direction, chute_deployed)
    k4 = derivatives(t + dt, state + dt * k3, motor, wind, launch_direction, chute_deployed)
    return state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate_one_flight(motor, wind, rail_angle_deg):
    """Run one full flight and return the landing (x, y) position."""
    angle = np.radians(rail_angle_deg)
    launch_direction = np.array([np.sin(angle), 0.0, np.cos(angle)])

    t = 0.0
    state = np.zeros(6)
    chute_deployed = False

    while t < T_MAX:
        prev_z = state[2]
        dt = DT_DESCENT if chute_deployed else DT
        state = rk4_step(t, state, dt, motor, wind, launch_direction, chute_deployed)
        t += dt

        if not chute_deployed and t > motor["burn_time"] and state[2] < prev_z:
            chute_deployed = True

        if state[2] < 0 and t > dt:
            break

    return state[0], state[1]


def run_monte_carlo(motor):
    """Run N_TRIALS flights, each with randomized wind and launch angle."""
    landing_x = []
    landing_y = []

    for i in range(N_TRIALS):
        wind_speed = np.random.normal(WIND_SPEED_MEAN, WIND_SPEED_STD)
        wind_dir = np.random.uniform(0, 2 * np.pi)
        wind = np.array([wind_speed * np.cos(wind_dir), wind_speed * np.sin(wind_dir), 0.0])

        rail_angle = np.random.normal(RAIL_ANGLE_MEAN, RAIL_ANGLE_STD)

        x, y = simulate_one_flight(motor, wind, rail_angle)
        landing_x.append(x)
        landing_y.append(y)

    return np.array(landing_x), np.array(landing_y)


def print_summary(landing_x, landing_y):
    distances = np.sqrt(landing_x ** 2 + landing_y ** 2)
    print(f"Trials:                  {len(landing_x)}")
    print(f"Mean landing point:      ({landing_x.mean():.1f}, {landing_y.mean():.1f}) m")
    print(f"Std dev (x, y):          ({landing_x.std():.1f}, {landing_y.std():.1f}) m")
    print(f"Mean distance from pad:  {distances.mean():.1f} m")
    print(f"95th percentile radius:  {np.percentile(distances, 95):.1f} m  <- suggested recovery/safety radius")


def plot_results(landing_x, landing_y, save_path="rocket_phase7_dispersion.png"):
    plt.figure(figsize=(7, 7))
    plt.scatter(landing_x, landing_y, alpha=0.5, s=15)
    plt.scatter([0], [0], color="red", marker="^", s=100, label="Launch pad")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title(f"Landing Dispersion ({len(landing_x)} simulated flights)")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()


def main():
    motor = load_motor(MOTOR_FILE)
    landing_x, landing_y = run_monte_carlo(motor)
    print_summary(landing_x, landing_y)
    plot_results(landing_x, landing_y)


if __name__ == "__main__":
    main()
