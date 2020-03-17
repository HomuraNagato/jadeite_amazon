
# Jadeite Amazon

Project aims to identify products on amazon that have a high margin of profit for
selling on their site.

## Initialization

Currently deployed locally. Ensure dependant packages are downloaded. Follow comments at top of programs/jadeite_sellers.py
to create a database and table. create a yaml file in same location as user.yaml.example but renamed without the trailing
.example with username and password substituted. Check that postgresql is
started. Start with the command: `sudo service postgresql restart`. Other helpful commands (in place of `restart`)
are: `status` and `stop`. Once the database is running, start the service with: `python main.py`. Copy the running
on http address in a web browser.

## Interaction

Amazon ASIN's (Amazon Standard Identification Number) found for many products sold on amazon.com can be found
in the product information table for the product, an example below

![ASIN for Sony WH1000XM3 headphones](data/images/amazon_site_product_asin_location.png?raw=True "find asin on product page")

Once this is found, seller information can be gathered and put in the database, formated, and displayed as a
table. Additionally one remove by asin, filter for a specific asin, or clear to display the entire database.


![What the page looks like](data/images/amazon_site_page.png?raw=True "What the page looks like")

Product Calculator

A prototype web-based calculator for quickly inputting various product values to identify relative value.

## Behind the curtain's

Main.py
`main.py` establishes the various components for the project. It uses flask to establish a local website. It
also creates plotly objects, such as tables or plots. Data for the plotly objects are loaded from an Amazon
class initialized in the program jadeite_sellers.py.

jadeite_sellers.py
Using beautiful soup, it takes an asin to generate a full http request to amazon. Once it establishes a connection,
it gathers information on the buybox, and information on the seller's page, such as the sellers offer price,
their name, and product. It formats this information into a memory-only csv file, then it reads this data into
a pandas dataframe. After this the dataframe is written to the postgresql database. This program also performs
other database related tasks, such as deleting asin's from it and viewing from it.

index.html
The html page used to format the website. There are javascript ajax calls on this page for creating the connection
between clicking on a button on the site that triggers main.py to perform an action. It also jquery for the
responsive calculator on the site.

gran_command.py
A template program that uses data on world development indicators from the worldbank to format a pandas dataframe
that is used for creating a table and an interactive graph that has dropdowns to change viewed axes.

## Current focus and future directions

When additional historical data is available, an interactive graph will be generated. Time series analysis
will be performed to identify critical points, such as an expected best time to sell, or categories that
are trending popular and should sell fast.