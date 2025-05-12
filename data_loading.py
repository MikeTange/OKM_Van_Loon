""" The functions used to load in and carry out an initial clean and validation (requirements check) of the input files """


from Recipe import MissingRequirementError
from typing import Literal
from parameters import *
import pandas as pd
import numpy as np


def rename_nan_columns(df : pd.DataFrame, prefix : str="col") -> pd.DataFrame:
    """
    Rename DataFrame columns whose header could not be inferred, and have 'NaN' as header

    Parameters
    ----------
    df  : pd.DataFrame
        the DataFrame to clean
    prefix: str
        prefix to replace NaN column names with

    Returns
    -------
    df : DataFrame
        DataFrame with renamed columns
    """
    df = df.copy()

    df.columns = [
        f"{prefix}{idx}" if pd.isna(col) else col.strip()
        for idx, col in enumerate(df.columns)]
    
    return df


def clean_dataframe(df : pd.DataFrame, replace_empty_with_nan : bool=True) -> pd.DataFrame:
    """
    Cleans a DataFrame by:
    - Stripping whitespace from string values
    - Optionally replacing empty strings with pd.NA
    - Converting column types using pandas' best-guess inference

    Parameters
    ----------
    df  : pandas.DataFrame
        the DataFrame to clean
    replace_empty_with_na: bool
        whether to treat empty strings as missing values

    Returns
    -------
    df : pd.DataFrame
        cleaned and type-inferred DataFrame
    """
    df = df.copy()

    # Strip whitespace from strings & replace commas with periods as floating points
    df = df.applymap(lambda x: x.replace(',', '.').strip() if isinstance(x, str) else x)

    # Optionally replace empty strings with pd.NA for better type inference
    if replace_empty_with_nan:
        df.replace("", np.nan, inplace=True)

    # Infer column types
    df = df.convert_dtypes()

    return df


def load_bom(file_path : str, sheet_name : str) -> pd.DataFrame:
    """
    Load in the BOM (Bill of Material).

    Processing of the BOM is complex, and will be carried out by the bom_pre_processing module

    Parameters
    ----------
    file_path : str
        the input file path
    sheet_name : str
        the name of the relevant Excel sheet

    Returns
    -------
    df : pd.DataFrame
        the raw BOM data
    """

    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, header=None, decimal=",")

    return df


def load_input(file_path : str, sheet_name : str) -> pd.DataFrame:
    """
    Load in an input Excel file and turn it into a DataFrame with clean structure

    The Excel file is stripped of empty leading rows. All columns get given a unique header, inferred based on the first meaningful row; 
        otherwise generic

    Parameters
    ----------
    file_path : str
        the input file path
    sheet_name : str
        the name of the relevant Excel sheet

    Returns
    -------
    df : pd.DataFrame
        the DataFrame with clean structure
    """

    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Drop leading empty rows
    df = df.loc[~df.isnull().all(axis=1)].reset_index(drop=True)

    # Promote the first non-empty row to header
    header = df.iloc[0]
    df = df[1:]
    df.columns = header
    df = df.reset_index(drop=True)

    # Rename any columns named: "NaN"
    df = rename_nan_columns(df)

    return df


def check_requirements(df : pd.DataFrame, requirements : list[str]) -> None:
    """
    Check if a DataFrame contains all required columns

    df : pd.DataFrame
        the DataFrame to check
    requirement : list
        the column names which are required

    Raises
    ------
    MissingRequirementError
        if required columns are missing from the DataFrame
    """

    # Check for required columns
    requirements = set(requirements)
    req_test = requirements.difference(set(df.columns))
    if len(req_test) > 0:
        raise MissingRequirementError(f'missing one or more required column(s): {", ".join(req_test)}. \
Either rename existing columns, add new columns, or edit required input columns under "parameters.py"')


def load_input_file(file_path : str, sheet_name : str, 
                    input_file_type : Literal['BOM', 'Prijslijst', 'Waste lijst', 'Actieve lijst']) -> pd.DataFrame:
    """
    Load in and do an initial check of the input file based on its input_file_type.

    BOM files are skipped beyond loading. All other files get their structures and values stripped and cleaned.

    Parameters
    ----------
    file_path : str
        the input file path
    sheet_name : str
        the name of the relevant Excel sheet
    input_file_type : str
        the type of input file

    Returns
    -------
    df : pd.DataFrame
        the output df
    """

    if input_file_type == 'BOM':
        df = load_bom(file_path, sheet_name)
    
    elif input_file_type == 'Prijslijst':
        df = load_input(file_path, sheet_name)
        check_requirements(df, req_cols_price_weight)
        df = clean_dataframe(df).astype({"INGREDIENT CODE": 'string', 
                                         "INGREDIENTS": 'string'}) # fix incorrect type inferences as strings (universally applicable) (TODO currently hard-coded)

    elif input_file_type == 'Waste lijst':
        df = load_input(file_path, sheet_name)
        check_requirements(df, req_cols_waste)
        df = clean_dataframe(df).astype({'MEAL CODE': 'string', 
                                         'INGREDIENT CODE': 'string', 
                                         'UNITS': 'string'}) # fix incorrect type inferences as strings (universally applicable) (TODO currently hard-coded)
        df['id'] = df[['MEAL CODE', 'INGREDIENT CODE']].agg('_'.join, axis=1).astype('string') # create a unique id column

    elif input_file_type == 'Actieve lijst':
        df = load_input(file_path, sheet_name)
        check_requirements(df, req_cols_act_rec)
        df = clean_dataframe(df)

    else:
        raise ValueError('incorrect input_file_type. Choose from: "BOM", "Prijslijst", "Waste lijst", or "Actieve lijst"')

    return df
