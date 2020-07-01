#!/usr/bin/env python3

from pymedext.annotators import Annotator, Annotation,regexFast
from pymedext.document import Document
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s -- %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
from os import path

import requests
import json
import argparse
import time
import os
def writeJson(dataObject,pathToOutput):
    with open(pathToOutput, 'w', encoding='utf-8') as f:
        json.dump(dataObject, f, ensure_ascii=False, indent=4)


def readJsonConfig(pathToconfig):
    with open(pathToconfig) as f:
        config_json = json.load(f)
    return(config_json)



if __name__ == "__main__":
    example_text = '''example:

     python test.py -i template/test.py
     python test.py -i template/test -c conf/test.conf
     python test.py -i test.py'''
    parser = argparse.ArgumentParser(prog='diso_search',
                                     description='template maker',
                                     epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', '--inputFile', help='path to input folder', type=str)
    # parser.add_argument('-s', '--source', help='if set, switch to english rxnorm sources, if not french  romedi source' ,action="store_true" )
    parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()
    logger.debug(args.inputFile)
    fileName=""
    rawFileName=""
    if args.inputFile.endswith(".json"):
        fileName=args.inputFile.split("/")[-1].replace(".json","_regexcovid.json")
        rawFileName=args.inputFile.split("/")[-1].replace(".json","")
    else:
       rawFileName=args.inputFile.split("/")[-1]
       fileName=args.inputFile.split("/")[-1].replace(".txt","_regexcovid.json")
    if path.exists (args.inputFile):
        logger.debug("ok")
    else :
        logger.debug("nnok")
        exit()

    pathTofile =args.inputFile
    resourcePath=os.getcwd().replace("src","resources/")
    thisFile=open(pathTofile,"r").read()
    thisDoc=Document(raw_text=thisFile, ID=pathTofile)
    getdrugs = regexFast(key_input = ['raw_text'],
                         key_output = 'regex_fast',
                         ID = "regex_fast.v1",
                         regexResource=resourcePath+"regexResource.txt ",
                         pathToPivot=resourcePath+"pivotResource.csv"
                         )

    pipeline = [getdrugs]
    thisDoc.annotate(pipeline)
    print(thisDoc.to_dict())
    # thisDoc.writeJson(fileName)
