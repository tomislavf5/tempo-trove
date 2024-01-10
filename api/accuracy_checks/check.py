import json

# Load the JSON objects from a file
with open('DIWK_and_SOOI-recs.json', 'r') as f:
 json_objects = json.load(f)

# Dictionary to store the sum of each attribute
attribute_sums = {}

# Iterate over the list of JSON objects
for obj in json_objects:
 # Iterate over the attributes of the JSON object
 for attr, value in obj.items():
    # Try to convert the value to a float
    try:
        value = float(value)
    except ValueError:
        # Skip this value if it can't be converted to a float
        continue
    # Append the value of the attribute to the corresponding list in the sum dictionary
    if attr not in attribute_sums:
        attribute_sums[attr] = []
    attribute_sums[attr].append(value)

# Calculate the average for each attribute
averages = {attr: sum(values) / len(values) for attr, values in attribute_sums.items()}

print(averages)