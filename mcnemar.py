"""
mcnemar.py
Part of the "Pharmacophore Creation Strategies: Human vs. Machine" study.

Anh-Tien Ton et al. (2026)

This script calculates the McNemar contingency table and associated 
chi-squared values to compare human-generated vs. machine-generated models.
"""

import pandas as pd
import argparse
import os
from itertools import combinations
from statsmodels.stats.contingency_tables import mcnemar

def determine_comparison_result(row, alpha=0.05):
    """Determines the comparison result based on p-value and discordant counts."""
    p_value = row['p-value']
    m1_better = row['M1 Correct / M2 Wrong (YN)']
    m2_better = row['M1 Wrong / M2 Correct (NY)']
    model_1 = row['Model 1']
    model_2 = row['Model 2']

    if p_value >= alpha:
        return 'Equivalent (p \u2265 0.05)'
    else:
        # Statistically significant difference (p < 0.05)
        if m1_better > m2_better:
            return f'{model_1} is significantly better than {model_2} (YN > NY)'
        elif m2_better > m1_better:
            return f'{model_2} is significantly better than {model_1} (NY > YN)'
        else:
            # This edge case should be rare for p < 0.05
            return 'Significant, but YN = NY'


def run_mcnemar_analysis(input_file):
    """
    Performs McNemar's test for all unique pairs of models in the input CSV.
    Generates two CSV files: a full results table with Comparison Result and a 
    lower triangular p-value matrix.
    """
    
    # 1. Load the dataset
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # 2. Setup Column Logic
    # Ground Truth column (Column E / index 4)
    ground_truth_col = 'real_activity'
    
    # Model columns (Columns F through O / indices 5 to 14)
    model_cols = df.columns[5:15].tolist()
    
    # Basic check to ensure required columns exist
    if ground_truth_col not in df.columns or len(model_cols) != 10:
        print("Error: Input file must contain 'real_activity' and 10 model columns (indices 5-14).")
        return
    
    print(f"Starting McNemar analysis for {len(model_cols)} models: {', '.join(model_cols)}")

    results = []

    # 3. Perform McNemar test for all unique combinations
    for m1, m2 in combinations(model_cols, 2):
        
        # Determine correctness against ground truth
        m1_correct = (df[m1] == df[ground_truth_col])
        m2_correct = (df[m2] == df[ground_truth_col])
        
        # Calculate Contingency Table Components (YY, YN, NY, NN)
        yy = ((m1_correct) & (m2_correct)).sum()
        yn = ((m1_correct) & (~m2_correct)).sum()
        ny = ((~m1_correct) & (m2_correct)).sum()
        nn = ((~m1_correct) & (~m2_correct)).sum()
        
        total = yy + yn + ny + nn
        
        # Construct the 2x2 Table: [[YY, YN], [NY, NN]]
        table = [[yy, yn], [ny, nn]]
        
        # Perform McNemar's Test
        stats = mcnemar(table, exact=False, correction=True)
        
        results.append({
            'Model 1': m1,
            'Model 2': m2,
            'Both Correct (YY)': yy,
            'M1 Correct / M2 Wrong (YN)': yn,
            'M1 Wrong / M2 Correct (NY)': ny,
            'Both Wrong (NN)': nn,
            'Total': total,
            'Chi-squared': stats.statistic,
            'p-value': stats.pvalue
        })

    # 4. Generate Output Filenames and Results DataFrame
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    output_full_results = f"mcnemar_results_{base_name}.csv"
    output_p_matrix = f"mcnemar_p_values_matrix_{base_name}.csv"

    results_df = pd.DataFrame(results)

    # 5. Add the Comparison Result Column**
    results_df['Comparison Result'] = results_df.apply(determine_comparison_result, axis=1)

    # --- FIRST OUTPUT: Full Results Table ---
    results_df.to_csv(output_full_results, index=False)
    print(f"1/2: Full McNemar results (including Comparison Result) saved to: {output_full_results}")

    # --- SECOND OUTPUT: Lower Triangular P-Value Matrix ---
    
    # Initialize an empty square matrix for p-values
    p_matrix = pd.DataFrame(index=model_cols, columns=model_cols)

    # Fill the lower triangular portion
    for _, row in results_df.iterrows():
        m1, m2 = row['Model 1'], row['Model 2']
        p_val = row['p-value']
        
        # Get index positions to enforce lower triangular structure
        idx1, idx2 = model_cols.index(m1), model_cols.index(m2)
        
        # Fill the cell where the row index > column index
        if idx1 > idx2:
            p_matrix.loc[m1, m2] = p_val
        else:
            p_matrix.loc[m2, m1] = p_val

    p_matrix.to_csv(output_p_matrix)
    print(f"2/2: Lower triangular p-value matrix saved to: {output_p_matrix}")


if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(
        description='Perform McNemar test on model predictions in a CSV.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_csv', help='Path to the input CSV file')
    
    args = parser.parse_args()
    
    run_mcnemar_analysis(args.input_csv)
