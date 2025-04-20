import pandas as pd
import pickle
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
    # print(experiences)
    # Convert the string to a list
    data_list = ast.literal_eval(experiences)
    users_experiences.append(data_list)

# Load the mapping to categories
with open("preprocessing/job_categories_map.pkl", "rb") as f:
    job_categories_map = pickle.load(f)


# Create list for users experiences
users_skills = []

# Go through users['experiences'] to convert it in proper format
for skills in users['skills']:
    # If experience is empty, then skip it
    if len(skills) == 0:
        users_skills.append([])
        continue
    # Convert the string to a list
    data_list = ast.literal_eval(skills)
    users_skills.append(data_list)

# Create dict to store result
skills_dict = {"Software Engineering": {},
                "Data & Analytics": {},
                "Infrastructure & Networks": {},
                "Cloud & DevOps": {},
                "Cybersecurity": {},
                "Machine Learning & AI": {},
                "Product & Project Management": {},
                "IT Support & Administration": {},
                "UI/UX & Design": {},
                "Other": {}
                }

# Iterate over users_skills
for index, user_skills in tqdm(enumerate(users_skills), total=users.shape[0]):
    categories = set()
    # For each user obtain only unique job categories
    for experience in users_experiences[index]:
        category = job_categories_map[experience['title']]
        categories.add(category)

    # For obtained categories calculate for each skill number of people
    for category in list(categories):
        for skill in user_skills:
            if skill == 'Python (Programming Language)':
                skill = "Python"
            if skill == 'Natural Language Processing (NLP)':
                skill = "NLP"
            skills_dict[category][skill] = 1 + skills_dict[category].get(skill, 0)

top_skills = {}

for category, skills in skills_dict.items():
    # Sort the skills by value (descending) and take the top 10
    sorted_skills = dict(sorted(skills.items(), key=lambda item: item[1], reverse=True)[:10])
    top_skills[category] = sorted_skills

# Build the final JSON structure
output = {
    "professions": []
}

for category, skills in top_skills.items():
    # Format for JSON structure
    profession_entry = {
        "profession_name": category,
        "top_skills": [
            {
                "skill_name": skill,
                "number_of_professionals": count
            } for skill, count in skills.items()
        ]
    }

    output["professions"].append(profession_entry)

# Save to JSON file
with open("data/processed_data/skills.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4)