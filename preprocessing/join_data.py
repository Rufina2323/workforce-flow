# Import required libraries
import pandas as pd
import numpy as np
from tqdm import tqdm
import ast
from deep_translator import GoogleTranslator
# from googletrans import Translator

# def translate_text(text):
#     translated = GoogleTranslator(source='auto', target='en').translate(text)
#     return translated

# Initialize the translator
# translator = Translator()

# Apply progress bar to dataframe
tqdm.pandas()

# Function to translate text to English
def translate_to_english(text):

    # Detect non-English characters
    if text and not text.isascii():
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except:
            return text
    return text


def create_experiences(row):
    if "." in str(row['Дата трудоустройства']):
        day, month, year = str(row['Дата трудоустройства']).split(".")
    else:
        year, month, day = str(row['Дата трудоустройства']).split("-")
        day = day.split(" ")[0]

    return str([{'start_date': year+"-"+month+"-"+day, 'end_date': None, 'title': row['Должность'], 'company': row['Организация']}])


data_1 = 'data/raw_data/users_detailed_info_collection/data_1/'
data_2 = 'data/raw_data/users_detailed_info_collection/data_2/'

# Concatenate all dataframes into one common users dataframe
users = pd.concat([pd.read_csv(f'{data_1}users_0_100.csv'),
                   pd.read_csv(f'{data_1}users_100_200.csv'),
                   pd.read_csv(f'{data_1}users_200_300.csv'),
                   pd.read_csv(f'{data_1}users_300_400.csv'),
                   pd.read_csv(f'{data_1}users_400_500.csv'),
                   pd.read_csv(f'{data_1}users_500_550.csv'),
                   pd.read_csv(f'{data_1}users_550_552.csv'),
                   pd.read_csv(f'{data_1}users_552_600.csv'),
                   pd.read_csv(f'{data_1}users_600_700.csv'),
                   pd.read_csv(f'{data_1}users_700_745.csv'),
                   pd.read_csv(f'{data_1}users_745_843.csv'),
                   pd.read_csv(f'{data_2}users_0_31.csv'),
                   pd.read_csv(f'{data_2}users_31_103.csv'),
                   pd.read_csv(f'{data_2}users_103_155.csv'),
                   pd.read_csv(f'{data_2}users_155_228.csv'),
                   pd.read_csv(f'{data_2}users_228_294.csv'),
                   pd.read_csv(f'{data_2}users_294_363.csv'),
                   pd.read_csv(f'{data_2}users_363_406.csv'),
                   pd.read_csv(f'{data_2}users_406_477.csv'),
                   pd.read_csv(f'{data_2}users_477_517.csv'),
                   pd.read_csv(f'{data_2}users_517_560.csv'),
                   pd.read_csv(f'{data_2}users_560_684.csv'),
                   pd.read_csv(f'{data_2}users_684_793.csv'),
                   pd.read_csv(f'{data_2}users_793_838.csv'),
                   pd.read_csv(f'{data_2}users_838_893.csv'),
                   pd.read_csv(f'{data_2}users_893_924.csv')],
                  ignore_index=True)

# Extract usefull columns
users = users[['id', 'name', 'location', 'estimated_age',
               'experiences', 'skills', 'school_1', 'school_2']].copy()

# Drop rows with duplicated ids
users = users.drop_duplicates(subset='id', keep='first')

# Fill missing values in location
users.fillna({'location': 'no location', 'school_1': 'no', 'school_2': 'no'}, inplace=True)

# Fill missing list values separately
for col in ['experiences', 'skills']:
    users[col] = users[col].apply(lambda x: [] if pd.isna(x) else x)

# Work with IU dataset
IU_dataset = pd.read_excel('data/raw_data/users_detailed_info_collection/IU_dataset.xlsx', header=2)

# Drop rows with duplicated information
IU_dataset = IU_dataset.drop_duplicates(subset=['Организация', 'Должность', 'Дата трудоустройства'], keep='first').copy()

# Create needed columns to join dataframes further
IU_dataset['id'] = IU_dataset['ID']
IU_dataset['name'] = [f"Student {id}" for id in IU_dataset['ID']]
IU_dataset['location'] = ["no location" for _ in range(IU_dataset.shape[0])]
IU_dataset['estimated_age'] = [np.nan for _ in range(IU_dataset.shape[0])]
IU_dataset['experiences'] = IU_dataset.apply(create_experiences, axis=1)
IU_dataset['skills'] = [[] for _ in range(IU_dataset.shape[0])]
IU_dataset['school_1'] = ["Innopolis University" for _ in range(IU_dataset.shape[0])]
IU_dataset['school_2'] = ["no" for _ in range(IU_dataset.shape[0])]

# Drop columns
IU_dataset.drop(columns=['Анкета трудоустройства.Дата', 'ID', 'Дата трудоустройства', 'Должность', 'Организация'], inplace=True)

# Merge all data
users = pd.concat([users, IU_dataset], ignore_index=True)

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
    user_experiences = []

    # Store only dates, position, company name, and work type (full time, part time, and etc.)
    for experience in data_list:
        user_experience = {'start_date': experience['start_date'],
                            'end_date': experience['end_date'],
                            'title': experience['title'],
                            'company': experience['company']
                            }

        user_experiences.append(user_experience)
    users_experiences.append(user_experiences)

# Extract only unique positions for language standartization
titles = set()
companies = set()
for experiences in users_experiences:
    for experience in experiences:
        titles.add(experience['title'])
        companies.add(experience['company'])

titles_list = list(titles)
companies_list = list(companies)

# Translate to English all positions and store its translation
translated_titles = {}
for title in tqdm(titles_list):
    translated_titles[title] = translate_to_english(title)

# Translate to English all company names and store its translation
translated_companies = {}
for company in tqdm(companies_list):
    translated_companies[company] = translate_to_english(company)

# Convert positions and companies in dataframe to English version
for experiences in users_experiences:
    for experience in experiences:
        experience['title'] = translated_titles[experience['title']]
        experience['company'] = translated_companies[experience['company']]

# Assign new experiences column
users['experiences'] = users_experiences


# Create list for users skills
users_skills = []

# Go through users['skills'] to convert it in proper format
for skills in tqdm(users['skills'], total=users.shape[0]):
    # If skills is empty, then skip it
    if len(skills) == 0:
        users_skills.append([])
        continue
    # Convert the string to a list
    data_list = ast.literal_eval(skills)
    user_skills = []

    # Store only name of skills
    for skills_from_user in data_list:
        user_skills.append(translate_to_english(skills_from_user['name']))
    users_skills.append(user_skills)

users['skills'] = users_skills

users.to_csv('preprocessing/users.csv', index=False)