import time
import re
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class MyLikes:
    def __init__(self, url, driver_path, records_path) -> None:
        self.url = url
        self.URLS = list()
        self.profile_urls = list()
        self.records = list()
        self.picture_count = 0
        self.records_path = records_path
        self.name_regEx = re.compile(pattern=r'itemprop=\"name\">(.+)(?=</[sS]pan></[dD]iv><[sS]pan [cC]lass=)')
        self.age_regEx = re.compile(pattern=r'=\"age\">(\d*)<')
        self.url_regEx = re.compile(pattern=r'url\(\"(https://.+\.jpg)\"')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('debuggerAddress', 'localhost:9222')
        self.driver = webdriver.Chrome(executable_path=driver_path, options=self.options)

    def __repr__(self) -> str:
        return 'This script gets the data from your likes on Tinder. You must have (1) Tinder Platinum and (2) Chrome running on a localhost.'

    def main(self):
        self.driver.get(url=self.url)

        # Click the Allow button
        try:
            self.driver.find_element_by_xpath(xpath='//*[@id="c207610411"]/div/div/div/div/div[3]/button[1]/span').click()
        except Exception as e:
            pass
        time.sleep(2)

        # Click the I Accept button
        try:
            self.driver.find_element_by_xpath(xpath='//*[@id="c-13730025"]/div/div[2]/div/div/div[1]/button').click()
        except Exception as e:
            pass
        time.sleep(2)

        # Click the Likes Sent button
        self.driver.find_element_by_xpath(xpath='//*[@id="s-791056625"]/div[1]/div[2]/a').click()
        time.sleep(3)


        # Press a point on the page that gives a reference for scrolling to the bottom
        self.random_div = self.driver.find_element_by_xpath(xpath='//*[@id="c609262533"]/div[1]/div/button')
        self.action = webdriver.common.action_chains.ActionChains(self.driver)
        self.action.move_to_element_with_offset(self.random_div, 0, 90)
        self.action.click()
        self.action.perform()
        self.html = self.driver.find_element_by_tag_name('html')

        time.sleep(3)

        # Scroll to the bottom and gather data for dataframe
        for _ in range(130):
            final_html = self.driver.page_source

            self.soup = BeautifulSoup(final_html, 'html.parser')

            cards = self.soup.find_all('div', {'class': 'Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox'})
            stats = self.soup.find_all('div', {'class': 'D(f) Ai(c) Miw(0)'})

            stat_count = 0

            for card in cards:
                if 'url' in str(card):
                    the_url = re.search(pattern=self.url_regEx, string=str(card)).group(1)

                    if the_url in self.URLS:
                        stat_count += 1
                        continue
                    else:
                        self.URLS.append(the_url)

                        self.picture_count += 1

                        the_stat = str(stats[stat_count])

                        # Get the person's name
                        self.name = re.search(pattern=self.name_regEx, string=the_stat).group(1).title()

                        # Try to get the person's age
                        try:
                            self.age = re.search(pattern=self.age_regEx, string=the_stat).group(1)
                        except Exception as e:
                            self.age = 'Age Not Found'

                        # Append person's name and age to the "records" list and print to stdout
                        self.records.append((self.name, self.age))
                        print(f'Name: {self.name}, Age: {self.age}')

                        # Download the profile picture
                        r = requests.get(url=the_url)

                        with open(file=f'./tinder_pics/{self.picture_count}_{self.name}.jpg', mode='wb') as pp:
                            pp.write(r.content)

                        # Increment the count for the section that has the person's name and age
                        stat_count += 1
                        
            time.sleep(1.5)
            self.html.send_keys(Keys.END)

    def pandas_to_excel(self):
        self.df = pd.DataFrame(data=self.records, columns=['Name', 'Age'])
        self.df.to_excel(excel_writer=self.records_path, sheet_name='Tinder Results', index=False, freeze_panes=(1,0))

# Instantiate the class and call the necessary functions, inputting your arguments
if __name__ == '__main__':
    c = MyLikes(url='https://tinder.com/app/recs', 
                driver_path=r'C:\Users\Alex\Desktop\Python drivers\chromedriver.exe',
                records_path=r'C:\Users\Alex\Desktop\Tinder_data.xlsx')
    c.main()
    c.pandas_to_excel()
