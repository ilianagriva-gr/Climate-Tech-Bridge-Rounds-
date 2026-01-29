import pandas as pd
import json
import os

file_path = "251223_Trellis_Bridge Rounds Research_Data.xlsx"
output_path = "data_analysis.json"

try:
    # Read all sheets to see what's available
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    print(f"Sheets found: {sheet_names}")

    data = {}
    for sheet in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        # Convert timestamps to string to make it JSON serializable
        df = df.applymap(lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)
        data[sheet] = df.head(5).to_dict(orient='records') # Just take head for inspection
        data[f"{sheet}_columns"] = list(df.columns)
        data[f"{sheet}_row_count"] = len(df)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Successfully converted data sample to {output_path}")

except Exception as e:
    print(f"Error: {e}")
