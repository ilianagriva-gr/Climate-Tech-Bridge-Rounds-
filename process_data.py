import pandas as pd
import os

# Configuration
INPUT_FILE = "251223_Trellis_Bridge Rounds Research_Data.xlsx"
SHEET_NAME = "Cleaned_Data"
OUTPUT_FILE = "cleaned_trellis_data.csv"

def load_and_process_data():
    print(f"Loading data from {INPUT_FILE}...")
    
    # Read the Excel file
    # Based on previous analysis, row 0 is header-like but the actual data starts properly around row 1.
    # The JSON analysis showed keys like "Unnamed: 1": "# ID", "Unnamed: 2": "Company " in the first element of "Cleaned_Data".
    # This implies the header is on the first row (index 0).
    
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, header=1)
    
    # Inspect columns to ensure we have what we need
    # The JSON showed column names like:
    # "# ID", "Company ", "HQ Location", "Year Founded", "Sector ", "Deal Date", 
    # "Deal Stage", "Total Capital Raised to date ", "Deal Size", "Valuation", etc.
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    print("Columns found:", df.columns.tolist())
    
    # Select relevant columns
    desired_columns = [
        "Company", "HQ Location", "Year Founded", "Sector", "Deal Date",
        "Deal Stage", "Total Capital Raised to date", "Deal Size", "Valuation",
        "Investors", "Investor Mix"
    ]
    
    # Handle potential missing or slightly named columns
    # Mappings based on inspection:
    # "Company " -> "Company"
    # "Sector " -> "Sector"
    
    # Let's filter to existing columns
    available_cols = [c for c in desired_columns if c in df.columns]
    
    # Check for missing critical columns
    missing_cols = set(desired_columns) - set(df.columns)
    if missing_cols:
        print(f"Warning: Missing columns: {missing_cols}")
        
    df_clean = df[available_cols].copy()
    
    # Data Cleaning
    
    # Convert Deal Date to datetime
    if 'Deal Date' in df_clean.columns:
        df_clean['Deal Date'] = pd.to_datetime(df_clean['Deal Date'], errors='coerce')
        df_clean['Year'] = df_clean['Deal Date'].dt.year
    
    # Ensure numeric columns are numeric
    numeric_cols = ["Total Capital Raised to date", "Deal Size", "Valuation", "Year Founded"]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
    # Save to CSV
    df_clean.to_csv(OUTPUT_FILE, index=False)
    print(f"Cleaned data saved to {OUTPUT_FILE}")
    print(f"Rows: {len(df_clean)}")
    
    return df_clean

if __name__ == "__main__":
    load_and_process_data()
