from stability import calculate_cp, static_margin, describe_stability

# Example rocket geometry (roughly matching the 8 cm diameter airframe
# used in Phases 2-4), all distances in meters, measured from the nose tip.
ROCKET = {
    "body_diameter":   0.08,
    "nose_length":     0.15,
    "nose_type":       "ogive",
    "fin_count":       3,
    "fin_root_chord":  0.12,
    "fin_tip_chord":   0.05,
    "fin_span":        0.08,
    "fin_sweep_length": 0.06,
    "fin_position":    0.90,   # distance from nose tip to fin root leading edge
}

CENTER_OF_GRAVITY = 0.62   # meters from nose tip - estimate (motor near tail pulls this back)


def main():
    cp = calculate_cp(ROCKET)
    margin = static_margin(cp, CENTER_OF_GRAVITY, ROCKET["body_diameter"])

    print(f"Center of pressure:  {cp:.3f} m from nose tip")
    print(f"Center of gravity:   {CENTER_OF_GRAVITY:.3f} m from nose tip")
    print(f"Static margin:       {margin:.2f} calibers")
    print(f"Verdict:             {describe_stability(margin)}")


if __name__ == "__main__":
    main()
