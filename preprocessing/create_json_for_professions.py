import pandas as pd
import pickle
from datetime import datetime
from tqdm import tqdm
import json
import ast

# Read data
users = pd.read_csv('preprocessing/users.csv')

# Create list for users experiences
users_experiences = []

# Go through users['experiences'] to convert it in proper format
for experiences in users['experiences']:
    # If experience is empty, then skip it
    if len(experiences) == 0:
        users_experiences.append([])
        continue
    # Convert the string to a list
    data_list = ast.literal_eval(experiences)
    users_experiences.append(data_list)

# Load the mapping to categories
with open("preprocessing/job_categories_map.pkl", "rb") as f:
    job_categories_map = pickle.load(f)

# Create map to store number of people in each category
job_categories = {'Software Engineering': 0,
                  'Data & Analytics': 0,
                  'Infrastructure & Networks': 0,
                  'Cloud & DevOps': 0,
                  'Cybersecurity': 0,
                  'Machine Learning & AI': 0,
                  'Product & Project Management': 0,
                  'IT Support & Administration': 0,
                  'UI/UX & Design': 0,
                  'Other': 0}

# Store info for each year
professions = {}

# Iterate over users_experiences 
for experiences in tqdm(users_experiences, total=users.shape[0]):
    for experience in experiences:
        # Extract start and end dates of working
        start_date = pd.to_datetime(experience['start_date']) if experience['start_date'] else pd.to_datetime(datetime.today())
        end_date = pd.to_datetime(experience['end_date']) if experience['end_date'] else pd.to_datetime(datetime.today())

        # Go through the interval from the start year to the end year and change the desired one
        for year in range(max(start_date.year, 2012), end_date.year + 1):
            category = job_categories_map[experience['title']]
            if year not in professions:
                professions[year] = job_categories.copy()
            professions[year][category] += 1

# Store data to json
with open("data/processed_data/professions.json", "w", encoding='utf-8') as f:
    json.dump(professions, f, indent=4)