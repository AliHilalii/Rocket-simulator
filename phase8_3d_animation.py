import numpy as np
import pyvista as pv

from phase6_recovery import simulate
from motor import load_motor
from rocket_mesh import build_rocket_mesh, place_rocket

MOTOR_FILE = "motors/sample_motor.eng"

# The full flight (with slow parachute descent) lasts ~11 minutes - we only
# animate the visually interesting part: launch, apogee, chute deployment,
# and the start of descent. See Phase 6's plots for the complete picture.
ANIMATION_DURATION = 60.0   # seconds of flight to animate
N_FRAMES = 150
OUTPUT_FILE = "rocket_flight_3d.gif"


def main():
    motor = load_motor(MOTOR_FILE)
    history = simulate(motor)

    times = np.array(history["time"])
    xs = np.array(history["x"])
    ys = np.array(history["y"])
    zs = np.array(history["z"])

    mask = times <= ANIMATION_DURATION
    times, xs, ys, zs = times[mask], xs[mask], ys[mask], zs[mask]

    frame_indices = np.linspace(0, len(times) - 1, N_FRAMES).astype(int)

    rocket_mesh = build_rocket_mesh()

    plotter = pv.Plotter(off_screen=True, window_size=(900, 700))
    plotter.set_background("white")

    ground = pv.Plane(center=(0, 0, 0), i_size=3000, j_size=3000)

    plotter.open_gif(OUTPUT_FILE, fps=15)

    trail_points = []

    for idx in frame_indices:
        position = np.array([xs[idx], ys[idx], zs[idx]])

        # Central difference for a robust direction estimate even at the
        # very first/last frame (avoids a zero-length vector at the end).
        prev_idx = max(idx - 1, 0)
        next_idx = min(idx + 1, len(xs) - 1)
        direction = np.array([
            xs[next_idx] - xs[prev_idx],
            ys[next_idx] - ys[prev_idx],
            zs[next_idx] - zs[prev_idx],
        ])
        if np.linalg.norm(direction) < 1e-6:
            direction = np.array([0.0, 0.0, 1.0])

        rocket_now = place_rocket(rocket_mesh, position, direction)

        plotter.clear_actors()
        plotter.add_mesh(ground, color="lightgreen", opacity=0.4)
        plotter.add_mesh(rocket_now, color="orange")

        trail_points.append(position)
        if len(trail_points) > 1:
            trail = pv.lines_from_points(np.array(trail_points))
            plotter.add_mesh(trail, color="blue", line_width=2)

        camera_offset = np.array([-8.0, -8.0, 4.0])
        plotter.camera.position = tuple(position + camera_offset)
        plotter.camera.focal_point = tuple(position)
        plotter.camera.up = (0.0, 0.0, 1.0)

        plotter.write_frame()

    plotter.close()
    print(f"Saved {OUTPUT_FILE} ({len(frame_indices)} frames, "
          f"covering the first {ANIMATION_DURATION:.0f}s of flight)")
    print("The full flight continues much longer under slow parachute descent - "
          "see Phase 6's altitude/speed plots for that part.")


if __name__ == "__main__":
    main()
