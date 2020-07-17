#!/usr/bin/env python3

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

reqs = ["nltk==3.4.5","spacy","rdflib>=4.2.2"]

setup(name='pymedext',
      version='0.1',
      description='pymedext core toolkit for clinical NLP',
      packages=['pymedext'],
      install_requires=reqs,
      author='Antoine Neuraz, William Digan, Ivan Lerner, Alice Rogier, David Baudoin, Anita Burgun, Nicolas Garcelon, Bastien Rance ',
      author_email='william.digan@aphp.fr',
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False)
