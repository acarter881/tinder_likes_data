import time
import re
import pyautogui
import pandas as pd
# import sys
# from collections import namedtuple
from selenium import webdriver
from bs4 import BeautifulSoup

class MyLikes:
    def __init__(self, url, driver_path, records_path) -> None:
        self.url = url
        self.picture_count = 0
        self.URLS = list()
        self.records = list()
        self.records_path = records_path
        # self.records_columns = namedtuple('CardData', ['Name', 'Age', 'Distance', 'Bio', 'Passions', 'Song_Title', 'Song_Artist'])
        self.passions = list()
        self.passions_all = list()
        self.url_regEx = re.compile(pattern=r'url\(\"(https://.+\.jpg)\"')
        self.distance_regEx = re.compile(pattern=r'(\d+) miles away')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('debuggerAddress', 'localhost:9222')
        self.driver = webdriver.Chrome(executable_path=driver_path, options=self.options)

    def __repr__(self) -> str:
        return 'This script is intended to download data from all the profile cards in the Likes Sent section of Tinder Platinum.'

    def log_in(self):
        # Open the URL in Chrome
        self.driver.get(url=self.url)
        time.sleep(4)
                                               
        # Click the Likes Sent button
        self.driver.find_element_by_xpath(xpath='//*[@id="q-1452937969"]/div[1]/div[2]/a').click() # Tinder may change the div the xpath relates to. I can probably write a regular expression to account for this, but I manually updated this one.
        time.sleep(3)

    def main(self):
        for i in range(200): # This range can be pretty much anything, really. This is probably overkill, but you don't want to set it to a number where there will still be profiles to download
            time.sleep(3)

            # Get the current page's HTML
            final_html = self.driver.page_source

            # Create a soup object
            self.soup = BeautifulSoup(final_html, 'html.parser')

            cards = self.soup.find_all('div', {'aria-label': re.compile(pattern='.*'), 'class': 'Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox'})

            # Iterate over the profile cards
            for card in cards:                
                the_url = re.search(pattern=self.url_regEx, string=str(card)).group(1)
                
                if the_url in self.URLS:
                    continue # Since the profile picture URL is in the list, skip this card and go to the next card
                else:        # Since we haven't gathered the profile data, gather now
                    # Click in the background
                    pyautogui.moveTo(x=1850, y=350, duration=0.1)
                    pyautogui.click()

                    # Add the URL to the URLS list
                    self.URLS.append(the_url)

                    self.picture_count += 1

                    time.sleep(1)

                    # Click the relevant profile card           
                    if self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div') is not None: # Tinder may change the div the xpath relates to. I can probably write a regular expression to account for this, but I manually updated this one.
                        try:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div').click()
                        except Exception as e:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div[2]/video').click()
                    elif self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div') is not None:
                        self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div').click()
                    else:
                        # There are no more profile cards to go through; write the data in memory to disk.
                        print('There are no more profile cards to go through; writing the data to disk.')
                        break
                        # self.pandas_to_excel()
                                     
                    time.sleep(1)

                    # Get HTML of the profile card
                    card_html = self.driver.page_source

                    card_soup = BeautifulSoup(card_html, 'html.parser')

                    # Try to get the name from the profile card
                    if card_soup.find('h1', {'class': 'Fz($xl) Fw($bold) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)'}) is not None:
                        name = card_soup.find('h1', {'class': 'Fz($xl) Fw($bold) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)'}).text.title()
                    else:
                        name = 'Name Not Found'

                    # Try to get the age from the profile card
                    if card_soup.find('span', {'class': 'Whs(nw) Fz($l)'}) is not None:
                        age = card_soup.find('span', {'class': 'Whs(nw) Fz($l)'}).text
                    else:
                        age = 'Age Not Found'

                    # Try to get the distance from me from the profile card
                    if card_soup.find('div', {'class': 'Fz($ms)'}) is not None:
                        row_text = str(card_soup.find('div', {'class': 'Fz($ms)'}))

                        if re.search(pattern=self.distance_regEx, string=row_text):
                            distance = re.search(pattern=self.distance_regEx, string=row_text).group(1)
                        else:
                            distance = 'Distance Not Found'
                    else:
                        distance = 'Distance Not Found'

                    # Try to get the bio from the profile card
                    if card_soup.find('div', {'class': 'P(16px) Us(t) C($c-secondary) BreakWord Whs(pl) Fz($ms)'}) is not None:
                        bio = card_soup.find('div', {'class': 'P(16px) Us(t) C($c-secondary) BreakWord Whs(pl) Fz($ms)'}).text
                    else:
                        bio = 'Bio Not Found'

                    # Try to get the passions from the profile card
                    if card_soup.find_all('div', {'class': 'Bdrs(100px) Bd D(ib) Va(m) Fz($xs) Mend(8px) Mb(8px) Px(8px) Py(4px) Bdc($c-secondary) C($c-secondary)'}) is not None:
                        passions = card_soup.find_all('div', {'class': 'Bdrs(100px) Bd D(ib) Va(m) Fz($xs) Mend(8px) Mb(8px) Px(8px) Py(4px) Bdc($c-secondary) C($c-secondary)'})

                        passions_text = ''

                        for passion in passions:
                            passions_text += passion.text + ','
                            self.passions_all.append(passion)

                        passions_text = passions_text.strip(',')
                    else:
                        passions_text = 'Passions Not Found'

                    if passions_text == '':
                        passions_text = 'Passions Not Found'

                    # Try to get the "My Anthem" from the profile card
                    if card_soup.find('div', {'class': 'Mb(4px) Ell Fz($ms)'}) is not None:
                        song_title = card_soup.find('div', {'class': 'Mb(4px) Ell Fz($ms)'}).text
                        song_artist = card_soup.find('span', {'class': 'Mstart(4px) Ell'}).text
                    else:
                        song_title = 'No Song Title Found'
                        song_artist = 'No Song Artist Found'

                    self.records.append((name, age, distance, bio, passions_text, song_title, song_artist))

                    # When done going through the pictures/videos, click off of the profile card
                    pyautogui.moveTo(x=1850, y=350, duration=0.1)
                    pyautogui.click()

                    time.sleep(1)

            if i == 0:
                pyautogui.moveTo(x=1850, y=350, duration=0.5)
                time.sleep(1)
                print(f'Run number: {i} | {pyautogui.position()}')
                pyautogui.scroll(clicks=-2000)
                time.sleep(2.5)
                pyautogui.scroll(clicks=-280)
                time.sleep(1)
            else:
                print(f'Run number: {i} | {pyautogui.position()}')
                time.sleep(2.5)
                pyautogui.scroll(clicks=-755)
                time.sleep(2.5)
            
    def pandas_to_excel(self):
        self.df = pd.DataFrame(data=self.records, columns=['Name', 'Age', 'Distance', 'Bio', 'Passions', 'Song_Title', 'Song_Artist'])
        self.df.to_excel(excel_writer=self.records_path, sheet_name='Tinder Card Data', index=False, freeze_panes=(1,0))

        self.df_2 = pd.DataFrame(data=self.passions_all, columns=['Passions'])
        self.df_2.to_excel(excel_writer=r'C:\Users\Alex\Desktop\Tinder_Passions.xlsx', sheet_name='Tinder Passions', index=False, freeze_panes=(1,0))
    
# Instantiate the class and call the necessary functions, inputting your arguments
if __name__ == '__main__':
    c = MyLikes(url='https://tinder.com/app/recs', 
                driver_path=r'C:\Users\Alex\Desktop\Python drivers\chromedriver.exe',
                records_path=r'C:\Users\Alex\Desktop\Tinder_Card_Data.xlsx')
    c.log_in()
    c.main()
    c.pandas_to_excel()
