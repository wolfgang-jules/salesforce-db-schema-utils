"""
This script is a tool designed to help in the field names standardization for tables
It checks if the values of the "NewFieldName" column were generated correctly,
comparing the old field name, label name, and new field name, and depending of the
findings will print the messages with different colors for better understanding.
"""
from shared import validate_file

validate_file('asset_final_version')
