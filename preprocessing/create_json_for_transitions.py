import pandas as pd
import pickle
from tqdm import tqdm
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


# List of company name keywords to look for (in lowercase)
target_keywords = [
    "yandex", "sber", "tinkoff", "gazprom", "mts", "alfa", "x5", "icl", "ak bars", "akbars", "kazanexpress", "magnit market",
    "kaspersky", "vk", "innopolis university", "tbank", "rostelecom", "ozon"
]

# Store IDs of users that have worked in specified companies
all_users = set()

# Count matches
for index, experiences in enumerate(users_experiences):
    # Check that user has studied at Innopolis University
    if "innopolis" in users['school_1'][index].lower() or \
    "иннополис" in users['school_1'][index].lower() or \
    "innopolis" in users['school_2'][index].lower() or \
    "иннополис" in users['school_2'][index].lower():
        # Check the age
        if not users['estimated_age'][index] or users['estimated_age'][index] <= 35:
            for experience in experiences:
                # Check data relevance
                if not experience['company']:
                    continue
                if not experience['start_date']:
                    continue
                if pd.to_datetime(experience['start_date']) and pd.to_datetime(experience['start_date']).year < 2012:
                    continue
                name = experience['company'].lower()
                for keyword in target_keywords:
                    if keyword in name:
                        all_users.add(users['id'][index])
                        break  # one match per name is enough

# Store info about user work 
rows = []

# Mapping keywords with company name
target_keywords_dict = {"yandex": "Yandex", 
                        "sber": "Sber", 
                        "tinkoff": "TBank", 
                        "gazprom": "Gazprom", 
                        "mts": "MTS", 
                        "alfa": "Alfa", 
                        "x5": "X5 Retail Group", 
                        "icl": "ICL", 
                        "ak bars": "Ak Bars", 
                        "akbars": "Ak Bars", 
                        "kazanexpress": "Magnit Market", 
                        "magnit market": "Magnit Market", 
                        "kaspersky": "Kaspersky", 
                        "vk": "VK", 
                        "innopolis university": "Innopolis University", 
                        "tbank": "TBank", 
                        "rostelecom": "Rostelecom", 
                        "ozon": "Ozon",
                        "other": "Other",
                        "not working": "Not Working"
                        }

all_users = list(all_users)

# Iterate over user IDs
for user_id in tqdm(all_users):
    # Obtain user_experiences using index from ID 
    user_experiences = users_experiences[users[users['id'] == user_id].index[0]]
    # Create variable to catch case then end date is none, however it is not last user work
    potential_end_date = None
    # Save order of works
    work_counter = 0
    # Iterate over user work
    for experience in user_experiences:
        if not experience['company']:
            continue
        if not experience['start_date']:
            continue
        if pd.to_datetime(experience['start_date']) and pd.to_datetime(experience['start_date']).year < 2012:
            continue
        
        name = experience['company'].lower()

        # Create default dict with user info
        new_row = {'pid': user_id, 
                   'grp': target_keywords_dict["other"], 
                   'work_counter': work_counter,
                   'duration': 0, 
                   'name': users[users['id'] == user_id]['name'].values[0], 
                   'location': users[users['id'] == user_id]['location'].values[0], 
                   'estimated_age': users[users['id'] == user_id]['estimated_age'].values[0], 
                   'start_date': pd.to_datetime(experience['start_date']), 
                   'end_date': pd.to_datetime(experience['end_date']) if experience['end_date'] else potential_end_date, 
                   'job_position': experience['title'],
                   'company_name': experience['company']
                   }
        
        # Save start time
        potential_end_date = pd.to_datetime(experience['start_date'])

        # Change grp info if work from our considered companies
        for keyword in target_keywords_dict.keys():
            if keyword in name:
                new_row['grp'] = target_keywords_dict[keyword]
                break

        # Consider case when user change the work place and did not work sometime
        if len(rows) != 0 and rows[-1]['pid'] == new_row['pid']:
            if rows[-1]['start_date'] > new_row['end_date']:

                # Save "not working" case
                not_work_row = {'pid': user_id, 
                                'grp': target_keywords_dict["not working"], 
                                'work_counter': work_counter,
                                'duration': 0, 
                                'name': users[users['id'] == user_id]['name'].values[0], 
                                'location': users[users['id'] == user_id]['location'].values[0], 
                                'estimated_age': users[users['id'] == user_id]['estimated_age'].values[0], 
                                'start_date': new_row['end_date'], 
                                'end_date': rows[-1]['start_date'], 
                                'job_position': None,
                                'company_name': None
                                }
                work_counter += 1
                new_row['work_counter'] = work_counter
                rows.append(not_work_row)
        work_counter += 1
        rows.append(new_row)

# Create dataframe using work info
transitions = pd.DataFrame(rows)


def calculate_duration(row):
    if pd.isna(row['end_date']):
        return -99
    months = (row['end_date'].year - row['start_date'].year) * 12 + (row['end_date'].month - row['start_date'].month)

    # Consider partial months
    if row['end_date'].day < row['start_date'].day:
        months -= 1
    return months

# Calculate the duration of work in months
transitions['duration'] = transitions.apply(calculate_duration, axis=1)

def reverse_work_counter(row):
    total = transitions[transitions["pid"] == row["pid"]]["pid"].count()
    return total - row["work_counter"]

# Reverse the work order
transitions['work_counter'] = transitions.apply(reverse_work_counter, axis=1)


index = 0

# Normalize all users by 2013-12-31 date
while index < transitions.shape[0]:
    if transitions['work_counter'][index] == 1:
        duration = (transitions['start_date'][index].year - pd.to_datetime("2013-12-31").year) * 12 + (transitions['start_date'][index].month - pd.to_datetime("2013-12-31").month)
        new_row = pd.DataFrame([{'pid': transitions['pid'][index], 
                   'grp': target_keywords_dict["not working"], 
                   'work_counter': 0,
                   'duration': duration, 
                   'name': transitions['name'][index], 
                   'location': transitions['location'][index], 
                   'estimated_age': transitions['estimated_age'][index], 
                   'start_date': None, 
                   'end_date': None, 
                   'job_position': None,
                   'company_name': None
                   }])
        index += 1
        transitions = pd.concat([transitions.iloc[:index], new_row, transitions.iloc[index:]]).reset_index(drop=True)
        
    index += 1

# Drop useless columns
transitions.drop(columns=['start_date', 'end_date'], inplace=True)

# Change the order of data to send it to frontend
transitions = transitions.iloc[::-1].reset_index(drop=True)

# Save to JSON file
transitions.to_json("data/processed_data/transitions.json", orient="records", indent=4)