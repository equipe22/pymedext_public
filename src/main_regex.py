#!/usr/bin/env python3

from pymedext.annotators import Annotator, Annotation,regexFast
from pymedext.annotators import PreprocessText, SentenceTokenizer, RomediCatcher, DoseCatcher
from pyromedi.romedi import Romedi

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

     python main_regex.py -i ../data/regex_demo.txt -o ../output/
     python main_regex.py -i test.py'''
    parser = argparse.ArgumentParser(prog='pymedext',
                                     description='main_regex demo',
                                     epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', '--inputFile', help='path to input folder', type=str)
    parser.add_argument('-o', '--output', help='path to output folder', type=str, default="")

    # parser.add_argument('-s', '--source', help='if set, switch to english rxnorm sources, if not french  romedi source' ,action="store_true" )
    parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()
    logger.debug(args.inputFile)
    fileName=""
    rawFileName=""
    if args.inputFile.endswith(".json"):
        fileName=args.inputFile.split("/")[-1].replace(".json","_regex.json")
        rawFileName=args.inputFile.split("/")[-1].replace(".json","")
    else:
       rawFileName=args.inputFile.split("/")[-1]
       fileName=args.inputFile.split("/")[-1].replace(".txt","_regex.json")
    if path.exists (args.inputFile):
        logger.debug("ok")
    else :
        logger.debug("nnok")
        exit()
    outputFolder = args.output
    if not outputFolder.endswith("/"):
        outputFolder = outputFolder+"/"

    pathTofile =args.inputFile
    resourcePath=os.getcwd().replace("src","resources/")
    # Preprocess of Romedi (should be done once)
    logger.info("Preprocess of Romedi (should be done once)" )
    romedi_ttl_file = "pyromedi/data/Romedi2-2-0.ttl"
    romedi_cache = 'cache_Romedi2-2-0.p'
    romedi = Romedi(romedi_ttl_file, from_cache = None)
    romedi.save(romedi_cache)
    #done
    logger.info("load input data")
    thisFile=open(pathTofile,"r").read()
    thisDoc=Document(raw_text=thisFile, ID=pathTofile)
    logger.info("Define annotators")
    getRegex = regexFast(key_input = ['raw_text'],
                         key_output = 'regex_fast',
                         ID = "regex_fast.v1",
                         regexResource=resourcePath+"regexResource.txt ",
                         pathToPivot=resourcePath+"pivotResource.csv"
                         )
    preprocessor = PreprocessText(["raw_text"], "preprocessed_text", 'ProprocessText.v1')

    sent_tokenizer = SentenceTokenizer( key_input = ['preprocessed_text'],
                                       key_output = "sentence",
                                       ID = "SentenceTokenizer.v1",
                                       language= 'french')

    romedi_catcher = RomediCatcher( key_input = ['sentence'],
                                       key_output = "drug",
                                      romedi_cache_path=romedi_cache,
                                      clean_FUN=preprocessor.clean_text,
                                      remove_accents = True,
                                       ID = "RomediCatcher.v1")

    dose_catcher = DoseCatcher(key_input = ['drug','sentence'],
                                       key_output = "dose",
                                      remove_accents = True,
                                       ignore_case=True,
                                       ID = "DoseCatcher.v1")
    logger.info("annotate document")
    annotators = [preprocessor, sent_tokenizer, romedi_catcher, dose_catcher, getRegex]
    thisDoc.annotate(annotators)
    logger.info(thisDoc.to_dict())
    thisDoc.writeJson(outputFolder+fileName)
