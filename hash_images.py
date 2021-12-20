import imagehash
import os
from PIL import Image
from tqdm import tqdm

def hash_images(directory: str, hashes=list()) -> None:
    """
    NOTE
    The images are named like: C:\\Users\\Alex\\Desktop\\hello\\my_tinder_test\\tinder_pics\\311_Hannah_5.jpg
    The directory's items need to be sorted by the number at the beginning of the filename (e.g., 311 in this example)
    """

    # Iterate over all the items in a directory, only hashing jpgs (can expand this to be other filetypes, if necessary)
    for item in tqdm(sorted(os.listdir(path=directory), key=lambda x: int(x.split('_')[0]))):
        if item.endswith('.jpg'):
            hashes.append(str(imagehash.phash(image=Image.open(fp=os.path.join(directory, item)))))

    # Create a list of tuples which include only the image names and their respective hashes.
    objects = list(zip([item for 
                        item in 
                        sorted(os.listdir(path=directory), key=lambda x: int(x.split('_')[0])) 
                        if item.endswith('.jpg')], 
                        hashes)
    )

    # Write all of the hash values to a text file (can write to Excel or csv with pandas, if necessary)
    with open(file='./hash_images.txt', mode='w', encoding='utf-8-sig') as f:
        for i in range(len(hashes)):
            if i == (len(hashes) - 1):                               # If we're at the last image, don't add the new line
                f.write(objects[i][0] + '|' + objects[i][1])
            else:                                                    # Otherwise, we're not at the last image, so add the new line
                f.write(objects[i][0] + '|' + objects[i][1] + '\n')

# Call the function
if __name__ == '__main__':
    hash_images(directory=r'C:\Users\Alex\Desktop\hello\my_tinder_test\tinder_pics')
