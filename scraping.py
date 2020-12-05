
# Import Splinter & BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path = "chromedriver", headless=True)

    news_title,news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dict
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    #Stop webdriver a d return data
    browser.quit()
    return data

def mars_news(browser):
    #Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent elements to find the first 'a' tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()


        # Use the parent elements to find the paragraph text
        news_p = slide_elem.find("div", class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Featured Images

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'


    return img_url

# Mars Facts
def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns=['description', 'value']
    df.set_index('description', inplace=True)
    return df.to_html(classes = "table table-striped")

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


