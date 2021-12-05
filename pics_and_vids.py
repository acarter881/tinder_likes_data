import time
import re
import pyautogui
import requests
import sys
import random
from selenium import webdriver
from bs4 import BeautifulSoup

class MyLikes:
    def __init__(self, url, driver_path) -> None:
        self.url = url
        self.saved_picture_urls = list()
        self.saved_video_urls = list()
        self.video_ids = list()
        self.card_identifier = dict()
        self.picture_count = 0
        self.url_regEx = re.compile(pattern=r'url\(\"(https://.+\.jpg)\"')
        self.video_regEx = re.compile(pattern=r'playsinline.*src=\"(.+\.mp4)\"')
        self.video_id_regEx = re.compile(pattern=r'https://images-ssl.gotinder.com/.*\d{3}x\d{3}_(.*)\_h264\.mp4')
        self.card_identifier_regEx = re.compile(pattern=r'https://images-ssl.gotinder.com/(.+)/\d{3}x')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('debuggerAddress', 'localhost:9222')
        self.driver = webdriver.Chrome(executable_path=driver_path, options=self.options)
        self.headers = {
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
        self.driver.find_element_by_xpath(xpath='//*[@id="q-1452937969"]/div[1]/div[2]/a').click() # Tinder may change the div the xpath relates to. I can probably write a regular expression to account for this, but I manually updated this one.
        time.sleep(3)

    def main(self) -> None:
        for i in range(350): # This range can be pretty much anything, really. This is probably overkill, but you don't want to set it to a number where there will still be profiles to download
            time.sleep(3)

            # Get the current page's HTML
            final_html = self.driver.page_source

            # Create a soup object
            self.soup = BeautifulSoup(final_html, 'html.parser')

            cards = self.soup.find_all('div', {'aria-label': re.compile(pattern='.*'), 'class': 'Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox'})

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
                    if self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div') is not None: # Tinder may change the div the xpath relates to. I can probably write a regular expression to account for this, but I manually updated this one.
                        try:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div').click()
                        except Exception as e:
                            self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div/span/div[2]/video').click()
                    elif self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div') is not None:
                        self.driver.find_element_by_xpath(xpath=f'//*[@id="q438038533"]/div[2]/div[{self.picture_count}]/div/div').click()
                    else:
                        sys.exit('The script is complete. There are no more profile cards to go through.')
                                     
                    time.sleep(1)

                    # Get HTML of the profile card
                    profile_html = self.driver.page_source

                    second_soup = BeautifulSoup(profile_html, 'html.parser')

                    name = second_soup.find('h1', {'class': 'Fz($xl) Fw($bold) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)'}).text.title()

                    # Get the total number of pages in the profile card
                    try:
                        number_of_pages = int(second_soup.find('button', {'class': 'bullet D(ib) Va(m) Cnt($blank)::a D(b)::a Cur(p) bullet--active H(4px)::a W(100%)::a Py(4px) Px(2px) W(100%) Bdrs(100px)::a Bgc(#fff)::a focus-background-style'}).text.split('/')[1])
                    except Exception as e:  
                        number_of_pages = 2 # If the page only has one page, set this to 2 so the loop below will run one time, as the loop starts at 1

                    pic_url_counter = 0

                    # Iterate over the profile's pictures/videos
                    for _ in range(1, number_of_pages, 1):
                        time.sleep(1)

                        page_html = self.driver.page_source

                        page_soup = BeautifulSoup(page_html, 'html.parser')

                        pot_pics = page_soup.find_all('div', {'class': 'profileCard__slider__img Z(-1)'})

                        pot_vids = page_soup.find_all('video', {'class': 'W(100%)'}) 

                        # Download available profile pictures
                        for item in pot_pics:
                            pot_url = re.search(pattern=self.url_regEx, string=str(item)).group(1)

                            if pot_url in self.saved_picture_urls:
                                continue
                            else:                               
                                pic_url_counter += 1

                                self.saved_picture_urls.append(pot_url)

                                r = requests.get(url=pot_url, headers=self.headers)

                                #print(r.headers) # The 'Content-Type' is either 'image/jpeg' (picture) or 'application/octet-stream' (video). The date the user uploaded the picture/video is found in 'Last-Modified'.

                                with open(file=f'./tinder_pics/{self.picture_count}_{name}_{pic_url_counter}.jpg', mode='wb') as pic:
                                    pic.write(r.content)
                        
                        # Download a video, if available
                        if pot_vids: # Only going to recognize and download the "h264" videos
                            for item in pot_vids:
                                try:
                                    pot_vid_url = re.search(pattern=self.video_regEx, string=str(item)).group(1)

                                    vid_id = re.search(pattern=self.video_id_regEx, string=pot_vid_url).group(1)

                                    if vid_id in self.video_ids:
                                        pass
                                    else:
                                        self.video_ids.append(vid_id)

                                        r = requests.get(url=pot_vid_url, headers=self.headers)

                                        with open(file=f'./tinder_pics/{self.picture_count}_{name}_video_{pic_url_counter}.mp4', mode='wb') as vid:
                                            vid.write(r.content)
                                except Exception as e:
                                    pass
                                        
                        # Click to go to the next page
                        pyautogui.moveTo(x=1250, y=400, duration=0.1)
                        pyautogui.click()

                        time.sleep(1)

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
                time.sleep(random.randint(2, 3))
                pyautogui.scroll(clicks=-755)
                time.sleep(random.randint(2, 3))
            
# Instantiate the class and call the necessary functions, inputting your arguments
if __name__ == '__main__':
    c = MyLikes(url='https://tinder.com/app/recs', 
                driver_path=r'C:\Users\Alex\Desktop\Python drivers\chromedriver.exe')
    c.log_in()
    c.main()
