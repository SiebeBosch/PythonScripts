import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def analyze_pump_test(excel_file, sheet_name, water_depth_col, water_height_col, time_col, flow_rate, recovery_start_offset, recovery_end_offset):
    # Read data from Excel
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    if water_depth_col not in df.columns or water_height_col not in df.columns or time_col not in df.columns:
        raise ValueError("One or more specified columns are not present in the Excel sheet.")

    # Rename columns for consistency
    df = df.rename(columns={water_depth_col: 'Water_depth', 
                            water_height_col: 'Water_Height', 
                            time_col: 'Time'})
    
    # Convert Excel serial date to datetime
    df['Time'] = pd.to_datetime(df['Time'], unit='D', origin='1899-12-30')
    
    # Convert time to seconds since start of test
    df['Time_seconds'] = (df['Time'] - df['Time'].min()).dt.total_seconds()

    # Identify the end of pumping (maximum drawdown)
    pumping_end = df['Water_depth'].idxmax()
    t_pump = df.loc[pumping_end, 'Time_seconds']
    print(f"Pumping ends at index: {pumping_end}, Time: {df.loc[pumping_end, 'Time']}, Water Depth: {df.loc[pumping_end, 'Water_depth']}")

    # Calculate t/t' for recovery data, avoiding division by zero
    df.loc[(df['Time_seconds'] > t_pump), 't_t_prime'] = df.loc[(df['Time_seconds'] > t_pump), 'Time_seconds'] / (df.loc[(df['Time_seconds'] > t_pump), 'Time_seconds'] - t_pump)

    # Plot recovery data
    plt.figure(figsize=(12, 8))
    plt.semilogx(df.loc[pumping_end:, 't_t_prime'], df.loc[pumping_end:, 'Water_depth'], 'bo-')
    plt.xlabel('t/t\'')
    plt.ylabel('Residual Drawdown (m)')
    plt.title('Theis Recovery Plot')
    plt.grid(True)

    # Calculate slope for the straight-line portion
    recovery_start = pumping_end + recovery_start_offset
    recovery_end = len(df) - recovery_end_offset

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        np.log10(df.loc[recovery_start:recovery_end, 't_t_prime']),
        df.loc[recovery_start:recovery_end, 'Water_depth']
    )

    if r_value**2 < 0.9:
        print("Warning: The linear fit may not be strong (R² < 0.9). Consider adjusting the analysis range.")

    # Calculate transmissivity
    T = 2.3 * flow_rate / (4 * np.pi * slope)

    print(f"Transmissivity (T): {T:.2e} m²/s")

    # Plot the fitted line
    x_fit = np.logspace(np.log10(df.loc[recovery_start:, 't_t_prime'].min()),
                        np.log10(df.loc[recovery_start:, 't_t_prime'].max()), 100)
    y_fit = slope * np.log10(x_fit) + intercept
    plt.plot(x_fit, y_fit, 'r-', label='Fitted Line')
    
    # Highlight the portion used for analysis
    plt.plot(df.loc[recovery_start:recovery_end, 't_t_prime'], 
             df.loc[recovery_start:recovery_end, 'Water_depth'], 
             'g-', linewidth=2, label='Analysis Range')
    
    plt.text(0.95, 0.05, f'R² = {r_value**2:.2f}', transform=plt.gca().transAxes, ha='right')

    plt.legend()
    plt.show()

    return T, df

def save_results_to_file(T, possible_thicknesses, filename="hydraulic_conductivity_results.csv"):
    results = pd.DataFrame({
        'Aquifer_Thickness_m': possible_thicknesses,
        'Hydraulic_Conductivity_K_m_per_day': [T/thickness * 86400 for thickness in possible_thicknesses]
    })
    results.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

# Example usage
excel_file = r'c:\\SYNC\\PROJECTEN\\H3143.SIBELCO\\01.Canada\\02.Analysis\\Pump_Test\\CA_AV_GT_20240125_SR_109_GT_01_PumpTests.xlsx'
sheet_name = 'CA_AV_SR_GT_Combined'
water_depth_col = 'Water depth (m)'
water_height_col = 'Water Height(m)'
time_col = 'Time'
flow_rate = 0.001  # m³/s
start_recovery_offset = 10 #timesteps after pumpings stops and before points are used in recharge test
recovery_end_offset = 5 #timesteps to skip at the end of the pumping test

T, df = analyze_pump_test(excel_file, sheet_name, water_depth_col, water_height_col, time_col, flow_rate, start_recovery_offset, recovery_end_offset)

print(f"\nFor flow rate {flow_rate} m³/s:")
print(f"Transmissivity (T): {T:.2e} m²/s")

# Calculate K for various possible aquifer thicknesses in m/day
possible_thicknesses = [10, 50, 100, 200]
print("\nPossible Hydraulic Conductivity (K) values in m/day:")
for thickness in possible_thicknesses:
    K = (T / thickness) * 86400  # Convert from m/s to m/day
    print(f"For aquifer thickness {thickness} m: K = {K:.2e} m/day")

# write the results to file
save_results_to_file(T, possible_thicknesses)

# Print the first few rows of the DataFrame
print("\nFirst few rows of the processed data:")
print(df.head())