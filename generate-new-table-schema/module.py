"""Module to process a CSV file and generate NewFieldNames based on the input parameters."""

import datetime
import os
import re
import sys
import pandas as pd
from colorama import Fore

OLD_FIELD_NAME:str ='QualifiedApiName'
LABEL_FIELD_NAME:str = 'Label'
NEW_FIELD_NAME:str = 'NewFieldName'

INPUT_PATH: str = './input_files'
OUTPUT_PATH: str = './output_files'

WAS_RENAMED_MANUALLY = 'WasRenamedManually'

def _get_current_datetime_string() -> str:
    """Get a unique timestamp in the format YYYYMMDD_HHMMSS.

    Returns:
        str: A unique timestamp in the format YYYYMMDD_HHMMSS.
    """
    now: datetime.datetime = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")

def _clean_original_field_name(value: str) -> str:
    """Convert the original field name to snake_case."""
    #replace anysalesforce __c suffix
    value_cleaned: str = value.replace('__c', '')
    value_cleaned = value_cleaned.replace('_c', '')
    # Convert original_field_name to snake_case
    value_cleaned = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value_cleaned)
    value_cleaned = re.sub('([a-z0-9])([A-Z])', r'\1_\2', value_cleaned).lower()
    # Replace # with literal "number"
    value_cleaned = value_cleaned.replace("identifier", "id")
    return value_cleaned

def _clean_label_name(value: str) -> str:
    """Convert label text to snake_case."""
    # Trim whitespace and convert input to lower case
    value_cleaned: str = value.strip().lower()

    # Replace spaces
    value_cleaned = value_cleaned.replace(' ', '_')

    # Replace # with literal "number"
    value_cleaned = value_cleaned.replace("#", "number")
    value_cleaned = value_cleaned.replace("identifier", "id")

    # Replace spaces, hyphens(dash), and plus signs with underscores
    value_cleaned = re.sub(r'[-+ ]', '_', value_cleaned)

    # Replace special characters with an empty string
    value_cleaned = re.sub(r'[`~!@#$%^&*()-=+?{}\[\]|\/<>\\,.;:\'\"°]', '', value_cleaned)

    return value_cleaned

def _get_new_field_name(old_field:str, label:str, data_type:str) -> str:
    """Generate a NewFieldName based on the input label name and data type.

    Args:
        old_field_name (str): The original field name.
        label_name (str): The original label name.
        data_type (str): The type of data associated with the field.

    Returns:
        str: The NewFieldName generated based on the input parameters.
    """
    # Clean old field name
    old_field_cleaned:str = _clean_original_field_name(old_field)

    # Clean label name
    label_cleaned: str = _clean_label_name(label)

    # Split the label name by underscores and get the first word and last word
    old_field_name_parts: list = old_field_cleaned.split('_')
    old_field_first_word: str = old_field_name_parts[0]
    old_field_last_word: str = old_field_name_parts[-1]

    label_name_parts: list = label_cleaned.split('_')
    label_first_word: str = label_name_parts[0]
    label_last_word: str = label_name_parts[-1]

    prefix:str = ''
    suffix:str = ''

    # Check conditions for prefix and suffix
    if data_type == 'boolean' and not label_first_word in ('is','has'):
        if old_field_first_word == 'has':
            prefix = 'has_'
        else:
            prefix = 'is_'

    if data_type == "id" and not label_last_word == "id":
        suffix = '_id'

    if data_type in ("integer","string")  and old_field_last_word == "id" and not label_last_word == "id":
        suffix = '_id'

    new_name: str = f"{prefix}{label_cleaned}{suffix}"

    return new_name


def process_file(file_name:str) -> str:
    """.
        It reads the input CSV file, which contains the table schema, from the "input_files"
        folder and analyzes the data to generate new field names. The output is a new CSV file
        with a new column named "NewFieldName", and stored in the "output_files" folder.
    """

    # Read the input CSV file into a DataFrame
    df: pd.DataFrame = pd.read_csv(f"{INPUT_PATH}/{file_name}.csv")

    # Delete the first column "[FieldDefinition]"
    df = df.drop(df.columns[0], axis=1)

    # Drop the records with OLD_FIELD_NAME = UserRecordAccessId
    # This field cannot be readed from salesforce
    df = df[df[OLD_FIELD_NAME] != 'UserRecordAccessId']

    # Order the dataframes by Label
    df = df.sort_values(by=[LABEL_FIELD_NAME])

    # Convert the old field names to snake_case
    old_field_names_camel_case: pd.Series = df.apply(
        lambda row: _clean_original_field_name(row[OLD_FIELD_NAME]),
        axis=1
    )

    # Insert the new field at the desired position
    df.insert(2, f"{OLD_FIELD_NAME}SnakeCase", old_field_names_camel_case)

    # Convert the labels field names to snake_case
    label_field_names_camel_case: pd.Series = df.apply(
        lambda row: _clean_label_name(row[LABEL_FIELD_NAME]),
        axis=1
    )

    # Insert the new field at the desired position
    df.insert(4, f"{LABEL_FIELD_NAME}SnakeCase", label_field_names_camel_case)

    # Generate the new field names
    new_field_values: pd.Series = df.apply(
        lambda row: _get_new_field_name(row[OLD_FIELD_NAME], row[LABEL_FIELD_NAME], row['ValueTypeId']),
        axis=1
    )

    # Insert the new field at the desired position
    df.insert(5, NEW_FIELD_NAME, new_field_values)

    # Create column IsReviwed column
    df[WAS_RENAMED_MANUALLY] = False

    # Write the updated DataFrame to a new CSV file
    output_file: str = f"{file_name}_{_get_current_datetime_string()}"
    output_file_path: str = f"{OUTPUT_PATH}/{output_file}.csv"

    df.to_csv(output_file_path, index=False)

    # Validate if the output_file exists in the output folder
    if os.path.exists(output_file_path):
        print(Fore.GREEN + f"\nThe file: {output_file_path} was created successfully!")
    else:
        print(Fore.RED + f"\nThe file: {output_file_path} was not created!")

    print(Fore.WHITE)

    return output_file

def validate_file(file_name: str) -> None:
    """Validate the output file and check if the fields were renamed correctly."""

    # Read the input CSV file into a DataFrame
    df: pd.DataFrame = pd.read_csv(f'{OUTPUT_PATH}/{file_name}.csv')

    filtered_df:pd.DataFrame = pd.DataFrame()

    old_eq_new: pd.Series = df[f"{OLD_FIELD_NAME}SnakeCase"] == df[NEW_FIELD_NAME]
    label_eq_new: pd.Series = df[f"{LABEL_FIELD_NAME}SnakeCase"] == df[NEW_FIELD_NAME]
    was_renamed_manually: pd.Series = df[WAS_RENAMED_MANUALLY]

    # Filter dataframe to get all records with equal values in the three fields
    filtered_df = df[(old_eq_new & label_eq_new) | was_renamed_manually]
    if not filtered_df.empty:
        print(Fore.GREEN + "\nSUCCESFULLY RENAMED FIELDS (3 FIELDS MATCH)")
        print(filtered_df[[OLD_FIELD_NAME, LABEL_FIELD_NAME, NEW_FIELD_NAME, WAS_RENAMED_MANUALLY]])

    # Filter dataframe to get all records with mixed values in the three fields
    filtered_df = df[(old_eq_new | label_eq_new) & ~(old_eq_new & label_eq_new) & ~was_renamed_manually]
    if not filtered_df.empty:
        print(Fore.YELLOW + "\nACCEPTABLY RENAMED FIELDS (2 FIELDS MATCH)")
        print(filtered_df[[OLD_FIELD_NAME, LABEL_FIELD_NAME, NEW_FIELD_NAME, WAS_RENAMED_MANUALLY]])

    # Filter dataframe to get all records with different values in the three fields
    filtered_df = df[~old_eq_new & ~label_eq_new & ~was_renamed_manually]
    if not filtered_df.empty:
        print(Fore.RED + "\nRENAMED FIELDS TO BE CHECKED (0 FIELDS MATCH)")
        print(filtered_df[[OLD_FIELD_NAME, LABEL_FIELD_NAME, NEW_FIELD_NAME, WAS_RENAMED_MANUALLY]])

    # Look duplicates in the dataframe
    duplicates: pd.DataFrame = df[df.duplicated(subset=[NEW_FIELD_NAME], keep=False)]
    if not duplicates.empty:
        print(Fore.RED + "\nDUPLICATES FIELDS")
        print(duplicates[[OLD_FIELD_NAME, LABEL_FIELD_NAME, NEW_FIELD_NAME]])

    print(Fore.WHITE)

if __name__ == "__main__":
    print(Fore.RED)
    print("This script is a module and should be imported into another script.")
    print("It is not meant to be run directly.")
    sys.exit(1)
