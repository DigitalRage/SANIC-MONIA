import os
from PIL import Image as im
from term_image.image import from_file

# Folder where your PNGs are stored
png_folder = 'png printer/pngs'  # Make sure this folder exists

def load_image_with_path(filename):
	path = os.path.join(png_folder, filename)
	return im.open(path).convert('RGBA')

def create_composite(objects):
	max_width = 0
	max_height = 0
	images = []

	for filename, x, y in objects:
		img = load_image_with_path(filename)
		images.append((img, x, y))
		max_width = max(max_width, x + img.width)
		max_height = max(max_height, y + img.height)

	base = im.new('RGBA', (max_width, max_height))
	for img, x, y in images:
		base.paste(img, (x, y), img)

	return base

def print_image_in_terminal(image):
	# Save the image temporarily
	temp_path = 'temp_composite.png'
	image.save(temp_path)
	# Display in terminal
	img = from_file(temp_path)
	img.draw()
	# Optionally, delete temp file
	os.remove(temp_path)

def print_objs(objects_to_place):
	# Make sure the folder exists
	if not os.path.exists(png_folder):
		print(f"Folder '{png_folder}' does not exist.")
		return
	composite_image = create_composite(objects_to_place)
	print_image_in_terminal(composite_image)

if __name__ == '__main__':
	for x in range(1, 100):
		objects_to_place = [
			('size.png',0,0),
			('player.png', 500, x),
			('enemy.png', 200, 150),
			
		]
		print_objs(objects_to_place)