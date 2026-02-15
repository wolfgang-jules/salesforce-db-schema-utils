"""
This script is a tool designed to help in the field names standardization for tables.
It reads the input CSV file, which contains the table schema, from the "input_files"
folder and analyzes the data to generate new field names. The output is a new CSV file
with a new column named "NewFieldName", and stored in the "output_files" folder.
"""
from shared import process_file

process_file('asset')
