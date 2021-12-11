import time
import re
import pyautogui
import requests
import sys
import random
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

class MyLikes:
    def __init__(self, url, driver_path, records_path) -> None:
        self.url = url                      # URL for selenium
        self.complete = False               # Is the script finished?
        self.incrementer = 0                # Variable to replace a count within a for loop for `main`
        self.card_identifier = dict()       # Unique identifier for a profile card
        self.picture_count = 0              # This helps to identify the profile card we're on and is also used in the filenames
        self.records = list()               # Storing the data to be written to an Excel workbook
        self.records_path = records_path    # Path to save the Excel workbook
        self.now = datetime.utcnow()        # Store the start time of the script in a variable
        self.url_regEx = re.compile(pattern=r'url\(\"(https://.+\.jpg)\"')
        self.card_identifier_regEx = re.compile(pattern=r'https://images-ssl.gotinder.com/(.+)/\d{3}x')
        self.options = webdriver.ChromeOptions() # Standard for using Chrome with selenium
        self.options.add_experimental_option('debuggerAddress', 'localhost:9222') # Running Chrome on localhost
        self.driver = webdriver.Chrome(executable_path=driver_path, options=self.options) # Standard for using Chrome with selenium
        self.headers = { # Headers for our requests. These are very important. Without them, we can get timed out or banned.
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://tinder.com/',
                    'dnt': '1'
        }

    def __repr__(self) -> str:
        return 'This script is intended to download all of the pictures and videos from the profiles on the "Likes Sent" section of Tinder.'

    def log_in(self) -> None:
        # Open the URL in Chrome
        self.driver.get(url=self.url)
        time.sleep(4)
                                               
        # Click the Likes Sent button           
        self.driver.find_element_by_xpath(xpath='//a[@href="/app/my-likes"]').click() # Selecting by the href of an anchor (i.e., 'a') tag
        time.sleep(3)

    def main(self) -> None:
        while not self.complete:
            time.sleep(3)

            # Get the current page's HTML
            final_html = self.driver.page_source

            # Create a soup object
            self.soup = BeautifulSoup(final_html, 'html.parser')

            # Find all profile cards within the current HTML
            cards = self.soup.find_all('div', {'aria-label': re.compile(pattern=r'.*'), 'class': 'Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox'})

            # Find the div's id for the div that holds the profile cards. This is important because Tinder frequently changes this id 
            div_id = self.soup.find('div', {'class': 'likesYou__scroller Sb(s) D(f) Jc(c) Fxd(c) Animtf(l) Animfm(f) Animdur(.75s) Ovy(s) Ovsb(n) Ovs(touch)'})['id']
            
            # Iterate over the profile cards
            for card in cards:  
                card_identifier = re.search(pattern=self.card_identifier_regEx, string=str(card)).group(1)

                if self.card_identifier.get(card_identifier) is not None:
                    continue # Since the profile card ID is in the dictionary, skip this card and go to the next card
                else:        # Since we haven't gathered the profile data, gather now
                    # Click in the background
                    pyautogui.moveTo(x=1850, y=350, duration=0.1)
                    pyautogui.click()

                    # Add the card ID to the dictionary
                    self.card_identifier.setdefault(card_identifier, 0)

                    # Increment the picture count
                    self.picture_count += 1

                    # Click the relevant profile card           
                    if self.driver.find_element_by_xpath(xpath=f'//*[@id="{div_id}"]/div[2]/div[{self.picture_count}]/div/div/span/div') is not None: # Tinder may change the div the xpath relates to. I can probably write a regular expression to account for this, but I manually updated this one.
                        try:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="{div_id}"]/div[2]/div[{self.picture_count}]/div/div/span/div').click()
                        except Exception as e:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="{div_id}"]/div[2]/div[{self.picture_count}]/div/div/span/div[2]/video').click()
                    elif self.driver.find_element_by_xpath(xpath=f'//*[@id="{div_id}"]/div[2]/div[{self.picture_count}]/div/div') is not None:
                        self.driver.find_element_by_xpath(xpath=f'//*[@id="{div_id}"]/div[2]/div[{self.picture_count}]/div/div').click()
                    else:
                        self.complete = True
                        sys.exit('The script is complete. There are no more profile cards to go through.')
                                     
                    time.sleep(1)

                    # Get HTML of the profile card
                    profile_html = self.driver.page_source

                    second_soup = BeautifulSoup(profile_html, 'html.parser')

                    name = second_soup.find('h1', {'class': 'Fz($xl) Fw($bold) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)'}).text.title()

                    # Get the total number of pages in the profile card
                    try:
                        number_of_pages = int(second_soup.find('button', {'class': 'bullet D(ib) Va(m) Cnt($blank)::a D(b)::a Cur(p) bullet--active H(4px)::a W(100%)::a Py(4px) Px(2px) W(100%) Bdrs(100px)::a Bgc(#fff)::a focus-background-style'}).text.split('/')[1])
                    except Exception:  
                        number_of_pages = 1 # If there's only one page, there won't be a button.

                    # Iterate over the number of pages
                    for i in range(0, number_of_pages, 1):
                        time.sleep(1)

                        page_html = self.driver.page_source

                        page_soup = BeautifulSoup(page_html, 'html.parser')

                        current_card = page_soup.find('span', {'class': 'keen-slider__slide Wc($transform) Fxg(1)', 'aria-hidden': 'false', 'style': re.compile(pattern=r'.+')})

                        vid = current_card.find('video', {'class': 'W(100%)'})

                        if vid: 
                            vid = vid['src']
                            download_url = vid
                        else:
                            pic = re.search(pattern=self.url_regEx, string=str(current_card)).group(1)
                            download_url = pic

                        r = requests.get(url=download_url, headers=self.headers)     

                        # content_type, res_date, res_last_mod, e_tag = r.headers['Content-Type'], r.headers['Date'], r.headers['Last-Modified'], r.headers['ETag'].strip('\"')
                        # res_last_mod = self.to_datetime_obj(date_str=res_last_mod)
                        # self.records.append((self.picture_count, name, card_identifier, content_type, res_date, res_last_mod, self.now, e_tag)) 

                        with open(file=f'./tinder_pics/{self.picture_count}_{name}_{i+1}.{download_url[-3:]}', mode='wb') as file:
                            file.write(r.content)   
                         
                        if i != (number_of_pages - 1):
                            pyautogui.moveTo(x=1250, y=400, duration=0.1)
                            pyautogui.click()
                            time.sleep(1)
                        else:
                            continue
                                       
                    pyautogui.moveTo(x=1850, y=350, duration=0.1)
                    pyautogui.click()

                    time.sleep(1)

            if self.incrementer == 0:
                pyautogui.moveTo(x=1850, y=350, duration=0.5)
                time.sleep(1)
                print(f'Run number: {self.incrementer} | {pyautogui.position()}')
                pyautogui.scroll(clicks=-2000)
                time.sleep(2.5)
                pyautogui.scroll(clicks=-280)
                time.sleep(1)
                self.incrementer += 1
            else:
                print(f'Run number: {self.incrementer} | {pyautogui.position()}')
                time.sleep(random.randint(2, 3))
                pyautogui.scroll(clicks=-755)
                time.sleep(random.randint(2, 3))
                self.incrementer += 1

    #def to_datetime_obj(self, date_str) -> datetime.strptime:
        #return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z') 
    
    #def pandas_to_excel(self) -> None:
        #self.df = pd.DataFrame(data=self.records, columns=['Name', 'Age', 'Distance', 'Bio', 'Passions', 'Song_Title', 'Song_Artist'])
        #self.df.to_excel(excel_writer=self.records_path, sheet_name='Tinder Card Data', index=False, freeze_panes=(1,0))
              
# Instantiate the class and call the necessary functions, inputting your arguments
if __name__ == '__main__':
    c = MyLikes(url='https://tinder.com/app/recs', 
                driver_path=r'C:\Users\Alex\Desktop\Python drivers\chromedriver.exe',
                records_path=r'C:\Users\Alex\Desktop\Date_Test.xlsx')
    c.log_in()
    c.main()
