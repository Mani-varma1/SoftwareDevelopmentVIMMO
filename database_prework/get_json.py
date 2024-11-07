import json
import requests
import os

# Initialize the list to store all data
all_data = []
# Fetch new data and append to the list
for number in range(1, 9):
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/signedoff/?display=all&format=json&page={number}"
    response = requests.get(url)
    json_data = response.json()
    all_data.append(json_data)

# Write the updated data back to the file
with open("all_panel.json", "w") as json_file:
    json.dump(all_data, json_file)