import numpy as np
import rasterio
import pandas as pd
import os
def main():
    print("Markov Chain Transition Matrix Generator for LULC Data\n")
    # Input folder and filenames
    folder = input("Enter the folder path where both LULC rasters are located: ").strip()
    file_2010 = input("Enter the filename for 2010 LULC raster: ").strip()
    file_2020 = input("Enter the filename for 2020 LULC raster: ").strip()
    # Set working directory
    os.makedirs(folder, exist_ok=True)
    os.chdir(folder)
    # full paths
    path_2010 = os.path.join(folder, file_2010)
    path_2020 = os.path.join(folder, file_2020)
    # Load raster data
    with rasterio.open(path_2010) as src1:
        lulc_2010 = src1.read(1)
    with rasterio.open(path_2020) as src2:
        lulc_2020 = src2.read(1)
    # Define LULC classes based on the reclassification values
    valid_classes = [1, 2, 3, 4, 5]
    class_labels = ['Water', 'Built', 'Barren', 'Forest', 'Agriculture']
    # Mask to keep only valid pixels
    mask = np.isin(lulc_2010, valid_classes) & np.isin(lulc_2020, valid_classes)
    initial = lulc_2010[mask]
    final = lulc_2020[mask]
    # Initialize transition matrix
    transition_counts = np.zeros((5, 5), dtype=int)
    # Fill in transition matrix
    for i, from_class in enumerate(valid_classes):
        for j, to_class in enumerate(valid_classes):
            transition_counts[i, j] = np.sum((initial == from_class) & (final == to_class))
    # Normalize to get probabilities
    transition_probs = transition_counts.astype(float)
    row_sums = transition_probs.sum(axis=1, keepdims=True)
    transition_probs = np.divide(transition_probs, row_sums, out=np.zeros_like(transition_probs), where=row_sums!=0)
    # Convert to DataFrames
    df_counts = pd.DataFrame(transition_counts, index=class_labels, columns=class_labels)
    df_probs = pd.DataFrame(transition_probs, index=class_labels, columns=class_labels)
    # Print results
    print("\nTransition Count Matrix:\n")
    print(df_counts)
    print("\nMarkov Transition Probability Matrix:\n")
    print(df_probs)
    # Save results (overwrite by default)
    counts_file = os.path.join(folder, "transition_counts.csv")
    probs_file = os.path.join(folder, "transition_probabilities.csv")
    df_counts.to_csv(counts_file, index=True)
    df_probs.to_csv(probs_file, index=True)
    print(f"\nMatrices successfully saved in: {folder}")
if __name__ == "__main__":
    main()
