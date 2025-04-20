# Import required libraries
import pandas as pd
from tqdm import tqdm
import ast
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import torch
import pickle


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


# Extract only unique positions for language standartization
titles = set()
for experiences in users_experiences:
    for experience in experiences:
        titles.add(experience['title'])

jobs = list(titles)

# Assign suitable device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Proper job categories
job_categories = ['Software Engineering',
                  'Data & Analytics',
                  'Infrastructure & Networks',
                  'Cloud & DevOps',
                  'Cybersecurity',
                  'Machine Learning & AI',
                  'Product & Project Management',
                  'IT Support & Administration',
                  'UI/UX & Design',
                  'Other']

# Initialize model for embeddings
model_kwargs = {'device': device}
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs=model_kwargs)

# Create for main categories embeddings
job_category_vectors = embedding_model.embed_documents(job_categories)

faiss_index = FAISS.from_texts(job_categories, embedding_model)

# Store matching to the map
job_categories_map = {}

for job in tqdm(jobs):
    category = faiss_index.similarity_search(job, k=1)[0].page_content
    job_categories_map[job] = category

with open("preprocessing/job_categories_map.pkl", "wb") as f:
    pickle.dump(job_categories_map, f)