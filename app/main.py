import requests
import json
import time

REQUEST_DELAY = 10
REQUEST_COUNT = 0

script_start_time = time.time()

def fetch_data(url):
  """Fetch data from the API endpoint."""
  time.sleep(REQUEST_DELAY)
  response = requests.get(url)
  response.raise_for_status()
  return response.json()

def get_key_metadata(entity, entity_type):
  """Extract key metadata from an entity depending on its type."""
  key_fields = {
    "Datastreams": [
      "@iot.id", "name", "description", "unitOfMeasurement",
      "properties", "restricted"
    ],
    "Projects": ["@iot.id", "name", "description", "properties"],
    "HistoricalLocations": ["@iot.id", "time"],
    "Locations": [
      "@iot.id", "name", "description", "location", "properties"
    ],
    "MultiDatastreams": [
      "@iot.id", "name", "description", "unitOfMeasurements",
      "properties", "restricted"
    ],
  }
  fields = key_fields.get(entity_type, ["@iot.id", "@iot.selfLink"])
  return {field: entity.get(field) for field in fields}

def build_tree(thing):
  """Recursively build the tree structure for a single 'Thing'."""
  tree = {
    "id": thing["@iot.id"],
    "name": thing["name"],
    "description": thing["description"],
    "properties": thing["properties"],
    "restricted": thing["restricted"]
  }

  links = [
    "HistoricalLocations", "Locations", "MultiDatastreams",
    "Projects", "Datastreams"
  ]

  for link in links:
    link_key = f"{link}@iot.navigationLink"
    if link_key in thing:
      related_data_url = thing[link_key]
      related_data = fetch_data(related_data_url).get("value", [])
      tree[link] = [
        get_key_metadata(item, link)
        for item in related_data
      ]
      global REQUEST_COUNT
      REQUEST_COUNT += 1
      print(REQUEST_COUNT)
  return tree

def build_things_tree(things_url):
  """Build the hierarchical JSON tree for all 'Things'."""
  things_data = fetch_data(things_url)
  return [build_tree(thing) for thing in things_data.get("value", [])]

things_url = "https://wyseason.uwyo.edu/sta/v1.1/Projects(1)/Things"
things_tree = build_things_tree(things_url)

output_file = "things_tree.json"
with open(output_file, "w") as f:
  json.dump(things_tree, f, indent=2)

duration_seconds = int(time.time() - script_start_time)
hours, remainder = divmod(duration_seconds, 3600)
minutes, seconds = divmod(remainder, 60)

print(f"JSON tree saved to {output_file}.")
print(f"Script completed in {hours}h {minutes}m {seconds}s...")
