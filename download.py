import os
import yaml
import argparse
import requests
import collections
import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm


class Scraper:

    def __init__(self, output_dir, url='https://research.ast.cam.ac.uk/lensedquasars/index.html'):
        self.output_dir = output_dir
        self.url = url

        self.df_main = self._scrape_df_main()
        self.df_url = self._scrape_df_url(survey='HST')

    def _scrape_df_main(self):

        # Fetch the HTML content of the website
        response = requests.get(self.url)
        html_content = response.text

        # Use BeautifulSoup to extract the table data
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        table_body = table.find('tbody')

        # Extract the column names from the table header
        headers = table.find_all('th')
        column_names = [header.text.strip() for header in headers]

        # Use BeautifulSoup to extract the table data
        rows = table_body.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            row_data = []
            for col in cols:
                element = col.text.strip()  # get text value
                for tag in col.find_all('a'):
                    href = tag.get('href')  # get href url
                    element = (element, href) # (text, url) as a tuple
                row_data.append(element)
            data.append(row_data)

        # Create a Pandas dataframe from the table data
        df_main = pd.DataFrame(data, columns=column_names)
        df_main.to_csv(os.path.join(self.output_dir, "df_main.csv"), index=False)
        return df_main


    def _scrape_df_url(self, survey='HST'):

        df_url = collections.defaultdict(list)

        for name, url in tqdm(self.df_main["Name"], desc="Scraping Quasars"):

            # Send an HTTP GET request to the URL and get the HTML content
            response = requests.get(url)
            html_content = response.content

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all <a> tags on the page
            links = soup.find_all('a')

            # Extract the href links that contain 'HST'
            for link in links:
                href = link.get('href')
                if href and survey in href:
                    df_url["name"].append(name)
                    df_url["url"].append(href)
                    df_url["download"].append(self._download_img(href))

        df_url = pd.DataFrame(df_url)
        df_url.to_csv(os.path.join(self.output_dir, "df_url.csv"), index=False)
        return df_url

    def _download_img(self, url):

        # Send an HTTP GET request to the URL and get the file content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Write the file content to a local file
            fpath = os.path.join(self.output_dir, "downloads", url.split("/")[-1].replace("*", ""))
            with open(fpath, 'wb') as file:
                file.write(response.content)
            return True  # record if successfully downloaded
        else:
            return False  # record if fail to download




if __name__ == "__main__":

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', required=True, type=str, help="xxx.yaml")
    args = parser.parse_args()

    # Load config
    with open(args.config_file) as file:
        config = yaml.safe_load(file)

    # Execute the scraper
    scraper = Scraper(config["output_dir"])
    print("Done :)")
