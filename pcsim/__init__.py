"""Persistent robot charging: scheduling core and Sec. VI simulation pipeline.

Paper: Kumar, Lee, et al., "The Persistent Robot Charging Problem for
Long-Duration Autonomy", IEEE RA-L 10(3), 2025.

Time convention used everywhere in this package: integer slots t = 0, 1, ...,
slot t covers [t, t+1) in slot units (1 slot = 1 minute in the simulation).
Robot i with initial state r_i(0) = e_j (phase j) is in cycle position
(j + t) mod T_i at slot t (Eqs. 5-6), and charges iff that position < c_i (Eq. 7).
"""
