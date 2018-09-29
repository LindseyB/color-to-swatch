import click 
from colour import Color
import zipfile
import json
from slugify import slugify
import requests
import re

@click.command()
@click.option('--url', default='https://color.adobe.com/vintage-card-color-theme-3165833/', help='The url to the adobe color page')

def convert(url):
	if not re.match(r'https://color.adobe.com/[0-9a-zA-Z_\-]+-color-theme-\d+', url):
		raise ValueError("Hmmm... this doesn't look like an Adobe Color URL. Wanna try that again?")

	name, hex_colors = get_hex_values(url)
	colors = convert_hex_to_hsl(hex_colors)

	# Swatches are just json files inside of a renamed zip
	# Lucky me
	zf = zipfile.ZipFile(slugify(name)+'.swatches', mode='w')

	json_obj = []
	json_obj.append({"name": name, "swatches": colors})
	json_string = json.dumps(json_obj)

	zf.writestr('Swatches.json', json_string)
	zf.close()

	print("...created " + slugify(name) + ".swatches")

def get_hex_values(url):
	m = re.search(r'color-theme-(\d+)', url)
	theme_id = m.group(1)

	url = "https://color.adobe.com/api/v2/themes/" + theme_id
	querystring = {"metadata":"all"}

	# This is the API key used on color.adobe.com it doesn't seem to expire
	headers = {'x-api-key': "7810788A1CFDC3A717C58F96BC4DD8B4"}
	response = requests.request("GET", url, headers=headers, params=querystring)
	data = json.loads(response.text)

	name = data["name"]
	swatches = data["swatches"]
	hex_colors = map(lambda c : "#"+c["hex"], swatches)

	return name, hex_colors

# Convert the fetched hex colors into the swatches JSON values
def convert_hex_to_hsl(hex_colors):
	colors = []
	for color in hex_colors:
		c = Color(color)
		colors.append({"hue": c.hue, "brightness": c.luminance, "saturation": c.saturation})

	return colors

if __name__ == '__main__':
	convert()
