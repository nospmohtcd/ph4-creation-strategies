"""
mcnemar.py
Part of the "Pharmacophore Creation Strategies: Human vs. Machine" study.

Anh-Tien Ton et al. (2026)

This script calculates the McNemar contingency table and associated 
chi-squared values to compare human-generated vs. machine-generated models.
"""

import pandas as pd
import numpy as np
import argparse
import os
from itertools import combinations
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multitest import multipletests

def determine_sig(row, p_col, alpha=0.05):
    p_val = row[p_col]
    if p_val >= alpha:
        return f'Equivalent (p \u2265 {alpha})'
    
    m1, m2 = row['Model 1'], row['Model 2']
    yn, ny = row['M1 Correct / M2 Wrong (YN)'], row['M1 Wrong / M2 Correct (NY)']
    better = m1 if yn > ny else m2
    return f'{better} is significantly better ({p_col})'

def get_or_ci(yn, ny):
    """
    Determines:
	 the Odds Ratio: (yn/ny)
	 the log standard error sqrt: (1/yn + 1/ny)
	 X, Y: the lower and upper bounds of the 95% Confidence Interval for the Odds Ratio
    """
    # Modular addition for effect size
    if ny == 0: return np.inf, np.nan, np.nan
    if yn == 0: return 0.0, np.nan, np.nan
    or_val = yn / ny
    se_log = np.sqrt((1/yn) + (1/ny))
    low_x = np.exp(np.log(or_val) - 1.96 * se_log)
    upper_y = np.exp(np.log(or_val) + 1.96 * se_log)
    return or_val, low_x, upper_y


def run_mcnemar_analysis(input_file):
    """
    Performs McNemar's test for all unique pairs of models in the input CSV.
    Generates a CSV file: a full results table with Comparison Result(s)
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
    
    # Model columns (Columns F through N / indices 5 to 13)
    model_cols = df.columns[5:14].tolist()
    
    # Basic check to ensure required columns exist
    if ground_truth_col not in df.columns or len(model_cols) != 9:
        print("Error: Input file must contain 'real_activity' and 9 model columns (indices 5-13).")
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
        odds_ratio, low_x, upper_y = get_or_ci(yn, ny)
        
        results.append({
            'Model 1': m1,
            'Model 2': m2,
            'Both Correct (YY)': yy,
            'M1 Correct / M2 Wrong (YN)': yn,
            'M1 Wrong / M2 Correct (NY)': ny,
            'Both Wrong (NN)': nn,
            'Total': total,
            'Chi-squared': stats.statistic,
            'p-value': stats.pvalue,
	    'Odds Ratio': odds_ratio,
	    'CI_Lower_X': low_x,
	    'CI_Upper_Y': upper_y
        })

    # 4. Generate Output Filenames and Results DataFrame
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    output_full_results = f"mcnemar_results_{base_name}.csv"
    output_p_matrix = f"mcnemar_p_values_matrix_{base_name}.csv"

    results_df = pd.DataFrame(results)

    # 5. Multiple Testing Corrections
    p_vals = results_df['p-value'].values

    # The [1] index retrieves the adjusted p-values array
    results_df['p_Bonferroni'] = multipletests(p_vals, method='bonferroni')[1]
    results_df['p_Holm'] = multipletests(p_vals, method='holm')[1]

    # 6. Add the Comparison Result Column**
    results_df['Result_Raw'] = results_df.apply(lambda r: determine_sig(r, 'p-value'), axis=1)
    results_df['Result_Bonferroni'] = results_df.apply(lambda r: determine_sig(r, 'p_Bonferroni'), axis=1)
    results_df['Result_Holm'] = results_df.apply(lambda r: determine_sig(r, 'p_Holm'), axis=1)

    # 7. Manual checking of the Holm correction
    results_df = results_df.sort_values('p-value')
    # Add Rank and Multiplier
    n = len(results_df)
    results_df['Holm_Rank'] = range(1, n + 1)
    results_df['Holm_Multiplier'] = n - results_df['Holm_Rank'] + 1
    # Now you can sort back to Model 1 / Model 2 order for the CSV
    results_df = results_df.sort_values(['Model 1', 'Model 2'])

    # 8. --- OUTPUT: Full Results Table ---
    results_df.to_csv(output_full_results, index=False)
    print(f"Full McNemar results (including Comparison Results) saved to: {output_full_results}")

if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(
        description='Perform McNemar test on model predictions in a CSV.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_csv', help='Path to the input CSV file')
    
    args = parser.parse_args()
    
    run_mcnemar_analysis(args.input_csv)
