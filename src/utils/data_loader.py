import pandas as pd

def load_excel_data(file_path):
    """Load data from an Excel file."""
    return pd.read_excel(file_path)

def load_csv_data(file_path):
    """Load data from a CSV file."""
    return pd.read_csv(file_path)

def load_airport_data(airport_file):
    """Load airport data including city and state information."""
    return load_csv_data(airport_file)

def load_projection_data(projection_file):
    """Load market projection data for airports."""
    return load_excel_data(projection_file)

def load_carga_data(carga_file):
    """Load air cargo market projection data."""
    return load_excel_data(carga_file)

def load_international_passengers_data(international_file):
    """Load international passengers projection data."""
    return load_excel_data(international_file)

def load_demand_projection_data(demand_file):
    """Load demand projection results."""
    return load_csv_data(demand_file)