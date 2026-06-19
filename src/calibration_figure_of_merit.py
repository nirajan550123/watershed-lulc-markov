# Markov-CA Calibration: Figure of Merit
# Compares the simulated 2020 built-up map against observed 2020 to evaluate
# model accuracy. Set the three raster paths below to your project geodatabase.
# Requires: ArcGIS Pro (arcpy), numpy.

import arcpy
import numpy as np

# Step 0: Read arrays
lulc_2010 = arcpy.RasterToNumPyArray(r"PROJECT.gdb\Reclass_NLCD_2010_Resample")
lulc_2020 = arcpy.RasterToNumPyArray(r"PROJECT.gdb\Reclass_NLCD_2020_Resample")
simulated_lulc = arcpy.RasterToNumPyArray(r"PROJECT.gdb\Simulated_2020_W")

# Step 1: Handle array size mismatch
min_rows = min(lulc_2010.shape[0], lulc_2020.shape[0], simulated_lulc.shape[0])
min_cols = min(lulc_2010.shape[1], lulc_2020.shape[1], simulated_lulc.shape[1])

lulc_2010 = lulc_2010[:min_rows, :min_cols]
lulc_2020 = lulc_2020[:min_rows, :min_cols]
simulated_lulc = simulated_lulc[:min_rows, :min_cols]

# ➡️ New: Count of agricultural land (value 5) in each raster
agri_2010_count = np.sum(lulc_2010 == 5)
agri_2020_count = np.sum(lulc_2020 == 5)
agri_simulated_count = np.sum(simulated_lulc == 5)

# Step 2: Create corrected simulated LULC
corrected_simulated = np.where(simulated_lulc == 2, 2, lulc_2010)

# Step 3: Mask areas that were already built in 2010
mask_not_built_2010 = (lulc_2010 != 2)

# Step 4: Find change-relevant cells (only new built-ups)
mask_change = ((lulc_2020 == 2) | (corrected_simulated == 2)) & mask_not_built_2010

# Step 5: Calculate A (Misses), B (Correct), and C (False Alarms)
A = np.sum((lulc_2020 == 2) & (corrected_simulated != 2) & mask_not_built_2010)
B = np.sum((lulc_2020 == 2) & (corrected_simulated == 2) & mask_not_built_2010)
C = np.sum((lulc_2020 != 2) & (corrected_simulated == 2) & mask_not_built_2010)

# Step 6: Calculate Figure of Merit (FoM)
FoM = B / (A + B + C) if (A + B + C) > 0 else 0

# ➡️ New: Calculate Total Actual Changes (only new built-up in 2020)
total_actual_changes = np.sum((lulc_2010 != 2) & (lulc_2020 == 2))

# ➡️ New: Calculate Total Simulated Changes (cells that changed to built in simulated)
total_simulated_changes = np.sum((lulc_2010 != corrected_simulated) & (corrected_simulated == 2))

# Step 7: Print results
print("Correct Predictions (B):", B)
print("False Negatives (Misses, A):", A)
print("False Positives (False Alarms, C):", C)
print("Figure of Merit (FoM):", FoM)

# ➡️ New: Print change counts
print("Total Actual Changes from 2010 to 2020 (Built areas):", total_actual_changes)
print("Total Changes Simulated by Model (Built areas):", total_simulated_changes)

# ➡️ New: Print agricultural land counts
print("Agricultural Land in 2010:", agri_2010_count)
print("Agricultural Land in 2020:", agri_2020_count)
print("Agricultural Land in Simulated Map:", agri_simulated_count)
