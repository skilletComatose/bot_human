import os
import re
import sys
import unicodedata
import spacy
from spacy.lang.es import Spanish
from spacy.lang.en import English
from nltk import SnowballStemmer
from spacymoji import Emoji
import pandas as pd
from tqdm import tqdm
from spacy_langdetect import LanguageDetector
from utils.steaming import Steaming
from utils.utils import Util


class TextAnalysis(object):
    """
    :Date: 2019-10-03
    :Version: 1.0
    :Author: Edwin Puertas & Gabriel Moreno - Pontificia Universidad Javeriana, Bogotá
    :Copyright: To be defined
    :Organization: Centro de Excelencia y Apropiación de Big Data y Data Analytics - CAOBA
    """
    name = 'text_analysis'

    def __init__(self, lang):
        """
        Constructor for the class
        :rtype: object
        :return: Text Analysis object
        """
        lang_stemm = {'es': 'spanish', 'en': 'english'}
        self.lang = lang
        self.stemmer = SnowballStemmer(language=lang_stemm[lang])
        self.nlp = self.load_sapcy(lang)

        
    def load_sapcy(self, lang):
        result = None
        try:
            stemmer_text = Steaming(lang)  # initialise component
            result = spacy.load('es_core_news_md') if lang == 'es' else spacy.load('en_core_web_md')
            emoji = Emoji(result)
            result.add_pipe(emoji, first=True)
            result.add_pipe(stemmer_text, after='parser', name='stemmer')
            print('Language: {0}\nText Analysis: {1}'.format(lang, result.pipe_names))
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error load_sapcy: {0}'.format(e))
        return result

    def analysis_pipe(self, text):
        result = None
        try:
            result = self.nlp(text)
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error analysis_pipe: {0}'.format(e))
        return result

    def tagger(self, text):
        result = None
        try:
            list_tagger = []
            doc = self.analysis_pipe(text.lower())
            for token in doc:
                item = {'text': token.text, 'lemma': token.lemma_, 'stem': token._.stem, 'pos': token.pos_,
                        'tag': token.tag_, 'dep': token.dep_, 'shape': token.shape_, 'is_alpha': token.is_alpha,
                        'is_stop': token.is_stop, 'is_digit': token.is_digit, 'is_punct': token.is_punct}
                list_tagger.append(item)
            result = list_tagger
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error tagger: {0}'.format(e))
        return result

    def language_detector(self, text):
        result = None
        try:
            doc = self.analysis_pipe(text.lower())
            for sent in doc.sents:
                if sent._.language['score'] > 0.8:
                    result = sent._.language['language']
                    break
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error language_detector: {0}'.format(e))
        return result

    def dependency(self, text):
        result = []
        try:
            doc = self.analysis_pipe(text.lower())
            doc_chunks = list(doc.noun_chunks)
            for chunk in doc_chunks:
                item = {'chunk': chunk, 'text': chunk.text,
                        'root_text': chunk.root.text, 'root_dep': chunk.root.dep_}
                result.append(item)
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error dependency: {0}'.format(e))
        return result

    def dependency_all(self, text):
        result = []
        try:
            doc = self.analysis_pipe(text.lower())
            for chunk in doc.noun_chunks:
                item = {'chunk': chunk, 'text': chunk.root.text, 'pos_': chunk.root.pos_, 'dep_': chunk.root.dep_,
                        'tag_': chunk.root.tag_, 'lemma_': chunk.root.lemma_, 'is_stop': chunk.root.is_stop,
                        'is_punct': chunk.root.is_punct, 'head_text': chunk.root.head.text,
                        'head_pos': chunk.root.head.pos_,
                        'children': [{'child': child, 'pos_': child.pos_, 'dep_': child.dep_,
                                      'tag_': child.tag_, 'lemma_': child.lemma_, 'is_stop': child.is_stop,
                                      'is_punct': child.is_punct, 'head.text': child.head.text,
                                      'head.pos_': child.head.pos_} for child in chunk.root.children]}
                result.append(item)
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error dependency_all: {0}'.format(e))
        return result

    def dependency_child(self, text):
        result = []
        try:
            doc = self.analysis_pipe(text.lower())
            for token in doc:
                item = {'chunk': token.text, 'text': token.text, 'pos_': token.pos_,
                        'dep_': token.dep_, 'tag_': token.tag_, 'head_text': token.head.text,
                        'head_pos': token.head.pos_, 'children': None}
                if len(list(token.children)) > 0:
                    item['children'] = [{'child': child, 'pos_': child.pos_, 'dep_': child.dep_,
                                         'tag_': child.tag_, 'head.text': child.head.text,
                                         'head.pos_': child.head.pos_} for child in token.children]
                result.append(item)
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error dependency_child: {0}'.format(e))
        return result

    def sentence_detection(self, text):
        result = []
        try:
            doc = self.analysis_pipe(text)
            result = [sent.string.strip() for sent in doc.sents]
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error sentence_detection: {0}'.format(e))
        return result
    
    def get_chunks(self, text):
        try:
            doc = self.analysis_pipe(text)
            return [chunk.text for chunk in doc.noun_chunks]
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error get_chunks: {0}'.format(e))
            return None

    def syntax_patterns(self, text):
        result = None
        try:
            doc = self.nlp(text)
            dict_noun = {}
            dict_verb = {}
            dict_adv = {}
            dict_adj = {}
            for span in doc.sents:
                result_dependency = self.dependency_all(str(span))
                for item in result_dependency:
                    if item['is_stop'] is not True and item['is_punct'] is not True and item['pos_'] not in 'PRON':
                        if item['pos_'] == 'NOUN':
                            # NOUN
                            chunk = str(item['chunk']).lower()
                            chunk_value = [chunk, item['pos_']]
                            dict_noun[chunk] = chunk_value
                            # Chinking
                            for child in item['children']:
                                if child['pos_'] == 'ADJ':
                                    # ADJ + NOUN
                                    chunk = str(child['child']).lower() + ' ' + str(item['chunk']).lower()
                                    chunk_value = [[str(child['child']).lower(), child['pos_']],
                                                   [str(item['chunk']).lower(), item['pos_']]]
                                    dict_noun[chunk] = chunk_value
                                    dict_adj[chunk] = chunk_value

                                elif child['pos_'] == 'ADP':
                                    # ADP + NOUN
                                    chunk = str(child['child']).lower() + ' ' + str(item['chunk']).lower()
                                    chunk_value = [[str(child['child']).lower(), child['pos_']],
                                                   [str(item['chunk']).lower(), item['pos_']]]
                                    dict_noun[chunk] = chunk_value

                        elif item['pos_'] in ['PRON', 'PROPN']:
                            for child in item['children']:
                                if child['pos_'] == 'NOUN':
                                    # PRON | PROPN + NOUN
                                    chunk = str(item['chunk']).lower() + ' ' + str(child['child']).lower()
                                    chunk_value = [[str(item['chunk']).lower(), item['pos_']],
                                                   [str(child['child']).lower(), child['pos_']]]
                                    dict_noun[chunk] = chunk_value

                        elif item['pos_'] == 'ADJ':
                            # ADJ
                            chunk = str(item['chunk']).lower()
                            chunk_value = [chunk, item['pos_']]
                            dict_adj[chunk] = chunk_value
                            for child in item['children']:
                                if child['pos_'] == 'NOUN':
                                    # ADJ + NOUN
                                    chunk = str(item['chunk']).lower() + ' ' + str(child['child']).lower()
                                    chunk_value = [[str(item['chunk']).lower(), item['pos_']],
                                                   [str(child['child']).lower(), child['pos_']]]
                                    dict_adj[chunk] = chunk_value

                        if item['dep_'] is not ['ROOT']:
                            if item['head_pos'] == 'NOUN':
                                for child in item['children']:
                                    if child['pos_'] == 'ADP':
                                        # NOUN + ADP + NOUN
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(child['child']).lower() + ' ' + \
                                                str(item['chunk']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(child['child']).lower(), child['pos_']],
                                                       [str(item['chunk']).lower(), item['pos_']]]
                                        dict_noun[chunk] = chunk_value

                            elif item['head_pos'] == 'ADJ':
                                for child in item['children']:
                                    if child['pos_'] == 'ADJ':
                                        # ADJ + ADJ + NOUN
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(child['child']).lower() + ' ' + \
                                                str(item['chunk']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(child['child']).lower(), child['pos_']],
                                                       [str(item['chunk']).lower(), item['pos_']]]
                                        dict_noun[chunk] = chunk_value
                                        dict_adj[chunk] = chunk_value

                            elif item['head_pos'] == 'VERB':
                                for child in item['children']:
                                    if child['pos_'] == 'ADJ':
                                        # VERB + NOUN + ADJ
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(item['chunk']).lower() + ' ' + \
                                                str(child['child']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(item['chunk']).lower(), item['pos_']],
                                                       [str(child['child']).lower(), child['pos_']]]
                                        dict_verb[chunk] = chunk_value

                                    elif child['pos_'] == 'ADP':
                                        # VERB + ADP + NOUN
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(child['child']).lower() + ' ' + \
                                                str(item['chunk']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(child['child']).lower(), child['pos_']],
                                                       [str(item['chunk']).lower(), item['pos_']]]
                                        dict_verb[chunk] = chunk_value

                            elif str(item['head_pos']) == 'ADV':
                                for child in item['children']:
                                    if child['pos_'] == 'ADV':
                                        # ADV + ADV + NOUN
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(child['child']).lower() + ' ' + \
                                                str(item['chunk']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(child['child']).lower(), child['pos_']],
                                                       [str(item['chunk']).lower(), item['pos_']]]
                                        dict_adv[chunk] = chunk_value

                                    elif child['pos_'] == 'ADJ':
                                        # ADV + NOUN + ADV
                                        chunk = str(item['head_text']).lower() + ' ' + \
                                                str(item['chunk']).lower() + ' ' + \
                                                str(child['child']).lower()
                                        chunk_value = [[str(item['head_text']).lower(), item['head_pos']],
                                                       [str(item['chunk']).lower(), item['pos_']],
                                                       [str(child['child']).lower(), child['pos_']]]
                                        dict_adv[chunk] = chunk_value

            dict_chunk = {'NOUN': dict_noun, 'VERB': dict_verb, 'ADV': dict_adv, 'ADJ': dict_adj}
            result = dict_chunk
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error syntax_patterns: {0}'.format(e))
        return result

    @staticmethod
    def proper_encoding(text):
        result = None
        try:
            text = unicodedata.normalize('NFD', text)
            text = text.encode('ascii', 'ignore')
            result = text.decode("utf-8")
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error proper_encoding: {0}'.format(e))
        return result

    
    def stopwords(self, text):
        try:
            nlp = Spanish() if self.lang == 'es' else English()
            doc = nlp(text)
            token_list = [token.text for token in doc]
            sentence = []
            for word in token_list:
                lexeme = nlp.vocab[word]
                if not lexeme.is_stop:
                    sentence.append(word)
            return ' '.join(sentence)
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error stopwords: {0}'.format(e))
            return None

    def delete_special_patterns(self, text):
        result = None
        try:
            text = re.sub(r'\©|\×|\⇔|\_|\»|\«|\~|\#|\$|\€|\Â|\�|\¬', ' ', text)# Elimina caracteres especilaes
            text = re.sub(r'\,|\;|\:|\!|\¡|\’|\‘|\”|\“|\"|\'|\`', ' ', text)# Elimina puntuaciones
            text = re.sub(r'\}|\{|\[|\]|\(|\)|\<|\>|\?|\¿|\°|\|', ' ', text)  # Elimina parentesis
            text = re.sub(r'\/|\-|\+|\*|\=|\^|\%|\&|\$', ' ', text)  # Elimina operadores
            result = text.lower()
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error delete_special_patterns: {0}'.format(e))
        return result

    def clean_text(self, text, **kwargs):
        result = None
        try:
            labels = ['EMAIL', 'EMOJI', 'MENTION', 'HASHTAG', 'URL']
            url = kwargs.get('url') if type(kwargs.get('url')) is bool else False
            mention = kwargs.get('mention') if type(kwargs.get('mention')) is bool else False
            emoji = kwargs.get('emoji') if type(kwargs.get('emoji')) is bool else False
            hashtag = kwargs.get('hashtag') if type(kwargs.get('hashtag')) is bool else False
            relabel = kwargs.get('relabel') if type(kwargs.get('relabel')) is bool else False
            stopwords = kwargs.get('stopwords') if type(kwargs.get('stopwords')) is bool else False

            text_out = str(text).lower()
            text_out = re.sub(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', '[EMAIL]', text_out)
            text_out = re.sub("[\U0001f000-\U000e007f]", '[EMOJI]', text_out) if emoji else text_out
            text_out = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                              '[URL]', text_out) if url else text_out
            text_out = re.sub("@([A-Za-z0-9_]{1,40})", '[MENTION]', text_out) if mention else text_out
            text_out = re.sub("#([A-Za-z0-9_]{1,40})", '[HASHTAG]', text_out) if hashtag else text_out
            text_out = re.sub("[0-9]", '', text_out)
            
            if not relabel:
                for label in labels:
                    text_out = re.sub(r'\[' + label + r'\]', ' ', text_out) if mention else text_out

            text_out = self.delete_special_patterns(text_out)
            text_out = self.stopwords(text_out) if stopwords else text_out
            # removing any single letter on a string
            text_out = re.sub(r'((?<=^)|(?<= )).((?=$)|(?= ))', ' ', text_out).strip()
            # condense multiple spaces with a single space
            text_out = re.sub(r'\s+', ' ', text_out).strip()
            text_out = text_out.rstrip()
            result = text_out if text_out != ' ' else None
        except Exception as e:
            Util.standard_error(sys.exc_info())
            print('Error clean_text: {0}'.format(e))
        return result

