import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



video_to_scrape = "URL" # Provide YT Video URL

driver = webdriver.Chrome("PATH") # Provide path to chrome driver
driver.get(video_to_scrape)

SCROLL_PAUSE_TIME = 2 # I'll use this variable for code sleeping time
delay = 30 # delay time for WebDriver (in seconds)
scrolling = True # boolean value -> TRUE means that we're still scrolling, FALSE means we're not scrolling anymore
last_height = driver.execute_script("return document.documentElement.scrollHeight") # this is our last/current position on the page
all_comments_list = [] # we'll store all scraped comments in this list
scrolling_attempt = 5 # we'll have 5 attempts before turning scrolling boolean to False


def scrape_loaded_comments():
    loaded_comments = []
    # Locate all Usernames and Comments
    all_usernames = WebDriverWait(driver, delay).until(
        EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="style-scope ytd-comment-renderer"]')))
    all_comments = WebDriverWait(driver, delay).until(
        EC.presence_of_all_elements_located((By.XPATH, '//yt-formatted-string[@id="content-text"]')))

    try:
        # we'll try to get only last 20 elements, because youtube loads 20 comments per scroll
        all_comments = all_comments[-20:]
        all_usernames = all_usernames[-20:]
    except:
        print("could not get last 20 elements")

    # we'll loop parallel through all usernames and comments
    for (username, comment) in zip(all_usernames, all_comments):
        current_comment = {"username": username.text,
                            "comment": comment.text}
        print(f"Username : {username.text}\nComment : {comment.text}")
        loaded_comments.append(current_comment)  # here we'll store comments

    return loaded_comments


while scrolling == True:
    htmlelement = driver.find_element_by_tag_name("body")  # locate html tag
    htmlelement.send_keys(Keys.END) # scroll to the bottom of html tag
    try:
        last_20_comments = scrape_loaded_comments() # calling function to scrape last 20 comments
        all_comments_list.append(last_20_comments) # appending last 20 comments to the list

    except:
        print("error while trying to load comments")

    new_height = driver.execute_script("return document.documentElement.scrollHeight") # calculate current position
    time.sleep(SCROLL_PAUSE_TIME) # make pause because scrolling will take 0.5/1 seconds
    driver.implicitly_wait(30)  # make longer pause if loading new comments takes longer

    if new_height == last_height: # if current position  is the same as last position, it means we've reached bottom of the page, so we'll break the loop
        scrolling_attempt -= 1
        print(f"scrolling attempt {scrolling_attempt}")
        if(scrolling_attempt == 0):
            scrolling = False # this will break while loop
    last_height = new_height # if current position is not the same as last one, we'll set last position as new height



df = pd.DataFrame(all_comments_list) # create dataframe from our list
df.drop_duplicates(inplace=True) # drop all duplicates
