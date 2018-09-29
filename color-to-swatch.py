import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from colour import Color
import zipfile
import json
from slugify import slugify

@click.command()
@click.option('--url', default='https://color.adobe.com/vintage-card-color-theme-3165833/', help='The url to the adobe color page')

#TODO: Add url validation
def convert(url):
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

# Ugh, so adobe color has no API and is JS only
# We use selenium to go get the colors
def get_hex_values(url):
	driver = webdriver.Chrome() #TODO: get headless working
	driver.set_window_size(1120, 550)
	driver.get(url)
	elements = driver.find_elements_by_css_selector('.themeBox li')
	name = driver.find_element_by_css_selector('h1 div').text
	return name, map(lambda e : e.get_attribute("title"), elements)

# Convert the fetched hex colors into the swatches JSON values
def convert_hex_to_hsl(hex_colors):
	colors = []
	for color in hex_colors:
		c = Color(color)
		colors.append({"hue": c.hue, "brightness": c.luminance, "saturation": c.saturation})

	return colors

if __name__ == '__main__':
	convert()
