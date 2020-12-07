
# Import Splinter & BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dict
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop web driver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Scrape Mars News
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

    df.columns = ['description', 'value']
    df.set_index('description', inplace=True)
    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    url = ("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    links = browser.find_by_css("a.product-item h3")

    for i in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[i].click()
        sample_elem = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']
        hemisphere['title'] = browser.find_by_css("h2.title").text
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # parse html text
    hemi_soup = soup(html_text, "html.parser")

    # adding try/except for error handling
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title_elem = None
        sample_elem = None

    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemispheres
    browser.quit()

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
