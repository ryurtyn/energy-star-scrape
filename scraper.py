import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape(base_url, starting_url, product_name):
    # URL of the website you want to scrape

    # Send an HTTP GET request to the URL
    response = requests.get(starting_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract specific elements or data from the HTML
        # For example, find all <a> tags (links) on the page
        links = soup.find_all('a', class_="pf_PRODUCTION")

        # Print the extracted links
        for link in links:
            reference = link.get("href")
            if ("certified-"+product_name) in reference:
                hit = reference
    else:
        print(f'Failed to retrieve the webpage {starting_url}', starting_url)
        return 
    
    if hit:
        product_page_url = starting_url + hit
        response = requests.get(product_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            products = soup.find_all("div", class_=("row certified-"+product_name))
            products_on_page = []
            for product in products:
                links = product.find_all("a")
                for l in links:
                    link = l.get("href")
                    link = re.sub(r'^(\.\./)+', '', link)
                    if product_name in link and "details" in link and "productfinder" in link: 

                        product_info_url = base_url + link
                        product_dictionary = parse_product_page(base_url, product_info_url)
                        products_on_page.append(product_dictionary)
            return products_on_page

        else:
            print("aww :( )")



def parse_product_page(base_url, url):
    response = requests.get(url)
    product_information = {}
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the div containing the label "Storage Volume (gallons)"
        product_data_table = soup.find_all('div', id="product-data-table")[0]

        # Extract the corresponding value
        if product_data_table:
            title_element = product_data_table.find_all("h1")[0].find_all("div", class_="text")[0]
            product_name = title_element.contents[0].strip()
            if product_name:
                product_information["product name"] = product_name
            property_table = product_data_table.find_all('div', class_='product-property-table')[0]
            if property_table:
                property_sections = property_table.find_all("div", class_="item-list")
                for section in property_sections:
                    section_info_list = section.find_all("li")
                    for s in section_info_list:
                        property_title = s.find_all("div", class_="views-field-title")[0]
                        property_title = ' '.join(property_title.text.replace(':', '').split()).lower()
                        property_value = s.find_all("div", class_="views-field-value")[0]
                        property_value = ' '.join(property_value.text.split())
                        product_information[property_title] = property_value
            
            # print(product_information, '\n')    
            return product_information
        else:
            print("Product Data Table not found on the page")
    else:
        print('Failed to retrieve the webpage', url)


def visualize(data):
    df = pd.DataFrame(data)
    df_no_duplicates = df.drop_duplicates()
    df_no_duplicates.to_csv('output.csv', index=False)
    print(df_no_duplicates)



if __name__ == "__main__":
    url = 'https://www.energystar.gov/productfinder/'
    base_url = 'https://www.energystar.gov'
    water_heaters = scrape(base_url, url, "water-heaters")
    furnaces = scrape(base_url, url, "furnaces")
    print(water_heaters)
    # print(furnaces)
    visualize(water_heaters)