"""
Scrape the top 100 best sells from amazon.

Notes
price, number of sellers, and whether amazon in list
"""
import urllib
import urllib3                  # open webpage as an object
import certifi                  # certificate to verify HTTPS requests
from bs4 import BeautifulSoup   # create soup from webpage-object
import os
import re
import numpy as np
import pandas as pd

from io import StringIO
from csv import writer

def choose_source():

    # electronics
    electronics = { 
                    'url1': 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'electronics',
                  }
    # camera and photo
    camera_photo = { 
                    'url1': 'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'camera_photo',
                  }
    # video games
    video_games  = { 
                    'url1': 'https://www.amazon.com/best-sellers-video-games/zgbs/videogames/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/best-sellers-video-games/zgbs/videogames/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'video_games',
                  }

    # arts, crafts, and sewing
    arts_crafts  = { 
                    'url1': 'https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'arts_crafts',
                  }
    # books
    books  = { 
                    'url1': 'https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'books',
                  }
    # beauty and personal care
    beauty_care  = { 
                    'url1': 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
                    'url2': 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
                    'category': 'beauty_care',
                  }
    
    
    sources = [electronics, camera_photo, video_games, arts_crafts, books, beauty_care]

    print("which best seller list would you like to choose from?\n")
    [ print('\t', i+1, x['category']) for i, x in enumerate(sources) ]
    selection = input('\n')
    if selection.isdigit() == True and int(selection) <= len(sources):
        source = sources[int(selection)-1]
    else:
        print("selected value outside the source range, please try again")
        return choose_source()
    #print("returning", source)
    return source
    
def soup_request(url):

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    return soup

def amazon_best_seller_request(category_dict, page):

    soup = soup_request(page)
    data = soup.find_all('li', class_='zg-item-immersion')

    # reference for more efficient in memory writer to append rows and at the end convert to dataframe
    # https://stackoverflow.com/questions/41888080/python-efficient-way-to-add-rows-to-dataframe
    output = StringIO()
    csv_writer = writer(output)

    csv_writer.writerow(['rank', 'price', 'name', 'href'])

    for item in data:
        
        #print(" *** data ***\n", item)

        # in case of any possible missing data, encapsulate each query in a try statement
        # perhaps find a more concise way
        try:
            rank = item.find_all('span', class_='zg-badge-text')[0].get_text().replace("#", "")
        except:
            rank = "unknown"
        try:
            name = item.find_all('div', class_='p13n-sc-truncate')[0].get_text().strip()
        except:
            name = "unknown"
        try:
            href = item.find_all('a', class_='a-link-normal')[0]['href']
        except:
            href = "unknown"
        try:
            price = item.find_all('span', class_='p13n-sc-price')[0].get_text()
        except:
            price = "unknown"
            
        #print("\n *** rank, price, name, href:", rank, price, name, href, "***\n")
        csv_writer.writerow([rank, price, name, href])

    output.seek(0) # need to get back to the start of the BytesIO
    df = pd.read_csv(output)

    return df
        


if __name__ == "__main__":

    chosen_source = choose_source()

    top50 = amazon_best_seller_request(chosen_source, chosen_source['url1'])
    bottom50 = amazon_best_seller_request(chosen_source, chosen_source['url2'])

    top100 = pd.concat([top50, bottom50], axis=0, ignore_index=True)
    print("amazon", chosen_source['category'], "best sellers\n", top100.head(), "\n", top100.tail())
