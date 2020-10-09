import io
import sys
PATH = 'D:/OneDrive - Pontificia Universidad Javeriana/Academic/ISCO/Analitica de Datos y Big Data/laboratories/PredictiveAnalytics'
DIR_DATA = PATH + '/data/input/'
sys.path.append(PATH) if PATH not in list(sys.path) else None
sys.path.append(DIR_DATA) if DIR_DATA not in list(sys.path) else None
import os
import spacy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from collections import Counter
from imblearn.over_sampling import RandomOverSampler
from utils.text_analysis import TextAnalysis
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression 
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix


ta = TextAnalysis('es')
data_raw = pd.read_csv('data.csv')
data_raw.head()

