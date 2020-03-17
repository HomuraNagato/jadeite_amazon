"""
Given an ASIN, get seller information

Notes
price, number of sellers, and whether amazon in list
"""

"""
front page
https://www.amazon.com/Fujifilm-INSTAX-Instant-Sheets-Cameras/dp/B06W5JYQX1/ref=zg_bs_electronics_27?_encoding=UTF8&psc=1&refRID=3D0Y6VEQEFHGYQEQ9DWG
https://www.amazon.com/WH-1000XM3-Wireless-canceling-Headset-International/dp/B07H2DBFQZ/ref=sr_1_1?keywords=B07H2DBFQZ&qid=1564946296&s=electronics&sr=1-1

seller page
https://www.amazon.com/gp/offer-listing/B06W5JYQX1/ref=olp_f_primeEligible?ie=UTF8&f_new=true&f_primeEligible=true
https://www.amazon.com/gp/offer-listing/B07H2DBFQZ/ref=olp_f_new?ie=UTF8&f_primeEligible=true&f_new=true
https://www.amazon.com/gp/offer-listing/B00008XEWG/ref=olp_f_new?ie=UTF8&f_primeEligible=true&f_new=true
"""

"""
list of asins
B06W5JYQX1
B07H2DBFQZ
B00008XEWG
"""

"""
Settings for connecting to postgres
helpful links
https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
https://stackoverflow.com/questions/31645550/why-psql-cant-connect-to-server

follow along from this site to create a user if desired, afterwards, edit user.yaml
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04

creating postgresql database from bash (for postgres user after setting up user and password)
    sudo -u postgres createdb pensieve

open postgresql interface to database
    psql -d pensieve

creating table in database for connection (within psql)
    CREATE TABLE amazon_sellers (index serial PRIMARY KEY, seller_price text, company_name text, title text, asin text, product_price text, date date);

starting postgresql service once user, database, and table have been created
    sudo service postgresql status/start/restart/stop
"""

from bs4 import BeautifulSoup   # create soup from webpage-object
import os
import re
import datetime
import argparse
import numpy as np
import pandas as pd
#import psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session

from io import StringIO
from csv import writer

import yaml # conda install pyyaml
from .jadeite_soup import *

from sqlalchemy import create_engine

with open("user.yaml", 'r') as stream:
    credentials = yaml.safe_load(stream)

postgresql_login = 'postgresql://' + credentials['postgresql']['username'] + ':' + credentials['postgresql']['password'] + '@' + str(credentials['postgresql']['host']) + ':' + str(credentials['postgresql']['port']) + '/' + credentials['postgresql']['db']
print("engine parameters", postgresql_login)
# should be of format
# postgresql://{user}:{password}@{host}:{port}/{db}
engine = create_engine(postgresql_login, echo=False)
conn = engine.connect()

# for parsing known argument without consuming it in parse_args()
class UserNamespace(object):
    pass
user_namespace = UserNamespace()

    
def parse_arguments():
    
    parser = argparse.ArgumentParser(description='''Use an amazon asin input via command line or user selection to get product price and seller information''')
    parser.add_argument('--asin', nargs='?', type=str, default=None, help='Amazon Product ID')

    args = vars(parser.parse_args())
    return args


class Amazon:
    
    def __init__(self, asin=None, action=None):
        
        self.href = ''
        self.title = ''
        self.product_price = None
        self.seller_df = pd.DataFrame()
        self.outer_df = pd.DataFrame()
        self.action= action
        
        if asin == None and action != "clear":
            self.asin = self.choose_asin()
        else:
            self.asin = asin

    def view_outer_df(self):
        return self.outer_df
            
    def choose_asin(self):

        selection = input("please type in the asin of a product\nExamples:\nB06W5JYQX1\nB07H2DBFQZ\nB00008XEWG\n\nASIN: ")

        return selection

    def amazon_asin_request(self):
        '''
        Given an ASIN, get the link to its product page
        '''
        url = 'https://www.amazon.com/s?k=' + self.asin
        print("acquiring link to product page. url:", url)
        soup = soup_request(url)
        product_link = soup.select("a.a-link-normal.a-text-normal")[0]
        href, title = re.search('(.+)ref\=', product_link['href']).group(1), product_link.text.strip()
        self.href = href
        self.title = title
        #print("asin information\ntitle:", self.title, "\nhref:", self.href)

    def amazon_product_request(self):
        '''
        Given a product page, get product information
        '''
        print("acquiring product page information")
        url = 'https://www.amazon.com' + self.href
        soup = soup_request(url)
        try:
            product_price = soup.find('span', id='price_inside_buybox').text.strip()
        except:
            #print(soup.find_all('span'))
            #print("soup\n", soup)
            product_price = 0
        #print("product price:", product_price)
        self.product_price = product_price

    def amazon_seller_request(self):
        '''
        Given an ASIN, get seller information
        '''
        print("acquiring seller page information")
        url = 'https://www.amazon.com/gp/offer-listing/' + self.asin + '/ref=olp_f_new?ie=UTF8&f_primeEligible=true&f_new=true'
        soup = soup_request(url)
        sellers = soup.find_all('div', class_='olpOffer')

        output = StringIO()
        csv_writer = writer(output)
        csv_writer.writerow(['seller_price', 'company_name'])

        for seller in sellers:
            price = seller.find('span', class_='olpOfferPrice').text.strip()
            #tax = seller.find('span', class_='olpEstimatedTaxText')
            try:
                company = seller.find('h3', class_='olpSellerName').find('a').text
            except:
                company = seller.find('h3', class_='olpSellerName').find('img')['alt']
                #print("check name:", name)
            #print(price, company)
            csv_writer.writerow([price, company])

        output.seek(0) # need to get back to the start of the BytesIO
        df = pd.read_csv(output)
        #print(" *** seller information *** ")
        #print(df.head())
        self.seller_df = df.copy()

        #print(" *** data ***")
        #file_ = open("soup.txt", "w")
        #file_.write(str(soup))
        #file_.close()

    def create_dataframe(self):
        ''' title, product_asin, price, seller_info'''
        #static_df = pd.DataFrame( { 'title': self.title, 'asin': self.asin, 'product_price': self.product_price } )
        static_df = pd.DataFrame([[self.title, self.asin, self.product_price]], columns=['title', 'asin', 'product_price'])
        outer_df = self.seller_df.copy()
        outer_df['title'] = self.title
        outer_df['asin'] = self.asin
        outer_df['product_price'] = self.product_price
        outer_df['date'] = datetime.datetime.today()

        self.outer_df = outer_df
        
        print("outer df\n", self.outer_df)

    def insert_sql(self):
        
        self.delete_sql()
        self.outer_df.to_sql('amazon_sellers', con=engine, if_exists='append')
        
    def delete_sql(self):
        
        try:
            conn.execute('DELETE FROM amazon_sellers WHERE asin = \'' + self.asin + '\';')
        except:
            print("unable to delete", self.asin, "from postgres database")

    def view_database(self):

        df = pd.read_sql_query('SELECT * FROM "amazon_sellers"', con=engine)
        return df
    

def asin_request(artifact):

    #artifact = Amazon(asin)

    # get link to product page
    artifact.amazon_asin_request()
    
    # get product price
    artifact.amazon_product_request()
    
    # get seller information for given asin
    artifact.amazon_seller_request()

    # combine information into dataframe
    artifact.create_dataframe()
    try:
        artifact.insert_sql()
    except:
        print("asin_request stage, trouble with inserting into postgres database")


if __name__ == "__main__":

    args = parse_arguments()
    # create Amazon object
    artifact = Amazon(args['asin'])
    
    # add
    #asin_request(artifact)

    # view
    df = artifact.view_database()
    print(df.head())

    # delete
    #artifact.delete_sql()
