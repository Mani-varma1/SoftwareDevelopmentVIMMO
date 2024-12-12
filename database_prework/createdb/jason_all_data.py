import json
import requests
# Initialize the list to store all data
all_data = []
# Fetch new data and append to the list

api_url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/signedoff/?display=latest&page=1"
while api_url:
    try:
        # Send GET request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()  # Parse JSON response
        all_data.append(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        break



    # Move to the next page if available
    api_url = data.get("next")



# Write the updated data back to the file
with open("all_panel.json", "w") as json_file:
    json.dump(all_data, json_file)



