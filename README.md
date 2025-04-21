# 🔍 Workforce flow of Innopolis University

## 📌 Overview

This project visualizes career transitions in the IT industry over the past years, using real data to track movements between companies, changes in in-demand skills, and the changing landscape of technology professions. By focusing on the technology community in Innopolis, we aim to show how professionals grow, move and adapt in a rapidly changing environment.
We explore:

- 📈 Frequency of company changes  
- 🕰️ Industry evolution over time  
- 🌐 Career centers and stepping stones  
- 🛠️ Skill popularity trends  
- 🧑‍💻 Occupational category transitions  

---

## 📊 Visualizations

### 1. **Tracing Career Paths**  
Each dot tells a story—watch how individuals move from Innopolis across the global tech ecosystem.

- **What you see:**  
  Node groups represent company clusters. Animated lines visualize individual career transitions.  

- **Tech used:**  
  `D3.js` for interactive 2D career graphs.

![Tracing Career Paths](public/gifs/tracing-career-paths.gif)

---

### 2. **Tech Skills That Matter**  
Track how demand for different tech skills shifts over the years.

- **What you see:**  
  Time-series bar chart race of skill frequencies based on job descriptions.

- **Tech used:**  
  D3.js transitions, reactive sliders for year selection.

![Tech Skills That Matter](public/gifs/skills-over-time.gif)

---

### 3. **The Tech Pie**  
See the tech team composition change through the years—roles that rise, fall, and reshape the industry.

- **What you see:**  
  Animated pie charts showing occupational categories annually.

- **Tech used:**  
  D3.js pie job categories with tooltip-based role descriptions.

![Tech Pie](public/gifs/tech-pie.gif)

---

## 📌 Conclusion

Through this data-driven journey, we've uncovered the unique patterns shaping the Innopolis tech community. From career transitions to skill evolution, each data point contributes to a deeper understanding of:

- 🚀 How people move and grow across roles and companies  
- 📚 Which skills define each era of IT evolution  
- 🌍 How Innopolis connects to the wider tech world  

This visualization isn't just a graph—it's a narrative of professional development, adaptation, and innovation.

---

## ✨ Project Highlights

- **Frontend**  
  - Interactive and dynamic visualizations using `D3.js`  
  - Clean UI/UX with responsive design  
  - Smooth transitions and tooltips
  - Filtering by job categories  

- **Backend**  
  - Data scraped from public profiles in LinkedIn  
  - Parsing and transformation scripts included  
  - Project deployed ([link](https://workforce-flow.onrender.com/))

- **GitHub Organization**  
  - Informative README  
  - Well-organized repo with logical folder structure  
  - Followed clean code and best practices  

---

## 📁 File Structure
```bash
.
├── checkpoints/                                # Processing checkpoints
├── data/ 
│   ├── EDA_and_processing/                     # Notebooks for exploratory data analysis
│   ├── processed_data/                         # Cleaned and ready-to-use .json files
│   ├── raw_data/                               # Original raw data before processing
│   │   ├── user_ids_collection/                # Collected user ID files from initial data scraping
│   │   ├── users_detailed_info_collection/     # Detailed info gathered per user
│   │   │   ├── data_1/                         # Subset of detailed user data (part 1)
│   │   │   ├── data_2/                         # Subset of detailed user data (part 2)
│   │   │   ├── IU_dataset.xlsx                 # Excel sheet with Innopolis University user data
│   │   │   └── retrieve_user_details.py        # Script for retrieving detailed user info
├── images/
├── preprocessing/                              # Scripts for cleaning, and transforming raw data to .json
├── web-application/                            # Web frontend and backend serving the visualizations
│   ├── css/                                    # Stylesheets for the web interface
│   ├── js/                                     # JavaScript files for interactivity and visualizations
│   ├── app.py                                  # Flask app runner
│   ├── index.html                              # Main HTML page served by the web app
│   └── requirements.txt                        # Python dependencies for the web app
├── .gitignore                                  # Specifies files/folders Git should ignore
├── Dockerfile                                  # Docker build instructions for app containerization
├── README.md                                   # Project overview and documentation
├── docker-compose.yml                          # Docker Compose file
└── render.yaml                                 # Deployment config file for Render.com
```

---

## 🚀 How to Launch

```bash
# Clone the repo
git clone https://github.com/Rufina2323/workforce-flow.git
cd workforce-flow

# Build and run with Docker
docker-compose up --build
```

## 🧩 Team

- **Data Scraping and Parsing:** Arina Goncharova  
- **Frontend & Visualizations:** Liana Mardanova  
- **EDA and Data Prerocessing:** Rufina Gafiiatullina  

---

## 🧱 Project Stages & Challenges

| Stage           | Problems                                      |Solutions                                      |
|------------------|----------------------------------------------------------|----------------------------------------------------------|
| Scaping with LinkedIn API         | The proposal for getting access to official LinkedIn API was rejected             | Used Selenium |
| Scaping with Selenium     | We reached the search limit            | Used [StaffSpy](https://github.com/cullenwatson/StaffSpy) |
| Scaping with [StaffSpy](https://github.com/cullenwatson/StaffSpy)     | It requires LinkedIn account to get the data            | Created ~ 30 accounts from different VPNs |
| Preprocessing    | Data were in different languages           | Used GoogleTranslator |
| Job categorization    | Classifying diverse job titles into clear categories was difficult | Used HuggingFaceEmbeddings model |
| Company grouping    | Finding similar companies was difficult  | Used keyword matching, and correction for edge cases|
| Docker           | Required debugging to ensure cross-platform deployment   | Refactored Dockerfile and docker-compose|
| Transitions visualization   | This D3 animation was too heavy   | Reduced node counts (200 nodes) |
