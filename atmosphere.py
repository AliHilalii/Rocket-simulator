import numpy as np

# NASA/ICAO International Standard Atmosphere constants
G0 = 9.80665       # m/s^2, standard gravity used to define the model
R  = 8.31446       # J/(mol*K), universal gas constant
M  = 0.0289644     # kg/mol, molar mass of air
T0 = 288.15        # K, sea-level standard temperature
P0 = 101325.0      # Pa, sea-level standard pressure
LAPSE_RATE = 0.0065  # K/m, temperature drop per meter in the troposphere

TROPOPAUSE_ALT = 11000.0    # m, top of the troposphere
STRATO_ALT     = 20000.0    # m, top of the lower (isothermal) stratosphere layer
T_TROPOPAUSE   = T0 - LAPSE_RATE * TROPOPAUSE_ALT   # 216.65 K, constant above 11 km


def temperature(altitude):
    """Air temperature (K) using the layered Standard Atmosphere model."""
    if altitude <= TROPOPAUSE_ALT:
        return T0 - LAPSE_RATE * altitude
    return T_TROPOPAUSE  # isothermal layer (11-20 km, and extended as an approximation above)


def pressure(altitude):
    """Air pressure (Pa) using the layered Standard Atmosphere model."""
    if altitude <= TROPOPAUSE_ALT:
        T = temperature(altitude)
        return P0 * (T / T0) ** (G0 * M / (R * LAPSE_RATE))

    # Pressure at the tropopause, then exponential decay through the
    # isothermal stratosphere layer (hydrostatic equation with constant T).
    P_tropopause = P0 * (T_TROPOPAUSE / T0) ** (G0 * M / (R * LAPSE_RATE))
    return P_tropopause * np.exp(-G0 * M * (altitude - TROPOPAUSE_ALT) / (R * T_TROPOPAUSE))


def air_density(altitude):
    """Air density (kg/m^3) via the ideal gas law: rho = P*M / (R*T)."""
    altitude = max(altitude, 0.0)
    T = temperature(altitude)
    P = pressure(altitude)
    return P * M / (R * T)
