import hashlib
import sys
import os
import os.path
import datetime
import unicodedata
from datetime import datetime


class Util(object):
    """
    :Date: 2019-10-03
    :Version: 0.1
    :Author: Gabriel Moreno & Edwin Puertas - Pontificia Universidad Javeriana, Bogotá
    :Copyright: To be defined
    :Organization: Centro de Excelencia y Apropiación de Big Data y Data Analytics - CAOBA
    This class has static methods
    """
    def __init__(self):
        print("Class Utils")

    @staticmethod
    def sha1(text):
        result = hashlib.sha1((text + str(datetime.datetime.now())).encode())
        return result.hexdigest()

    @staticmethod
    def proper_encoding(text):
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return text

    @staticmethod
    def walklevel(some_dir, level=1):
        some_dir = some_dir.rstrip(os.path.sep)
        assert os.path.isdir(some_dir)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    @staticmethod
    def standard_error(error_data):
        try:
            exc_type, exc_obj, exc_tb = error_data
            return \
                'ERROR: ' + exc_type.__name__ + ': ' + str(exc_obj) + '\nFILE: ' + exc_tb.tb_frame.f_code.co_filename + \
                '\nMETHOD: ' + exc_tb.tb_frame.f_code.co_name + \
                '\nLINE: ' + str(exc_tb.tb_lineno) + \
                '\n------------------------------------------------------------------------'
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return \
                'ERROR: ' + exc_type.__name__ + ': ' + str(exc_obj) + '\nFILE: ' + exc_tb.tb_frame.f_code.co_filename + \
                '\nMETHOD: ' + exc_tb.tb_frame.f_code.co_name + \
                '\nLINE: ' + str(exc_tb.tb_lineno) + \
                '\n------------------------------------------------------------------------'
