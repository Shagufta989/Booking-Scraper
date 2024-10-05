from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from lxml import etree
import pyperclip
import pandas as pd
import time
import random

columns = [
    "Business_Type",
    "Business_Name",
    "Business_SubType",
    "Business_FullAddressAndPostCode",
    "Business_Booking.com_URL",
    "Business_Hotel_Star",
    "Business_Source",
    "Business_SourceSearch",
    "Booking.com_DoWePriceMatch",
    "Booking.com_Review_NumberOfReviews",
    "Booking.com_Review_Score",
    "Booking.com_Review_SummaryText",
    "Booking.com_Best_Rating_Name",
    "Booking.com_Best_Rating_Score"
]
BNB_Keywords = [
    "B&B",
    "Bed & Breakfast",
    "Inn",
    "Guest House",
    "Lodge",
    "Cottage",
    "Homestay",
    "Pension",
    "Farmhouse",
    "Retreat",
    "Manor",
    "Villa",
    "Country House",
    "Residence",
    "Cabin",
    "Chalet",
    "Estate",
    "House",
    "Barn",
    "Studio"
]
Hotel_Keywords = [
    "Hotel",
    "Motel",
    "Resort",
    "Suites",
    "Inn",
    "Lodge",
    "Hostel",
    "Boutique Hotel",
    "Luxury Hotel",
    "Business Hotel",
    "Conference Hotel",
    "Spa",
    "Retreat",
    "Guesthouse",
    "Stay",
    "Palace",
    "House",
    "Manor",
    "Residence",
    "Accommodation"
]
Apartment_Keywords = [
    "Apartment",
    "Apartments",
    "Flat",
    "Flats"
    "Studio",
    "Studios",
    "Suite",
    "Suites",
    "Residence",
    "Loft",
    "Lofts",
    "Condos",
    "Condominium",
    "Condo",
    "Apart-Hotel",
    "Apartel",
    "Holiday Apartment",
    "Vacation Apartment",
    "Serviced Apartment",
    "Aparthotel"
]
data_for_each_link = {
    "Business_Type": "Hotel",
    "Business_Name": "",
    "Business_SubType": "",
    "Business_FullAddressAndPostCode": "",
    "Business_Booking.com_URL": "",
    "Business_Hotel_Star": "",
    "Business_Source": "Booking.com",
    "Business_SourceSearch": "",
    "Booking.com_DoWePriceMatch": "",
    "Booking.com_Review_NumberOfReviews": "",
    "Booking.com_Review_Score": "",
    "Booking.com_Review_SummaryText": "",
    "Booking.com_Best_Rating_Name": "",
    "Booking.com_Best_Rating_Score": ""
}
all_content_loaded = False
close_button_css = '[aria-label="Dismiss sign in information."]'
current_url = ""

def initialize_options(options):
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")


opts = Options()
initialize_options(opts)

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=opts)


def random_wait(min_secs=2, max_secs=5):
    time.sleep(random.uniform(min_secs, max_secs))


def manual_stealth(drv):
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined})"
    })
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters)
            );
        """
    })
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});"
    })
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});"
    })


def ask_user(to_ask, digital=False, special_term=0):
    user_response = False
    while not user_response:
        time.sleep(1)
        if digital:
            try:
                user_response = int(input(to_ask))
                if user_response > special_term or user_response < 0:
                    user_response = False
                    raise ValueError
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        else:
            user_response = input(f"{to_ask}")
    return user_response


def switch_url(town_name):
    global current_url
    source_search = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Where are you going?"]')
    for i in range(8):
        source_search.send_keys(Keys.BACKSPACE)
    source_search.send_keys(f"{town_name}")
    time.sleep(1.5)
    source_search.send_keys(Keys.ENTER)
    current_url = driver.current_url
    driver.get(current_url)


def click_buttons(elem):
    is_it_true = False
    try_again = 0
    while not is_it_true:
        try:
            if try_again < 3:
                element = WebDriverWait(driver, 5).until(ec.presence_of_element_located(elem))
                element.click()
                is_it_true = True
                try_again = 0
            else:
                is_it_true = True
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
            try_again += 1
    return is_it_true


manual_stealth(driver)
town_name = ask_user("Enter the town name:")
town = "_".join(town_name.split(" "))
driver.get("https://www.booking.com/searchresults.en-gb.html?ss=Bicester&ssne=Alcabideche&ssne_untouched=Alcabideche&highlighted_hotels=331206&label=gen173nr-1FCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQH4AQyIAgGoAgO4Arqc1bQGwAIB0gIkMWJkMGFiNWQtY2VjNi00ZjFjLTkyZjItZTY0YjM0NzhiMTdj2AIG4AIB&sid=511f17f4f353f725ae8c200277e15e7e&aid=304142&lang=en-gb&sb=1&src_elem=sb&src=searchresults&dest_id=-2589863&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=936f44c58e800870&ac_meta=GhBiZDkzNDRjYTU5ODEwMDMxIAAoATICZW46BUJpY2VzQABKAFAA&checkin=2024-10-15&checkout=2024-10-16&group_adults=1&no_rooms=1&group_children=0&selected_currency=GBP")
click_buttons((By.CSS_SELECTOR, close_button_css))
switch_url(town_name)

click_buttons((By.XPATH, "//span[contains(text(), 'See all')]"))


def find_business_type(title):
    for w in BNB_Keywords:
        if w in title:
            return "B&B"
    for w in Hotel_Keywords:
        if w in title:
            return "Hotel"
    for w in Apartment_Keywords:
        if w in title:
            return "Apartment"
    return random.choice(["B&B", "Hotel", "Apartment"])


def extract_two_common_fields(title_text):
    # TODO: Business Type
    data_for_each_link["Business_SubType"] = find_business_type(title_text)

    # TODO: Business Name
    data_for_each_link["Business_Name"] = title_text


def extract_star_ratings(business):
    # TODO: Rating Stars
    rating_stars_container = business.find("div", {"data-testid": "rating-stars"})
    rating_squares_container = business.find("div", {"data-testid": "rating-squares"})
    if rating_stars_container:
        rating_stars = len(rating_stars_container.find_all("svg"))
    elif rating_squares_container:
        rating_stars = len(rating_squares_container.find_all("svg"))
    else:
        rating_stars = 0
    data_for_each_link["Business_Hotel_Star"] = str(rating_stars)


def extract_complete_address():
    # TODO: Complete Address
    address = WebDriverWait(driver, 60).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, "span.hp_address_subtitle")))
    return address.text


def extract_do_we_price_match():
    try:
        we_match = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//span[contains(normalize-space(.), 'We Price Match')]")))
        we_match = we_match.text
    except exceptions.TimeoutException:
        we_match = "No price match"
    return we_match


def extract_reviews_info():
    try:
        overall_reviews_container = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-capla-component-boundary="b-property-web-property-page/PropertyReviewScoreRight"]')))
        container_text = overall_reviews_container.text.split("\n")
        overall_score = [e for e in container_text if "Scored" in e][0].replace("Scored", "").strip()
        overall_rating = [e for e in container_text if "Rated" in e][0].replace("Rated", "").strip().capitalize()
        overall_reviews = [e for e in container_text if "reviews" in e][0].replace("reviews", "").strip()
    except exceptions.TimeoutException:
        overall_score = ""
        overall_rating = ""
        overall_reviews = ""
    return (
        overall_score,
        overall_rating,
        overall_reviews
    )


def extract_best_review():
    try:
        reviews_button = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH,
                                              "//span[contains(normalize-space(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')), 'read all reviews')]")))
        reviews_button.click()
        reviewer = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '[aria-label="Reviewer"]')))
        reviewer_first_text = reviewer.text.split("\n")[0]
        reviewer_second_text = reviewer.text.split("\n")[1]
        reviewer_text = reviewer_first_text if len(reviewer_first_text) > 2 or "Room" in reviewer_second_text else reviewer_second_text
        reviewer_score = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="review-score"]')))
        reviewer_score_text = reviewer_score.text.split("\n")[-1]
    except exceptions.TimeoutException:
        reviewer_text = ""
        reviewer_score_text = ""
    return (
        reviewer_text,
        reviewer_score_text
    )


def extract_share_link():
    share_link = ""
    while True:
        try:
            share = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="property-share-button"] span')))
            share.click()
            share_l = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Copy property link to clipboard"]')))
            share_l.click()
            share_link = pyperclip.paste()
            break
        except (exceptions.StaleElementReferenceException, exceptions.ElementClickInterceptedException,
                exceptions.ElementNotInteractableException):
            continue
        except (exceptions.TimeoutException, exceptions.NoSuchElementException):
            break
    return share_link


def extract_new_window_data(title_text):
    # TODO: Business Complete Address
    elem = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, f'//div[@data-testid="title" and contains(text(), "{title_text.strip()}")]')))
    elem.click()
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data_for_each_link["Business_FullAddressAndPostCode"] = extract_complete_address()
    data_for_each_link["Booking.com_DoWePriceMatch"] = extract_do_we_price_match()
    reviews_data = extract_reviews_info()
    data_for_each_link["Booking.com_Review_Score"] = reviews_data[0]
    data_for_each_link["Booking.com_Review_SummaryText"] = reviews_data[1]
    data_for_each_link["Booking.com_Review_NumberOfReviews"] = reviews_data[2]
    data_for_each_link["Business_Booking.com_URL"] = extract_share_link()
    best_review_data = extract_best_review()
    data_for_each_link["Booking.com_Best_Rating_Name"] = best_review_data[0]
    data_for_each_link["Booking.com_Best_Rating_Score"] = best_review_data[1]
    driver.close()
    if len(driver.window_handles) > 0:
        driver.switch_to.window(driver.window_handles[0])


def save_data_as_csv(data):
    dataframe = pd.DataFrame(data, columns=columns)
    dataframe.to_csv(f'Data_{town_name}.csv', index=False, mode="a", header=False)


def manage_data(business):
    title = business.find("h3")
    title_text = title.text.replace("Opens in new window", "")
    extract_two_common_fields(title_text)
    extract_star_ratings(business)
    extract_new_window_data(title_text)
    save_data_as_csv([data_for_each_link])
    for i, key in enumerate(data_for_each_link):
        if i != 0 and key != "Business_Source" and key != "Business_SourceSearch":
            data_for_each_link[key] = ""


def load_more():
    global all_content_loaded
    while not all_content_loaded:
        try:
            driver.execute_script("""
                var elements = document.querySelectorAll('[data-testid="sticky-container-inner"]');
                elements.forEach(function(element) {
                    element.remove();
                });
            """)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            more = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, "//span[contains(normalize-space(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')), 'Load more results')]")))
            more.click()
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
            all_content_loaded = True
        except exceptions.ElementClickInterceptedException:
            continue


def find_data():
    global all_content_loaded, close_button_css
    try:
        driver.find_element(By.CSS_SELECTOR, "button.map_full_overlay__close").click()
    except (exceptions.TimeoutException, exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException):
        pass

    try:
        driver.find_element(By.CSS_SELECTOR, close_button_css).click()
    except (exceptions.TimeoutException, exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException):
        pass

    load_more()

    # TODO: Initialize BS4
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # TODO: Business Source Search
    source_search = soup.find("input", attrs={"placeholder": "Where are you going?"})
    data_for_each_link["Business_SourceSearch"] = source_search.get("value")

    # TODO: Total Properties Count
    h1 = soup.find("h1", attrs={"aria-live": "assertive"})
    if h1:
        total_properties = int(''.join([letter for letter in h1.text if letter.isdigit()]))
    else:
        print("Total Properteies wasn't estimated")
        total_properties = 0

    driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
    # TODO: Collect On Screen Business List
    WebDriverWait(driver, 60).until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid=property-card]")))
    properties = soup.find_all(attrs={"data-testid": "property-card"})
    properties_length = len(properties)
    if properties_length < 1000:
        while properties_length < total_properties:
            driver.get(current_url)
            all_content_loaded = False
            find_data()
    # TODO: Manage Data
    for business in properties:
        try_again_count = 0
        try:
            manage_data(business)
        except (exceptions.TimeoutException, exceptions.NoSuchElementException):
            if try_again_count < 2:
                if len(driver.window_handles) > 0:
                    driver.switch_to.window(driver.window_handles[0])
                try_again_count += 1
                manage_data(business)
            else:
                continue
    print("ALL DATA HAS BEEN SCRAPED.")
    driver.close()
    driver.quit()


if click_buttons((By.CSS_SELECTOR, close_button_css)):
    df = pd.DataFrame(columns=columns)
    df.to_csv(f'Data_{town_name}.csv', index=False)
    find_data()
