from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# open login page
driver.get("https://www.linkedin.com/login")

# wait for manual login
input("Press Enter after logging in to continue...")

# visit Innopolis University's people alumni page
driver.get("https://www.linkedin.com/school/innopolis-university/people/")
time.sleep(5)

# click on Alumni tab if not already selected
try:
    # using text content (more reliable)
    alumni_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alumni')]"))
    )
    alumni_tab.click()
    print("Switched to Alumni tab")
    time.sleep(3)
except Exception as e:
    print(f"Error switching to Alumni tab: {e}")

# scrolling parameters
max_scrolls = 100 
scroll_count = 0
alumni_data = [] 
processed_profile_ids = set()

# extract card data
def extract_card_data(card):
    try:
        # extract the profile ID or URL
        profile_link_elem = card.find_element(By.CSS_SELECTOR, "a.app-aware-link")
        profile_link = profile_link_elem.get_attribute("href")
        
        if not profile_link or "/in/" not in profile_link:
            return None
            
        profile_id = profile_link.split("/in/")[-1].strip("/").split("?")[0]
        
        # check for duplicates
        if profile_id in processed_profile_ids:
            return None 
            
        # extract name
        try:
            name_element = card.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-title")
        except:
            try:
                name_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title")
            except:
                name_element = None
        
        name = name_element.text.strip() if name_element else "Unknown"
        
        # extract description 
        try:
            description_element = card.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-description")
        except:
            try:
                description_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
            except:
                description_element = None
                
        description = description_element.text.strip() if description_element else ""
        
        # add profile to processed set
        processed_profile_ids.add(profile_id)
        
        return {
            "name": name,
            "description": description,
            "url": profile_link,
            "id": profile_id
        }
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

# function to scroll and collect alumni profiles
def scroll_and_collect_alumni():
    global scroll_count, max_scrolls, driver, alumni_data
    
    scroll_count = 0
    show_more_clicks = 0
    max_show_more_clicks = 30
    
    while scroll_count < max_scrolls:
        # click "Show more results" button if it exists
        try:
            # selectors for Show more button
            show_more_selectors = [
                "//button[contains(text(), 'Show more results')]",  # XPath with exact text
                "button.scaffold-finite-scroll__load-button",
                "button.artdeco-button--muted",
                "button.artdeco-pagination__button--next",
                "//button[contains(@aria-label, 'Show more')]"  # XPath with aria-label
            ]
            
            button_found = False
            for selector in show_more_selectors:
                try:
                    if selector.startswith("//"):
                        show_more_buttons = driver.find_elements(By.XPATH, selector)
                    else:
                        show_more_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if show_more_buttons:
                        for button in show_more_buttons:
                            if button.is_displayed() and button.is_enabled():
                                print(f"Found button with text: '{button.text}'")
                                # scroll to the button 
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                # wait
                                time.sleep(2) 
                                
                                # try clicking with JS
                                try:
                                    driver.execute_script("arguments[0].click();", button)
                                except:
                                    button.click()
                                    
                                show_more_clicks += 1
                                button_found = True
                                print(f"Clicked 'Show more results' button ({show_more_clicks} times)")
                                time.sleep(5)
                                break
                        
                        if button_found:
                            break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
        except Exception as e:
            print(f"Error finding 'Show more results' button: {e}")
        
        # prevent infinite loops
        if show_more_clicks >= max_show_more_clicks:
            print(f"Reached maximum 'Show more results' clicks ({max_show_more_clicks})")
            break
            
        # process alumni cards
        try:
            # wait for cards to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.scaffold-finite-scroll__content"))
            )
            
            # multiple selectors to find the cards
            cards = []
            card_selectors = [
                "li.org-people-profile-card",
                "li.org-people-profile-card__profile-card-spacing",
                "div.artdeco-card.org-people-profile-card__card-spacing",
                "div.org-people-profile-card",
                ".scaffold-finite-scroll__content > ul > li"
            ]
            
            for selector in card_selectors:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    break
            
            print(f"Found {len(cards)} alumni cards")
            
            # extract data from cards
            new_profiles = 0
            for card in cards:
                user_data = extract_card_data(card)
                if user_data:
                    alumni_data.append(user_data)
                    new_profiles += 1
            
            print(f"Added {new_profiles} new profiles (total: {len(alumni_data)})")
            
            # avoid stacking in the bottom
            if new_profiles == 0 and scroll_count > 5:
                print("No new profiles found in this iteration, might have reached the end")
            
        except Exception as e:
            print(f"Error processing alumni cards: {e}")
        
        # scroll down to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scrolled down ({scroll_count + 1}/{max_scrolls})")
        scroll_count += 1
        time.sleep(3) 
        
        # check for finishing
        try:
            no_more_results_selectors = [
                ".artdeco-empty-state__message", 
                "//p[contains(text(), 'No more results')]",
                "//div[contains(text(), 'You've viewed all results')]"
            ]
            
            for selector in no_more_results_selectors:
                elements = driver.find_elements(By.XPATH if selector.startswith("//") else By.CSS_SELECTOR, selector)
                if elements and any(("No more" in e.text or "viewed all" in e.text) for e in elements if e.text):
                    print("Reached end of results, no more data to load")
                    return alumni_data
        except:
            pass

    return alumni_data

# get all alumni
all_alumni = scroll_and_collect_alumni()

# save the results
with open("innopolis_alumni_info_2.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "description", "url", "id"])
    for user in all_alumni:
        writer.writerow([user["name"], user["description"], user["url"], user["id"]])

print(f"Collected {len(all_alumni)} alumni profiles")

# close the driver
driver.quit()