import numpy as np

# Given data
y = [0, 20.13425, 40.2685, 60.40276, 80.53701, 100.6713, 120.8055, 140.9398, 161.074, 181.2083, 201.3425, 221.4768, 241.611, 261.7453, 281.8795, 302.0138, 322.148, 342.2823, 362.4165, 382.5508, 402.685, 422.8193, 442.9535, 463.0878, 483.222, 503.3563, 523.4906, 543.6248, 563.7591, 583.8933, 604.0276, 604.0276]
z = [1441.657, 1433.818, 1427.505, 1420.838, 1414.38, 1408.748, 1403.157, 1394.708, 1384.022, 1372.483, 1362.677, 1358.463, 1357.71, 1357.835, 1358.083, 1358.64, 1359.843, 1361.76, 1364.3, 1366.198, 1369.848, 1376.395, 1383.205, 1391.007, 1400.368, 1410.863, 1421.118, 1429.78, 1436.953, 1442.465, 1447.515, 1447.515]

# Manning's roughness and slope
n = 0.03
S = 0.005


def interpolate(x1, y1, x2, y2, x):
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

def calculate_hydraulic_parameters(water_level):
    area = 0
    wetted_perimeter = 0
    left_bank = None
    right_bank = None
    
    for i in range(len(y) - 1):
        y1, y2 = y[i], y[i+1]
        z1, z2 = z[i], z[i+1]
        
        if water_level <= min(z1, z2):
            continue
        elif water_level >= max(z1, z2):
            zmax, zmin = max(z1, z2), min(z1, z2)
            segment_area = (water_level - zmin) * (y2 - y1) - (zmax - zmin) * (y2 - y1) / 2
            segment_perimeter = np.sqrt((y2 - y1)**2 + (z2 - z1)**2)
            if left_bank is None:
                left_bank = y1
            right_bank = y2
        else:
            if z1 < z2:
                y_intersect = interpolate(z1, y1, z2, y2, water_level)
                segment_area = 0.5 * (y_intersect - y1) * (water_level - z1)
                segment_perimeter = np.sqrt((y_intersect - y1)**2 + (water_level - z1)**2)
                if left_bank is None:
                    left_bank = y1
                right_bank = y_intersect
            else:
                y_intersect = interpolate(z2, y2, z1, y1, water_level)
                segment_area = 0.5 * (y2 - y_intersect) * (water_level - z2)
                segment_perimeter = np.sqrt((y2 - y_intersect)**2 + (water_level - z2)**2)
                if left_bank is None:
                    left_bank = y_intersect
                right_bank = y2
        
        area += segment_area
        wetted_perimeter += segment_perimeter
        
    return area, wetted_perimeter
    

# Calculate Q-H relation
lowest_point = min(z)
max_depth = 10  # meters
step = 0.1  # 10 cm steps

water_levels = np.arange(lowest_point, lowest_point + max_depth + step, step)
results = []

for wl in water_levels:
    A, P = calculate_hydraulic_parameters(wl)
    R = A / P if P > 0 else 0
    Q = (1/n) * A * R**(2/3) * S**(1/2)
    results.append((wl, Q, A, P))

# Print results
print("Water Level (m) | Discharge (m³/s) | Wetted Area (m²) | Wetted Perimeter (m)")
print("--------------------------------------------------------------------------")
for wl, Q, A, P in results:
    print(f"{wl:.2f} | {Q:.2f} | {A:.2f} | {P:.2f}")