import os
import json
from bs4 import BeautifulSoup

# Define the output directory
output_dir = 'qjson'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read the HTML file
with open('questions.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Initialize variables
current_category = None
current_subcategory = None
questions_dict = {}

# Find all h2, h3, and ul elements
for element in soup.find_all(['h2', 'h3', 'ul']):
    if element.name == 'h2':
        current_category = element.get_text().strip()
        questions_dict[current_category] = {}
    elif element.name == 'h3':
        current_subcategory = element.get_text().strip()
        questions_dict[current_category][current_subcategory] = []
    elif element.name == 'ul' and current_category and current_subcategory:
        # Extract questions from li elements
        questions = [li.get_text().strip() for li in element.find_all('li')]
        questions_dict[current_category][current_subcategory] = questions

# Generate JSON files
for category, subcategories in questions_dict.items():
    for subcategory, questions in subcategories.items():
        # Create a safe filename from the subcategory
        filename = subcategory.replace(' ', '_').replace('/', '_').replace('?', '') + '.json'
        filepath = os.path.join(output_dir, filename)
        
        # Write questions to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)

print(f"JSON files have been generated in the '{output_dir}' directory.")