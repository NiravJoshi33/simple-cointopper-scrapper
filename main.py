import json
import requests
from bs4 import BeautifulSoup

offset_value = 9

def get_html_content(url: str) -> str:
    response = requests.get(url)
    decoded_content = response.content.decode("utf-8")
    return decoded_content

def get_urls(html_content: str) -> list:
    all_url_list = list()
    soup = BeautifulSoup(html_content, "html.parser")
    all_url_content = soup.find_all('div', {'class': 'col-xs-12 col-sm-6 col-md-4'})
    for element in all_url_content:
        links_content = element.find_all("a")
        for link in links_content:
            article_url = link["href"]
            all_url_list.append(article_url)
    return all_url_list

# get all article urls from cointopper
ct_main_url = "https://cointopper.com/news"
mainpage_decoded_content = get_html_content(ct_main_url)
main_page_url_list = get_urls(mainpage_decoded_content)

is_data_available = True
next_page_url_list = list()
while is_data_available:
    request_url = f"https://cointopper.com/ajax/news?offset={offset_value}"
    print(f"Requesting content from: {request_url}")
    nextpage_decoded_content = get_html_content(request_url)
    json_data = json.loads(nextpage_decoded_content)
    data = json_data.get("data")
    if data:
        url_list = get_urls(data)
        offset_value += 9
        next_page_url_list.extend(url_list)
    else:
        print("data no longer availabe")
        is_data_available = False

all_url_list = main_page_url_list + next_page_url_list

def get_article_data(article_url: str) -> dict:
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, "html.parser")
# getting title and image url
    elements = soup.find_all("div", class_ = "post-image")
    for element in elements:
        data = element.find_all("img")
        for d in data:
            title = d["title"]
            image_link = d["src"]
    # getting date
        date_data = element.find("a")
        for d in date_data:
            date = d.get_text()
            print(f"date: {date}")
            if date:
                break
        if date is not None and title is not None and image_link is not None:
            break
# getting the content
    twitter_content = list()
    elementsTobeRemoved = soup.find_all("div", dir = "ltr")
    for element in elementsTobeRemoved:
        data = element.find_all("blockquote", class_ = "twitter-tweet")
        for d in data:
            d.decompose()
    elements = soup.find_all("div", dir = "ltr")
    content = ""
    for element in elements:
        content_data = element.find_all("p")
        for d in content_data:
            para = d.get_text()
            content += "\n" + para
    
    print(f"title: {title}")
    article_data = {
        "title": title,
        "article_url": article_url,
        "publish_date": date,
        "content": content,
        "image_url": image_link,
        "source_name": "CoinTopper"
    }

    return article_data

all_article_data = list()
for article_url in all_url_list:
    try:
        article_data = get_article_data(article_url)
    except Exception as err:
        print(f"couldn't retrieve data from: {article_url} with error: {err}")
    with open("content.json", "r") as datafile:
        old_data = json.load(datafile)
    old_data.append(article_data)
    with open("content.json", "w") as datafile:
        json.dump(old_data, datafile, indent=2)
    all_article_data.append(article_data)

with open("article_data.json", "w") as datafile:
    json.dump(all_article_data, datafile, indent=2)
