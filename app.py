# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 18:38:02 2022

@author: yoonseok
"""

from Dart_Scraper import Dart_Scraper
from os import chdir

chdir(r"C:\results")    
Dart_Scraper("A001", 1, 20220530, 20220612, delay=3)
