# Data collection

## 🔎 LinkedIn data
1. Collected user_ids using selenium and different search approaches (search by university, keywords and [LinkedIn API](https://github.com/tomquirk/linkedin-api) from GitHub repository that stopped working after our attempts 😅)

This data is stored in folder `user_ids_collection` in `*.csv` files.

2. Using retrieved user_ids collected the detailed user info using [StaffSpy](https://github.com/cullenwatson/StaffSpy).


To retrieve users we created many LinkedIn accounts. One account allows to get ~ 50 users. The code for collecting users' details can be found in `retrieve_user_details.py`.

This data is stored in folder `users_detailed_info_collection` in folders `data_1` and `data_2`.

Using Linkedin we collected data about 1737 LinkedIn users who are connected to Innopolis university with 45 attributes.

## 🔎 Innopolis University dataset

We asked Innopolis University for the data about alumni employments. Accorfing to policies, university provided as anonymized information that is stored in `IU_dataset.xlsx`.

The Innopolis University dataset contains information about 377 students.
