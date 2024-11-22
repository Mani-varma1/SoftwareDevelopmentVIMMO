import json
import re
import csv
from datetime import datetime

# Function to extract R codes from a list of disorders
def extract_rcodes(disorders_list):
    rcodes = []
    pattern = r'^R\d+(\.\d+)?$'  # Matches 'R' followed by digits, optional decimal and digits
    for disorder in disorders_list:
        if re.match(pattern, disorder):
            rcodes.append(disorder)
    return rcodes

# Function to parse ISO datetime strings
def parse_iso_datetime(date_string):
    # Remove the 'Z' timezone indicator for parsing
    date_string = date_string.rstrip('Z')
    # Handle datetime strings with or without microseconds
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
    return dt

def main():
    # Load the data from the JSON file
    with open("all_panel.json", "r") as json_file:
        all_data = json.load(json_file)
    
    # Initialize a list to store the relevant fields
    relevant_data = []
    
    # Iterate over each page's data
    for page_data in all_data:
        for item in page_data.get('results', []):
            panel_id = item.get('id')
            version = item.get('version')
            version_created = item.get('version_created')
            disorders_list = item.get('relevant_disorders', [])
            
            # Extract R codes using the function
            rcodes = extract_rcodes(disorders_list)
            
            # Parse version_created into a datetime object
            version_created_dt = parse_iso_datetime(version_created)
            
            # Collect the relevant data
            relevant_fields = {
                'id': panel_id,
                'version': version,
                'version_created': version_created_dt.strftime('%Y-%m-%d'),
                'version_created_dt': version_created_dt,
                'rcodes': rcodes
            }
            relevant_data.append(relevant_fields)
    
    # Group the data by panel ID
    panels = {}
    for item in relevant_data:
        panel_id = item['id']
        if panel_id not in panels:
            panels[panel_id] = []
        panels[panel_id].append(item)
    
    # Initialize a list to store the latest version data for each panel
    latest_versions = []
    
    # Process each panel's versions
    for panel_id, versions in panels.items():
        # Sort versions by 'version_created_dt' in ascending order
        versions.sort(key=lambda x: x['version_created_dt'])
        
        # The last item in the sorted list is the latest version
        latest_version = versions[-1]
        
        # Prepare data for CSV
        latest_versions.append({
            'Panel_ID': panel_id,
            'rcodes': ', '.join(latest_version['rcodes']),  # Join rcodes into a single string
            'Version': latest_version['version'],
        })
    
    # Write the latest versions to a CSV file
    csv_file_name = 'latest_panel_versions.csv'
    csv_headers = ['Panel_ID', 'rcodes', 'Version']
    
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for data in latest_versions:
            writer.writerow(data)
    
    print(f"CSV file '{csv_file_name}' has been created.")

if __name__ == "__main__":
    main()