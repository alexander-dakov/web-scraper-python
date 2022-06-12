from bs4 import BeautifulSoup
import requests
import pandas as pd

# Create the dataframe from which to export a csv file.
result = pd.DataFrame()

# Create repositories for all of the needed data for each book. Every book will have them, so there is no need to null-ify them every time.
book_titles = ''
book_upcs = ''
book_types = ''
book_prices = ''
book_availability = ''
book_reviews = ''
book_description = ''

# Now its time to visit the site successfully ...
url = "http://books.toscrape.com"
html_text = requests.get(url).text

base_page = BeautifulSoup(html_text, 'lxml')

# ... find how many pages does the script have to crawl through ...
pages = base_page.find("li", class_="current").text.split()
current_page = int(pages[1])
last_page = int(pages[-1])

while current_page <= last_page:

    catalogue_url = url + '/' + (str(base_page.find("li", class_="next")).split('"')[-2])[:-6:] + str(current_page) + '.html'
    catalogue_page = BeautifulSoup(requests.get(catalogue_url).text, 'lxml')

    # ... and search through the structure of the page for every book.
    books = catalogue_page.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for book in books:
        # After finding the books, lets look up for the URL of each of them and visit their pages, as the needed data can be found only there.
        book_url = url + '/catalogue/' + ((str(book.find("a")).split())[1].replace('href="', '')).replace('"><img', '')
        book_page = BeautifulSoup(requests.get(book_url).text, 'lxml')

        # Lets extract the data from the page.
        book_titles = book_page.find("h1").text

        data = ((str(book_page.find_all('td'))[1:-1:].replace('<td>', '')).replace('</td>', '')).split(', ')

        # Take only what is needed from the table.
        book_upcs = data[0]
        book_types = data[1]
        book_prices = data[3]
        book_availability = data[5]
        book_reviews = data[6]

        # Take the description from the <head>, because of the indentation, otherwise it could be taken from the <body> as well.
        book_description = ((str(book_page.find_all("meta")[2]).replace('', '')).replace('<meta content="\n', '')).replace('\n" name="description"/>', '')

        # For each book the attributes are added to the existing dataframe.
        df = pd.DataFrame([book_titles, book_upcs, book_types, book_prices, book_availability, book_reviews, book_description]).transpose()
        result = result.append(df)

    current_page += 1

# After collecting the data needed, its time to write it to a file. Lets also put names for the columns.
result.columns = ['Title', 'UPC', 'Type', 'Price (tax included)', 'Availability', 'Reviews', 'Description']
result.to_csv('results.csv')
