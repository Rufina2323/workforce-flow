# Workforce Flow: Mapping Job Movements Across Companies

## Project Goal and Vision
The aim of this project is to visualize career transitions in the IT industry over the past decades. By tracking the movement of employees between companies and highlighting different occupa- tions, we want to provide insight into industry trends, labor mobility, and career patterns.

Users will be able to find out:
- How often people change companies.
- How industries have evolved over time. 
- Whether certain companies are career centers or stepping stones.
- What skills were popular during a particular time period.
- How the percentage of occupational categories changed.

## Visualization Concepts
### Inter-company Transfer
- **Nodes**: Represent individuals in the workforce.
- **Node Groups**: Each company will be represented as a cluster of nodes.
- **Node Movement**: Nodes will change one company to another, showing career shifts.
- **Node Color**: Each company will be assigned a distinct color for better understanding.
- **Timeline Animation**: The visualization will be time-based, allowing users to watch career movements unfold over decades.

### Distribution by Skills
- **Nodes**: Represent individuals in the workforce.
- **Node Groups**: Each company will be represented as a cluster of nodes.
- **Node Movement**: Nodes will change one company to another, showing career shifts.
- **Node Color**: Each company will be assigned a distinct color for better understanding.
- **Timeline Animation**: The visualization will be time-based, allowing users to watch career movements unfold over decades.

### Distribution by Jobs
- **Nodes**: Represent individuals in the workforce.
- **Node Groups**: Each company will be represented as a cluster of nodes.
- **Node Movement**: Nodes will change one company to another, showing career shifts.
- **Node Color**: Each company will be assigned a distinct color for better understanding.
- **Timeline Animation**: The visualization will be time-based, allowing users to watch career movements unfold over decades.

## Dataset
Data will be retrieved using the [LinkedIn API](https://github.com/tomquirk/linkedin-api). We have chosen this approach because the official LinkedIn API requires registering an organization and obtaining approval, which we do not have.

The main goal of data collection step is to extract information about users. The proposed API makes it possible to obtain personal and employment information.

### Main Features
| Feature                     | Description |
|-----------------------------|---------------------------|
| id                          | Unique identifier for individuals. |
| name                        | Useful for labeling nodes. |
| location                    | Can be used for geographic career trend analysis. |
| estimated_age               | Helps analyze career trends by age group. |
| experiences                 | Key to tracking career progression. |
| schools                     | Helps in educational background analysis. |
| skills                      | Valuable for skill-based career trends. |
| certifications              | Adds information about professional development. |

## Team Members
- **Rufina Gafiiatullina** (r.gafiiatullina@innopolis.university)
- **Arina Goncharova** (a.goncharova@innopolis.university)
- **Liana Mardanova** (l.mardanova@innopolis.university)
