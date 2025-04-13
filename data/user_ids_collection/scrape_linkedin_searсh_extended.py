from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import pandas as pd
import re

# set up browser options
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

# initialize the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# open login page
driver.get("https://www.linkedin.com/login")

# wait for manual login
input("Please log in manually and press Enter when ready...")

# function to extract data from a profile card
def extract_profile_data(card):
    try:
        # extract profile URL and ID
        try:
            profile_link_elem = card.find_element(By.CSS_SELECTOR, "a.onRHPXypfWLuNOCinrLJfqDJJJaXLBUXSKz[href*='/in/']")
            profile_url = profile_link_elem.get_attribute("href")
            
            # clean up the URL 
            profile_url = re.sub(r'\?miniProfileUrn=.*', '', profile_url)
            
            # extract user_id from URL
            user_id = re.search(r'/in/([^/?]+)', profile_url)
            user_id = user_id.group(1) if user_id else ""
        except Exception as e:
            print(f"Error extracting profile link: {e}")
            
            # try alternative selectors
            try:
                # Try alternative selectors
                selectors = [
                    # without href filter
                    "a.onRHPXypfWLuNOCinrLJfqDJJJaXLBUXSKz",
                    # any link with /in/ path 
                    "a[href*='/in/']",                        
                    "a.app-aware-link"                   
                ]
                
                for selector in selectors:
                    elements = card.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and '/in/' in href:
                            profile_url = href
                            # clean the URL
                            profile_url = re.sub(r'\?miniProfileUrn=.*', '', profile_url)
                            user_id = re.search(r'/in/([^/?]+)', profile_url)
                            user_id = user_id.group(1) if user_id else ""
                            if user_id:
                                break
                    if user_id:
                        break
            except:
                profile_url = ""
                user_id = ""
        
        # extract name
        try:
            # possible selectors
            name_selectors = [
                "span.HRhgvrlUQaNUjqZvHFUQPuVJeCYVVgEweHDSJUA a",  
                "a.onRHPXypfWLuNOCinrLJfqDJJJaXLBUXSKz span[dir='ltr']",
                "span.entity-result__title-text a",                     
                "span.artdeco-entity-lockup__title"                     
            ]
            
            name = "Unknown"
            for selector in name_selectors:
                try:
                    elements = card.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        name_elem = elements[0]
                        name = name_elem.text.strip()
                        # clean up any hidden text markers
                        name = re.sub(r'View\s+[\w\s]+\'s\s+profile', '', name)
                        name = name.strip()
                        if name: 
                            break
                except:
                    continue
        except Exception as e:
            print(f"Error extracting name: {e}")
            name = "Unknown"
        
        # extract description
        try:
            desc_selectors = [
                "div.TmhqKVgxpVFoDdYnKiMIkkTPeoywzixNLXovdrw",  
                "div.entity-result__primary-subtitle",
                "div.t-14.t-black.t-normal"             
            ]
            
            description = ""
            for selector in desc_selectors:
                try:
                    elements = card.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        desc_elem = elements[0]
                        description = desc_elem.text.strip()
                        if description:
                            break
                except:
                    continue
        except Exception as e:
            print(f"Error extracting description: {e}")
            description = ""
        
        # extract location
        try:
            loc_selectors = [
                "div.eDoCapdtCHaaqGmFnsIyAPMKjrgPGOOrQ",    
                "div.entity-result__secondary-subtitle",    
                ".t-14.t-normal:not(.t-black)"      
            ]
            
            location = ""
            for selector in loc_selectors:
                try:
                    elements = card.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        loc_elem = elements[0]
                        location = loc_elem.text.strip()
                        if location:
                            break
                except:
                    continue
        except:
            location = ""
            
        return {
            "name": name,
            "description": description,
            "location": location,
            "url": profile_url,
            "id": user_id
        }
    except Exception as e:
        print(f"Error extracting card data: {e}")
        return None

# function to search and extract profiles
def search_and_extract(search_url, max_pages=20):
    # extract base URL for pagination
    base_search_url = search_url
    if "page=" in base_search_url:
        base_search_url = re.sub(r'&page=\d+', '', base_search_url)
    
    # go to the first page
    driver.get(search_url)
    time.sleep(3)
    
    all_profiles = []
    processed_ids = set() 
    current_page = 1
    
    while current_page <= max_pages:
        print(f"Processing page {current_page} of {max_pages}")
        
        # wait for loading search results
        try:
            result_selectors = [
                "ul.JzzvftOqOYkcrssyumZALQrxzuqDoutvBA",  # New LinkedIn class
                "ul[role='list']",  # Generic role-based selector
                "div.reusable-search__entity-result-list",  # Old selector
                ".search-results-container"  # Another fallback
            ]
            
            for selector in result_selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"Found results container with selector: {selector}")
                    time.sleep(5)
                    break
                except:
                    continue
            else:
                raise Exception("Could not find any results container")
                
        except Exception as e:
            print(f"Error waiting for search results: {e}")
            # debugging
            with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved page source to 'linkedin_debug.html' for debugging")
            
            break
        
        # get all profile cards on the current page
        try:
            # scroll to load the content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            
            # possible selectors for profile cards
            card_selectors = [
                "li.tDfphBmQslIXKQzHkydHYPMOKfvxiBLINLOBw",  
                "div.UsPYSiMsBednWmzFJBjctvEfXFbahwbs",      
                "li.reusable-search__result-container",      
                "div[data-chameleon-result-urn]",           
                "div.entity-result",                        
                "li[role='listitem']",                       
                ".search-results-container > ul > li"       
            ]
            
            cards = []
            for selector in card_selectors:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    print(f"Found {len(cards)} cards with selector: {selector}")
                    
                    # try another selector if  we found fewer than 10 cards 
                    if len(cards) < 10:
                        print("Found fewer than expected cards, trying another selector...")
                        continue
                        
                    break
            
            # if not 10 cards were found
            if not cards or len(cards) < 8: 
                print(f"Found only {len(cards)} cards (expecting around 10) - trying broader approach")
                
                # try another approach
                try:
                    # find the results container
                    result_container = None
                    for container_selector in result_selectors:  # Use the result_selectors from earlier
                        containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
                        if containers:
                            result_container = containers[0]
                            break
                    
                    if result_container:
                        # find all potential cards within the container using a more generic approach
                        potential_cards = result_container.find_elements(By.CSS_SELECTOR, "li, div[class*='result']")
                        
                        # filter elements that could be profile cards
                        filtered_cards = []
                        for item in potential_cards:
                            # check for profile-like content
                            has_link = len(item.find_elements(By.TAG_NAME, "a")) > 0
                            has_content = len(item.text) > 20
                            
                            if has_link and has_content:
                                filtered_cards.append(item)
                        
                        if filtered_cards:
                            cards = filtered_cards
                            print(f"Found {len(cards)} cards using comprehensive detection")
                except Exception as e:
                    print(f"Error in comprehensive card detection: {e}")
            
            if not cards:
                print("No cards found on this page after all detection attempts")
                
                # save the html and take a screenshot for debugging
                with open("missing_cards_debug.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot("missing_cards_debug.png")
                print("Saved debug files for manual inspection")
                
                # go to the next page
                continue
            
            print(f"Final card count: {len(cards)} - proceeding with extraction")
                    
            # extract data from each card
            page_profiles = []
            for card in cards:
                profile_data = extract_profile_data(card)
                if profile_data and profile_data["id"] and profile_data["id"] not in processed_ids:
                    processed_ids.add(profile_data["id"])
                    page_profiles.append(profile_data)
            
            print(f"Extracted {len(page_profiles)} new profiles from page {current_page}")
            all_profiles.extend(page_profiles)
            
            # save results
            if current_page % 5 == 0 or len(all_profiles) % 50 == 0:
                save_to_csv(all_profiles, "linkedin_search_results_progress.csv")
                
        except Exception as e:
            print(f"Error processing page {current_page}: {e}")
            driver.save_screenshot(f"error_page_{current_page}.png")
            print(f"Saved screenshot to error_page_{current_page}.png")
        
        # go to next page
        try:
            next_page = current_page + 1
            
            print(f"Using direct URL navigation to page {next_page}...")
            if direct_page_navigation(base_search_url, next_page):
                print(f"✓ Successfully navigated to page {next_page}")
                current_page = next_page
                continue
            
            print("All pagination methods failed - stopping search")
            break
            
        except Exception as e:
            print(f"Error during page navigation: {e}")
            break
    
    return all_profiles

# function to save profiles to CSV
def save_to_csv(profiles, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "description", "location", "url", "id"])
        for profile in profiles:
            writer.writerow([
                profile["name"], 
                profile["description"], 
                profile["location"],
                profile["url"], 
                profile["id"]
            ])
    print(f"Saved {len(profiles)} profiles to {filename}")

def debug_pagination_issues():
    print("\n==== DEBUGGING PAGINATION ISSUES ====")
    
    # save the current page source for debugging
    with open("pagination_debug_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved full page source to 'pagination_debug_source.html'")
    
    # take a screenshot of the page
    driver.save_screenshot("pagination_debug_screenshot.png")
    print("Saved screenshot to 'pagination_debug_screenshot.png'")
    
    # check that pagination container exists at all
    pagination_containers = driver.find_elements(By.CSS_SELECTOR, "div.artdeco-pagination")
    if pagination_containers:
        print(f"Found pagination container: {len(pagination_containers)} element(s)")
        
        # get container attributes
        container = pagination_containers[0]
        print(f"Container class: {container.get_attribute('class')}")
        print(f"Container ID: {container.get_attribute('id')}")
        
        # page state info
        try:
            page_state = container.find_element(By.CSS_SELECTOR, ".artdeco-pagination__page-state")
            print(f"Page state text: '{page_state.text}'")
        except:
            print(" No page state element found")
        
        # pagination buttons
        pagination_buttons = container.find_elements(By.TAG_NAME, "button")
        print(f"  Found {len(pagination_buttons)} buttons in pagination container")
        
        # "Next" button
        next_buttons = []
        for btn in pagination_buttons:
            btn_text = btn.text.strip()
            btn_class = btn.get_attribute("class") or ""
            btn_disabled = btn.get_attribute("disabled")
            btn_aria = btn.get_attribute("aria-label")
            
            print(f"Button: text='{btn_text}', aria-label='{btn_aria}', disabled='{btn_disabled}'")
            
            if (btn_text == "Next" or 
                "Next" in (btn_aria or "") or 
                "next" in btn_class.lower()):
                next_buttons.append(btn)
                print(f"Potential Next button found: '{btn_text}', disabled='{btn_disabled}'")
                
                # If the button is disabled, we've reached the last page
                if btn_disabled == "true" or "disabled" in btn_class:
                    print("Next button is disabled - you've reached the last page")
                    return "LAST_PAGE"
    else:
        print("No pagination container found! Possible reasons:")
    
    
    # сheck for end of results message
    end_indicators = [
        "You've reached the end", 
        "No more results",
        "End of results", 
        "No matching results"
    ]
    
    for text in end_indicators:
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
        if elements:
            print(f"Found end of results message: '{elements[0].text}'")
            return "END_OF_RESULTS"
    
    # сheck if we're on a security challenge page
    security_indicators = [
        "verify", "captcha", "security", "check", "robot"
    ]
    
    for text in security_indicators:
        elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
        if elements:
            print(f"Security verification likely detected: '{elements[0].text}'")
            return "SECURITY_CHALLENGE"
    
    # check if the profile is logged in
    signin_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign in')]")
    if signin_elements:
        print("Session may have expired - 'Sign in' text detected")
        return "SESSION_EXPIRED"
    
    print("==== END PAGINATION DEBUGGING ====\n")
    return "UNKNOWN_ISSUE"

def try_scroll_for_more_results():
    print("Attempting to scroll for more results (in case of infinite loading)")
    
    # get current number of results
    initial_cards = len(driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container"))
    if initial_cards == 0:
        # Try alternative selector
        initial_cards = len(driver.find_elements(By.CSS_SELECTOR, "li.tDfphBmQslIXKQzHkydHYPMOKfvxiBLINLOBw"))
    
    print(f"Currently {initial_cards} results visible")
    
    # scroll down multiple times with pauses
    for scroll in range(3):
        # scroll to the bottom of the current view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scroll attempt {scroll+1}/3...")
        time.sleep(2)
    
    new_cards = len(driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container"))
    if new_cards == 0:
        # try alternative selector
        new_cards = len(driver.find_elements(By.CSS_SELECTOR, "li.tDfphBmQslIXKQzHkydHYPMOKfvxiBLINLOBw"))
    
    if new_cards > initial_cards:
        print(f"Success! Loaded {new_cards - initial_cards} more results by scrolling")
        return True
    else:
        print("No additional results loaded by scrolling")
        return False

def try_url_based_navigation():
    """Try to navigate to the next page by directly manipulating the URL"""
    current_url = driver.current_url
    print(f"Attempting URL-based navigation from: {current_url}")
    
    next_url = None
    
    # check for page parameter
    page_match = re.search(r'page=(\d+)', current_url)
    if page_match:
        current_page_num = int(page_match.group(1))
        next_url = current_url.replace(f"page={current_page_num}", f"page={current_page_num+1}")
        print(f"Modified URL using page parameter: {next_url}")
        
    # check for start parameter
    elif "start=" in current_url:
        start_match = re.search(r'start=(\d+)', current_url)
        if start_match:
            current_start = int(start_match.group(1))
            next_start = current_start + 25  # LinkedIn typically shows 25 results per page
            next_url = current_url.replace(f"start={current_start}", f"start={next_start}")
            print(f"Modified URL using start parameter: {next_url}")
    
    # try navigating to new URL 
    if next_url:
        try:
            driver.get(next_url)
            print(f"Navigated to: {next_url}")
            time.sleep(5)  
            
            results = driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
            if not results:
                # alternative selector
                results = driver.find_elements(By.CSS_SELECTOR, "li.tDfphBmQslIXKQzHkydHYPMOKfvxiBLINLOBw") 
            
            if results:
                print(f"Successfully loaded next page with {len(results)} results")
                return True
            else:
                print("Navigation successful but no results found")
                return False
        except Exception as e:
            print(f"Error during URL navigation: {e}")
            return False
    
    print("Could not determine appropriate URL modification pattern")
    return False

def direct_page_navigation(base_url, page_number):
    
    # extract the base URL without pagination number
    if "page=" in base_url:
        # remove existing page number
        base_url = re.sub(r'&page=\d+', '', base_url)
    
    # add the page parameter
    if "?" in base_url:
        next_url = f"{base_url}&page={page_number}"
    else:
        next_url = f"{base_url}?page={page_number}"
    
    print(f"Navigating directly to page {page_number} via URL: {next_url}")
    
    # navigate to the URL
    driver.get(next_url)
    time.sleep(5) 
    
    result_selectors = [
        "ul.JzzvftOqOYkcrssyumZALQrxzuqDoutvBA",
        "ul[role='list']",
        "div.reusable-search__entity-result-list"
    ]
    
    for selector in result_selectors:
        results = driver.find_elements(By.CSS_SELECTOR, selector)
        if results:
            print(f"Successfully loaded page {page_number} with results")
            return True
    
    print(f"Failed to load page {page_number} with results")
    return False

# main code
search_url = "https://www.linkedin.com/search/results/people/?network=%5B%22F%22%2C%22S%22%2C%22O%22%5D&origin=FACETED_SEARCH&page=31&schoolFilter=%5B%223355892%22%5D&sid=MXf"

# get profiles
all_profiles = search_and_extract(search_url, max_pages=100)  # Adjust max_pages as needed

# save results
save_to_csv(all_profiles, "innopolis_search_results_extended_2.csv")

# close browser
driver.quit()