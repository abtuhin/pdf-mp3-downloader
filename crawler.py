import requests
from bs4 import BeautifulSoup
import time
import re
import urllib

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')

    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return search_term, response.text

def scrap_website(urls):
    resources = []
    for entry in urls:
        try:
            response = requests.get(entry['url'], headers=USER_AGENT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            results = soup.find_all('a', attrs={'href': re.compile("^(http|https)://")})

            for result in results:
                current_link = result['href']
                if current_link.endswith('.mp3'):
                    resources.append(current_link)
        except:
            print("something wrong")
    return resources

def parse_results(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')

    found_results = []

    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:
        link = result.find('a', attrs={'href': re.compile("^(http|https)://")})
        if link:
            link = link['href']
            if link != '#':
                found_results.append({'url': link})
    resources = scrap_website(found_results)
    return resources

def scrape_google(search_term, number_results, language_code):
    try:
        keyword, html = fetch_results(search_term, number_results, language_code)
        results = parse_results(html, keyword)
        return results
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")

def download(link, filename=""):
    if filename == "":
        filename = link.split("/")[-1]
    try:
        print(filename)
        print("Downloading...")
        urllib.urlretrieve(link, filename)
    except:
        print("404: Couldn't download file")
    print("Done!")


if __name__ == '__main__':
    keywords = ['free mp3 sample']
    data = []
    for keyword in keywords:
        try:
            results = scrape_google(keyword, 6, "en")
            for result in results:
                download(result)
                data.append(result)
        except Exception as e:
            print(e)
        finally:
            time.sleep(10)
    print(data)
