import os
import json
import re

# Paths to your folders containing music files and images
music_folder = 'C:\\Users\\nur_e\\EmoSync\\static\\music2'
image_folder = "C:\\Users\\nur_e\\EmoSync\\static\\images\\cover"

# Base paths relative to the server for static resources (to use in URLs)
relative_music_folder = 'static/music2'
relative_image_path = '/static/images/cover'

# Create a list to store song data
songs = []

# Loop through each file in the music folder
for idx, filename in enumerate(os.listdir(music_folder)):
    print(f"Processing file: {filename}")  # Debugging: show each file being processed

    # Check if the file has a .mp3 extension (case insensitive)
    if filename.lower().endswith('.mp3'):
        # Remove the file extension to get the song title
        song_title = os.path.splitext(filename)[0]

        # Remove prefix matching "A0--" or similar patterns using regex
        cleaned_title = re.sub(r'^A0[0-9]*[_-]*', '', song_title)

        # Replace underscores and hyphens with spaces, and convert to title case for formatted title
        formatted_title = re.sub(r'[_-]', ' ', cleaned_title).title()

        # Set the corresponding image file path based on the song file name
        image_filename = f"{song_title}.jpeg"
        image_path = os.path.join(image_folder, image_filename)

        # Check if the image file exists, if not, set a default image
        if os.path.exists(image_path):
            image_url = f"{relative_image_path}/{image_filename}"
        else:
            # Use a default image if specific image is not found
            image_url = f"{relative_image_path}/default.jpeg"

        # Add song data to the list
        songs.append({
            "id": idx + 1,
            "title": song_title,
            "formatted_title": formatted_title,  # Formatted title for display
            "image": image_url,  # Image URL path
            "file_path": os.path.join(relative_music_folder, filename).replace('\\', '/')  # Relative path with forward slashes
        })

# Convert the list to JSON format with indentation for readability
output_json = json.dumps(songs, indent=4)

# Save to a JSON file
output_path = 'sowhat.json'
with open(output_path, 'w') as json_file:
    json_file.write(output_json)

print(f"JSON file generated successfully at {output_path}!")
