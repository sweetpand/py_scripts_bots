from selenium import webdriver
from selenuim.webdriver.common.by import By
from selenuim.webdriver.support.ui import WebDriverWait
from selenuim.webdriver.support import expected_conditions as expect
from selenuim.webdriver.common.keys import Keys 
import time 
from random import randint

def delay(n):
	time.sleep(randint(2, n))


driver = webdriver.Chrome()
driver.get("https://www.youtube.com")
print("enter" + driver.title)
delay(5)

item = driver.find_element_by_css_selector("ytd-masthead div#buttons ytd-button-renderer a")
item.click()
delay(5)

driver.find_element_by_id("identifierId").send_keys("xxx@gmail.com")
driver.find_element_by_id("identifierNext").click()
delay(5)

password_locator = (By.CSS_SELECTOR,'div#password input[name="password"]')
WebDriverWait(driver, 10).until(
	expect.presence_of_element_located(password_locator)
)
password = driver.find_element(*password_locator)
WebDriverWait(driver, 10).until(
    expect.element_to_be_clickable(password_locator)
)
password.send_keys("password")
driver.find_element_by_id("passwordNext").click()
delay(5)

print("wait for login ...")
WebDriverWait(driver, 300).until(
    expect.presence_of_element_located((By.CSS_SELECTOR, "ytd-masthead button#avatar-btn"))
)
print("login ok")

search = driver.find_element_by_css_selector("ytd-masthead form#search-form input#search")
search.click()
search.send_keys("hago")
search.submit()
delay(5)

item = driver.find_element_by_css_selector("ytd-search a#video-title")
item.click()
delay(5)

# scroll to the bottom in order to load the comments
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

print("wait for comments to load ...")
WebDriverWait(driver, 10).until(
    expect.presence_of_element_located((By.CSS_SELECTOR, "ytd-comments ytd-comment-simplebox-renderer"))
)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
item = driver.find_element_by_css_selector("ytd-comments ytd-comment-simplebox-renderer div#placeholder-area")
item.click()
item = driver.find_element_by_css_selector(("ytd-comments ytd-comment-simplebox-renderer " 
                                            "iron-autogrow-textarea #textarea"))
item.click()
item.send_keys("I like it!\n")
item.send_keys("This is the most amazing things ever seen.\n")
item.send_keys("Wanna see more~\n")
item.send_keys(Keys.CONTROL, Keys.ENTER)