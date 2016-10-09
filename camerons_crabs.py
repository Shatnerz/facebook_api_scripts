"""Quick hack to grab crab prices from Cameron's FB page"""

# This is far from perfect, but good enough to see the larger picture.

import facebook
import pandas as pd
import matplotlib.pyplot as plt
import requests
import re
import iso8601


APP_ID = "REDACTED"
APP_SECRET = "REDACTED"

# TODO
# Write everything to a sqlite db.
# Stop collecting once we hit duplicates.
# Create a pandas datafram.
# Plot the results


def analyze_all_posts():
    """Go through all posts, grab prices, and plot the price of #1 males."""
    graph = facebook.GraphAPI()
    graph.access_token = graph.get_app_access_token(APP_ID, APP_SECRET)

    page_name = 'Cameronsseafoodmarket'

    page = graph.get_object(page_name)

    posts = graph.get_connections(page['id'], 'posts')

    data = {}

    while True:
        try:
            # Perform some action
            data = get_price_data(posts, data)

            # Attempt to get the next page
            posts = requests.get(posts['paging']['next']).json()
        except KeyError:
            break

    # Create DataFrame for #1 Males
    num_one = data['#1 males']
    df = pd.DataFrame(data=num_one, columns=['Product', 'Price', 'Time'])
    df = df.set_index('Time')
    # Plot Price
    df['Price'].plot(kind='line')
    plt.show()

    # return the data
    return data


def get_price_data(posts, price_tables={}):
    """Go through posts and pull out the dates, prices, and product."""
    product_template = re.compile('\#1 males|mixed', re.IGNORECASE)
    price_template = re.compile('\$\d+')

    # price_tables = {}  # dict of {product name: datafram of prices over time}
    # table = pd.DataFrame()

    # Extract Prices
    data = posts['data']
    for post in data:
        time = iso8601.parse_date(post['created_time'])
        text = post['message']
        products = product_template.findall(text)
        prices = [int(i.strip('$')) for i in price_template.findall(text)]
        product_prices = zip(products, prices)
        for product, price in product_prices:
            _record_prices(product, price, time, price_tables)
        # try:
        #     if prices[0] < 50:
        #         print(post)
        # except:
        #     pass
    return price_tables


def _record_prices(product, price, time, tables):
    """Write the data somewhere."""
    # We can later change this to write to sqlite
    # print(product, price, time)
    product = product.lower()
    try:
        data = tables[product]
    except KeyError:
        data = tables.setdefault(product, [])
    data.append((product, price, time))


def main():
    data = analyze_all_posts()


if __name__ == '__main__':
    main()
