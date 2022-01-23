import imagehash
import os
import pandas as pd
from PIL import Image
from tqdm import tqdm

def hash_images_1(directory: str, hashes=list()) -> None:
    """
    NOTE
    The images are named like: C:\\Users\\Alex\\Desktop\\hello\\my_tinder_test\\tinder_pics\\311_Hannah_5.jpg
    The directory's items need to be sorted by the number at the beginning of the filename (e.g., 311 in this example)
    """

    # Iterate over all the items in a directory, only hashing jpgs (can expand this to be other filetypes, if necessary)
    for item in tqdm(sorted(os.listdir(path=directory), key=lambda x: int(x.split('_')[0]))):
        if item.endswith('.jpg'):
            # Append the hash
            hashes.append(str(imagehash.phash(image=Image.open(fp=os.path.join(directory, item)))))

    # Create a list of tuples which include only the image names and their respective hashes.
    objects = list(zip([item for 
                        item in 
                        sorted(os.listdir(path=directory), key=lambda x: int(x.split('_')[0])) 
                        if item.endswith('.jpg')], 
                        hashes)
    )

    # Write all of the image names and their respective hash values to a text file (can write to Excel or csv with pandas, if necessary)
    with open(file='./hash_images.txt', mode='w', encoding='utf-8-sig') as f:
        for i in range(len(hashes)):
            if i == (len(hashes) - 1):                               # If we're at the last image, don't add the new line
                f.write(objects[i][0] + '|' + objects[i][1])
            else:                                                    # Otherwise, we're not at the last image, so add the new line
                f.write(objects[i][0] + '|' + objects[i][1] + '\n')

def hash_images_2(directory: str, records=list()) -> None:
    """
    NOTE
    The images are named like: C:\\Users\\Alex\\Downloads\\Tinder is maddening\\maddy - 2.jpg

    TODO
    Potentially, we may want to calculate the hamming distance between images so that similar images, whose 
    hashes don't match exactly, are seen as a match if they're defined as "similar enough" or something like that.
    """

    # Iterate over all the items in a directory, only hashing jpgs (can expand this to be other filetypes, if necessary)
    for item in tqdm(sorted(os.listdir(path=directory), key=lambda x: int(x.split(' - ')[-1].split('.')[0]))):
        if item.endswith('.jpg'):
            # Append the image's name and the hash
            records.append((item, str(imagehash.phash(image=Image.open(fp=os.path.join(directory, item))))))
    
    # Write the data to Excel
    pandas_to_excel(data=records, records_path=r'C:\Users\Alex\Desktop\My_Hashes.xlsx', sheet_name='Hashes')

def pandas_to_excel(data: list, records_path: str, sheet_name: str) -> None:
        df = pd.DataFrame(data=data, columns=['File Name', 'Hash'])
        df.to_excel(excel_writer=records_path, 
                         sheet_name=sheet_name, 
                         index=False, 
                         freeze_panes=(1,0)
                         )

# Call the function(s)
if __name__ == '__main__':
    directory = input('Please input your directory:\n\t')
    hash_images_2(directory=directory)
