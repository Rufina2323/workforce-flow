from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# set browser options
options = Options()
# set full screen
options.add_argument("--start-maximized") 
# hide selenium
options.add_argument("--disable-blink-features=AutomationControlled") 

# start chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# open linkedin login page
driver.get("https://www.linkedin.com/login")

# wait for manual login
input("Press Enter after logging in to continue...")

# visit "People you may know" section
driver.get("https://www.linkedin.com/mynetwork/grow/")
time.sleep(5) 

# open modal to get more people
try:
    button = driver.find_element(By.CSS_SELECTOR, "div._1k2lxmev4._1k2lxmeyw._1k2lxme12w._1k2lxme16o.cnuthtb4.cnuthtds.cnutht18g.cnutht14.cnuththk.cnuthth4 > div > button")
    ActionChains(driver).move_to_element(button).click().perform()
    print("Modal window was opened")
    time.sleep(5)
except Exception as e:
    print("Error opening modal window", e)
    driver.quit()
    exit()

# find cards with users
cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-view-name="cohort-card"]')
print(f"Found {len(cards)} cards with user info")


def scroll_and_collect():
    users = []
    # num of users before scrolling
    last_count = 0  

    while True:
        # get all profile cards
        cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-view-name="cohort-card"]')

        # extract data from new cards
        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, 'p._12p2gmq9._1s9oaxg7').text
                description = card.find_element(By.CSS_SELECTOR, 'p._12p2gmq9._12p2gmq2').text
                profile_url = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

                user_data = {
                    "name": name,
                    "description": description,
                    "url": profile_url
                }

                # check for duplicates
                if user_data not in users:
                    users.append(user_data)

            except Exception as e:
                print(f"Error while parsing card: {e}")

        # stop scrolling, if no new users are found
        if len(users) == last_count:
            break
        last_count = len(users)

        # scroll down
        driver.execute_script("arguments[0].scrollIntoView();", cards[-1])
        # wait for loading
        time.sleep(10) 

    return users

# get all users
all_users = scroll_and_collect()

# save the results
with open("initial_users_info.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "description", "url"])
    for user in all_users:
        writer.writerow([user["name"], user["description"], user["url"]])

print(f"Collected {len(all_users)} profiles")

# close the driver
driver.quit()