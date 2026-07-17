import json
import os

def extract_item_type_fields(input_file, output_file):
    """
    Extracts 'id', 'typeKey', and 'display' from a JSON file
    and saves them to a new JSON file.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.
    """
    extracted_data = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            extracted_data.append({
                'id': item.get('id'),
                'typeKey': item.get('typeKey'),
                'display': item.get('display')
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=4)

        print(f"Successfully extracted data to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    extract_item_type_fields('item_types_result.json', 'extracted_item_types.json')