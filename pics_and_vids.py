import time
import re
import pyautogui
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

class MyLikes:
    def __init__(self, url, driver_path) -> None:
        self.url = url
        self.URLS = list()
        self.saved_picture_urls = list()
        self.saved_video_urls = list()
        self.video_ids = list()
        self.picture_count = 0
        self.url_regEx = re.compile(pattern=r'url\(\"(https://.+\.jpg)\"')
        self.video_regEx = re.compile(pattern=r'playsinline.*src=\"(.+\.mp4)\"')
        self.video_id_regEx = re.compile(pattern=r'https://images-ssl.gotinder.com/.*\d{3}x\d{3}_(.*)\_h264\.mp4')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('debuggerAddress', 'localhost:9222')
        self.driver = webdriver.Chrome(executable_path=driver_path, options=self.options)

    def __repr__(self) -> str:
        return 'This script is intended to download all of the pictures and videos from the profiles on the "Likes Sent" section of Tinder.'

    def log_in(self):
        # Open the URL in Chrome
        self.driver.get(url=self.url)
        time.sleep(4)

        # Click the Likes Sent button
        self.driver.find_element_by_xpath(xpath='//*[@id="c-1281713969"]/div[1]/div[2]/a').click()
        time.sleep(3)

    def main(self):
        for i in range(30): # This range can be pretty much anything, really. This is probably overkill, but you don't want to set it to a number where there will still be profiles to download
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

                    # Increment the picture count
                    self.picture_count += 1

                    # Click the relevant profile card
                    try:                              # Try to click on the profile picture (i.e., it's not a video)       
                        self.driver.find_element_by_xpath(xpath=f'//*[@id="c609262533"]/div[2]/div[{self.picture_count}]/div/div/span/div').click()
                    except Exception as e:            # Click on the profile video (i.e., it's not a picture). When there aren't any more profiles to view, the script will error here and you're done.
                        self.driver.find_element_by_xpath(xpath=f'//*[@id="c609262533"]/div[2]/div[{self.picture_count}]/div/div').click()
                    
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
                    for j in range(1, number_of_pages, 1):
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
                                # We have to append each profile's last picture's URL to the "URLS" list since the last picture is shown when clicking off a profile
                                if j == (number_of_pages - 1):
                                    self.URLS.append(pot_url)

                                pic_url_counter += 1

                                self.saved_picture_urls.append(pot_url)

                                r = requests.get(url=pot_url)

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

                                        r = requests.get(url=pot_vid_url)

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
                print(f'Run number: {i}')
                pyautogui.scroll(clicks=-2000)
                time.sleep(2.5)
                pyautogui.scroll(clicks=-280)
                time.sleep(1)
            else:
                print(f'Run number: {i}')
                time.sleep(2.5)
                pyautogui.scroll(clicks=-755)
                time.sleep(2.5)
            
# Instantiate the class and call the necessary functions, inputting your arguments
if __name__ == '__main__':
    c = MyLikes(url='https://tinder.com/app/recs', 
                driver_path=r'C:\Users\Alex\Desktop\Python drivers\chromedriver.exe')
    c.log_in()
    c.main()
