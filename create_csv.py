from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm

from test import all_truth
def get_tweet(path):
    doc = ET.parse(path)
    root = doc.getroot()
    tweets = [i.text for i in root.iter('document')]
    return tweets

def get_names(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles


def is_humam(user_id,all_truth):
    n = len(all_truth)
    for i in range(n):
        if(user_id in all_truth[i]):
            aux = all_truth[i]
            if(aux[1]=='bot'):
                return 0
            else:
                return 1
            break
          

bot = 'bc3b33dd99909e387475b536fab5eef'
human = '59407dd42bda70c214da57fefe4c7764'
x = is_humam(bot,all_truth)
print(x)

path = './parcial1/xml'
all_names =  get_names(path)
all_names_copy = all_names.copy() # tiene .xml
n = len(all_names)
for i in range(n):
    all_names[i] = all_names[i].replace('.xml','')


n = len(all_names)
print('\nWriting a csv file')
with open('data.csv', 'w') as file:
    writer = csv.writer(file,lineterminator='\n')
    writer.writerow(['user_id','tweets','is_human'])
    for i in tqdm(range(n)):
        path2 = './parcial1/xml/'
        actual_name = all_names_copy[i]
        username = all_names[i]
        human = is_humam(username,all_truth)
        path2 += actual_name
        tweets = get_tweet(path2)
        writer.writerow([username,tweets,human])

    



