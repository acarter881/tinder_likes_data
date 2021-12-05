import numpy as np
import pandas as pd
import emoji
from PIL import Image
from wordcloud import WordCloud
from collections import Counter

class TinderData:
    def __init__(self, path_to_workbook) -> None:
        self.path_to_workbook = path_to_workbook
        self.emojis = emoji.UNICODE_EMOJI_ENGLISH

    def __repr__(self) -> str:
        return 'This class takes data from an Excel workbook as input and performs basic analysis.'

    def load_workbook(self) -> None:
        # Load the dataframe
        self.df = pd.read_excel(self.path_to_workbook)
        
    def initial_clean(self) -> None:
        # The number of profiles that did not include a bio
        self.no_bio = sum([1 for value in self.df['Bio'] if value == 'Bio Not Found'])
        
        # Replace the "Bio Not Found" with None
        self.df['Bio'].replace({'Bio Not Found': None}, inplace=True)

        # # Create a dataframe that will be used for the emojis
        # self.bio_df = self.df['Bio'][self.df['Bio'].notna()]
        # self.bio_df = pd.DataFrame(data=self.bio_df)

        # The number of profiles that did not select a passion
        self.no_passions = sum([1 for value in self.df['Passions'] if value == 'Passions Not Found'])
        
        # Replace the "Passions Not Found" with None
        self.df['Passions'].replace({'Passions Not Found': None}, inplace=True)

        # Convert the Distance column to floating point, converting the 'Distance Not Found' text to NaN
        self.df['Distance'] = pd.to_numeric(self.df['Distance'], errors='coerce', downcast='float')

    def word_cloud(self) -> None:
        # Punctuations and uninteresting words to process text
        punctuations = '''!()-.[]{};:'"\,<>./?@#$%^&*_~'''
    
        # uninteresting_words = ["a", 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
        # 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        # "the", "to", "if", "is", "it", "of", "and", "or", "an", "as", "i", "me", "my", 
        # "we", "our", "ours", "you", "your", "yours", "he", "she", "him", "his", "her", "hers", "its", "they", "them", 
        # "their", "what", "which", "who", "whom", "this", "that", "am", "are", "was", "were", "be", "been", "being", 
        # "have", "has", "had", "do", "does", "did", "but", "at", "by", "with", "from", "here", "when", "where", "how", 
        # "all", "any", "both", "each", "few", "more", "some", "such", "no", "nor", "too", "very", "can", "will", "just"]

        uninteresting_words = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

        # Create a text list that ignores the "None" values
        text = [line.split() for line in self.df['Bio'] if line is not None]

        # Create the words string
        self.words = ''

        # Iterate over the text list and add the words to the words string
        for line in text:
            for word in line:
                self.words += word.lower() + ' '

        self.words_for_emoji = self.words
    
        # Text transformations
        self.words = self.words.replace('insta', 'ig')
        self.words = self.words.replace('instagram', 'ig')
        self.words = self.words.replace('iggram', 'ig')
        self.words = self.words.translate(str.maketrans('', '', punctuations))
        self.words = [word for word in self.words.split() if word.isalpha() and word not in uninteresting_words]

        # Create the mask
        mask = np.array(Image.open(r'C:\Users\Alex\Downloads\romeo_mask-1.jpg'))
        # mask[mask < 1] = 255
      
        # Create the word cloud
        cloud = WordCloud(font_path=r'C:\Windows\Fonts\HoboStd.otf', max_words=150, max_font_size=50, min_font_size=0, random_state=5, colormap='autumn', mask=mask).generate_from_frequencies(Counter(self.words))
        cloud.to_file('my_cloud.png')

    def emoji_data(self) -> None:
        # Emoji fun
        emojis = Counter([char for char in self.words_for_emoji if char in self.emojis])
        emojis_df = pd.DataFrame.from_dict(data=emojis, orient='index')
        emojis_df.columns = ['Count']
        emojis_df.sort_values(by='Count', ascending=False, inplace=True)
        emojis_df.to_excel(excel_writer='./emojis.xlsx', sheet_name='Emojis', index=True, freeze_panes=(1,0))

    def basic_stats(self) -> None:
        # Display the count of the number of profiles
        print(f'The number of profiles is {len(self.df)}.')

        # Display the average and median age from the profiles. Profiles without an age are NOT included in the count of profiles.
        mean_age = round(self.df['Age'].mean(skipna=True), 2)
        median_age = round(self.df['Age'].median(skipna=True))

        print(f'The average match is {mean_age} years old.')
        print(f'The median match is {median_age} years old.')

        # Display the average and median distance from the profiles. Profiles without a distance are NOT included in the count of profiles.
        mean_distance = round(self.df['Distance'].mean(skipna=True))
        median_distance = round(self.df['Distance'].median(skipna=True))

        print(f'The average match is {mean_distance} miles away from me.')
        print(f'The median match is {median_distance} miles away from me.')

        # Display the top 10 names
        names = self.df.groupby('Name').size().sort_values(ascending=False).head(n=10).reset_index().rename(columns={0:'Count'})

        names.index = np.arange(1, len(names) + 1)

        print(names.head(n=10))

        # Display the number of profiles that did not select a passion, followed by the top 10 passions
        print(f'The number of profiles that did not select any Passions is {self.no_passions}, out of a total of {len(self.df)} profiles.\nThis equates to {round((self.no_passions / len(self.df)) * 100, 2)}%.')

        passions = [passion for sublist in self.df['Passions'].dropna().str.split(',').tolist() for passion in sublist]

        passions_summary = pd.DataFrame(data=passions, columns=['Passions']).value_counts().reset_index().rename(columns={0:'Count'})

        passions_summary.index = np.arange(1, len(passions_summary) + 1)

        print(passions_summary.head(n=10))

        # Display the number of profiles that did not have anything in the "bio" section
        print(f'The number of profiles that did not have a bio is {self.no_bio}, out of a total of {len(self.df)} profiles.\nThis equates to {round((self.no_bio / len(self.df)) * 100, 2)}%.')

if __name__ == '__main__':
    c = TinderData(path_to_workbook=r'C:\Users\Alex\Downloads\tinder - Excel workbooks\Tinder_Card_Data.xlsx')
    c.load_workbook()
    c.initial_clean()
    c.word_cloud()
    c.emoji_data()
    c.basic_stats()
