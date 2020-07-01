import uuid
import re
from nltk.tokenize import sent_tokenize
import json
from flashtext import KeywordProcessor
import unidecode
from pyromedi.romedi import Romedi
from subprocess import Popen, PIPE
from os import path
import logging
logger = logging.getLogger(__name__)






class Annotation:
    
    def __init__(self, type, value, source, source_ID, span = None, attributes = None, isEntity=False, ID = str(uuid.uuid1())):
        self.value = value
        self.type = type
        self.source = source
        self.span = span
        self.source_ID = source_ID
        self.attributes = attributes
        self.ID = ID
        self.isEntity = isEntity

        
    def to_json(self): 
        return json.dump(self.to_dict())
    
    def to_dict(self):
        return {'type':self.type,
               'value':self.value,
               'span':self.span,
               'source':self.source,
               'source_ID': self.source_ID,
               'isEntity': self.isEntity,
               'attributes': self.attributes,
               'id':self.ID}

class Annotator: 
    def __init__(self, key_input, key_output, ID):
        self.key_input = key_input # list
        self.key_output = key_output # str
        self.ID = ID
        
    def get_first_key_input(self,_input): 
        return  self.get_key_input(_input, 0)
    
    def get_all_key_input(self,_input): 
        return [x for x in _input.annotations if x.type in self.key_input]
    
    def get_key_input(self, _input, i):
        return [x for x in _input.annotations if x.type == self.key_input[i]]
    
    

class regexFast(Annotator):
    """
    Annotator based on linux grep to search regext from a source file
    """
    def __init__(self, key_input, key_output, ID, regexResource, pathToPivot, ignore_syntax=False):
        """FIXME! initialize the annotator

        :param key_input: input [raw_text']
        :param key_output: either regex_fast or the normalized regex value need to discuss
        :param ID: regex_fast.version
        :param regexResource: path to regex value file
        :param pathToPivot: pivot table between regex and the normalized value
        :param ignore_syntax: not used yet
        :returns:
        :rtype:

        """
        super().__init__(key_input, key_output, ID)
        self.ignore_syntax=ignore_syntax
        self.fileAnnotation=None
        self.countValue=None
        self.pathToPivot=pathToPivot
        self.pivot=dict()
        self.cmds=["fgrep -iow -n -b -F -f "+regexResource]
        self.loadPivot()

    def annotate_function(self, _input):
        """ main annotation function
        :param _input: in this case raw_text
        :returns: a list of annotations
        :rtype:
        """
        logger.debug(_input)
        inp = self.get_key_input(_input,0)[0]
        fileAnnotation,countValue=self.makeMatch(inp.source_ID)
        countValue=self.setPivot(countValue)
        logger.debug(countValue)
        annotations=[]
        for matchPos in list(fileAnnotation.keys()):
            for drug in fileAnnotation[matchPos]:
                ID = str(uuid.uuid1())
                attributes={"ngram":drug}
                annotations.append(Annotation(type= self.key_output,
                                              value=countValue[drug]["normalized"], #drug,
                                              span=(int(matchPos), int(matchPos)+len(drug)),
                                              source=self.ID,
                                              isEntity=True,
                                              ID=ID,
                                              attributes=attributes,
                                              source_ID = inp.ID))
        return(annotations)


    def loadPivot(self):
        """This function load the pivot table to normalized the value

        :returns:  pivot table
        :rtype:  dictonnary

        """
        with open(self.pathToPivot,'r') as f:
            for line in f:
                record=line.rstrip().split(",")
                if record[0] not in self.pivot.keys():
                    self.pivot[record[0]] = record[-1]


    def makeMatch(self, inputFileName):
        """ wrapper aroung grep to search words match
        :param inputFileName: file name
        :returns:   matches
        :rtype:  dict

        """
        fileAnnotation = dict()
        countValue = dict()
        logger.debug(inputFileName)
        for cmd in self.cmds:
            p = Popen((cmd+" "+inputFileName).split() ,stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            logger.debug(out)
            logger.debug(err)
            for line in out.decode("utf-8").split("\n"):
                thisRecord = line.split(":")
                if len(thisRecord) ==3:
                    logger.debug(thisRecord)
                    if thisRecord[1] not in fileAnnotation.keys():
                        fileAnnotation[thisRecord[1]] = dict()
                        fileAnnotation[thisRecord[1]]= [thisRecord[2]]
                    else:
                        fileAnnotation[thisRecord[1]].append(thisRecord[2])
                    if thisRecord[2] not in countValue.keys():
                        countValue[thisRecord[2]] = {"count":1 ,"normalized":"" }
                    else:
                        countValue[thisRecord[2]]["count"]+=1
        return(fileAnnotation,countValue)

    def setPivot(self, countValue):
        """ associated match to the mnormalized value
        :param countValue: dictonnary of match
        :returns: dictionnary with matches
        :rtype: dict

        """
        thisMatch = list(countValue.keys())
        for acall in thisMatch:
            if acall.lower() in self.pivot.keys():
                countValue[acall]["normalized"]=self.pivot[acall.lower()]
        return(countValue)

      
class PreprocessText(Annotator): 
    
    def annotate_function(self, _input): 
        inp = self.get_first_key_input(_input)[0]
        
        clean = self.clean_text(inp.value)
        
        return [Annotation(type=self.key_output, 
                         value = clean, 
                         span = (0, len(clean)),
                         source_ID = inp.ID,
                         source= self.ID)]
    @staticmethod
    def clean_text(text): 
        space_strip_punctuation = re.compile("([!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~])+")
        replace_decimal_points = re.compile("(?<=[0-9]) \. (?=[0-9])")

        clean = text
        clean = space_strip_punctuation.sub( r' \1 ', text)
        clean = replace_decimal_points.sub(r" , ",clean)
        clean = re.sub(r"(\s)+", r"\1", clean)
        return clean
        
    
class SentenceTokenizer(Annotator): 
    
    def __init__(self, key_input, key_output, ID, language):
        self.language = language
        super().__init__(key_input, key_output, ID)
    
    def annotate_function(self, _input):
        #inp = getattr(_input, self.key_input[0])
        inp = self.get_first_key_input(_input)[0]
        
        sentences = []
        for row in inp.value.split('\n'):  
            sentences += sent_tokenize(row, language = self.language)

        res = []
        
        for sent in sentences: 
            start = inp.value.find(sent)
            end = start + len(sent)
            res.append(Annotation(type=self.key_output,
                                 value=sent,
                                 span=(start, end),
                                 source=self.ID,
                                 source_ID = inp.ID))
        return res
        
    
class DictionaryCatcher(Annotator):
    def __init__(self, key_input, key_output, ID, dictionary, clean_FUN = None, case_sensitive=False, remove_accents=True ):
        super().__init__(key_input, key_output, ID)
        self.dictionary = dictionary
        self.remove_accents = remove_accents
        self.case_sensitive=case_sensitive
        self.clean_FUN = clean_FUN
        if clean_FUN is not None: 
            self.dictionary = self.clean_dict()
            
        self.keyword_processor = KeywordProcessor(case_sensitive = self.case_sensitive)
        self.keyword_processor.add_keywords_from_dict(self.dictionary)
        
    def annotate_function(self, _input): 
        
        inp = self.get_all_key_input(_input)
        
        res = []
        for sent in inp: 
            if self.remove_accents: 
                sent.value = unidecode.unidecode(sent.value)
            
            catch = self.keyword_processor.extract_keywords(sent.value, span_info = True)
            if len(catch) > 0:
                for ann in catch:
                    
                    res.append(Annotation(type=self.key_output, 
                                         value=ann[0],
                                         span=(ann[1],ann[2]),
                                         source = self.ID,
                                         source_ID = sent.ID))
        return res

    def clean_dict(self): 
        res = {}
        for k,v in self.dictionary.items():
            res[k] = [self.clean_FUN(x) for x in v]
        return res
    
   
    
class RomediCatcher(DictionaryCatcher):
    def __init__(self, key_input, key_output, ID, 
                 romedi_cache_path, clean_FUN = None, 
                 case_sensitive=False, remove_accents=True ):
        
        self.romedi = Romedi(from_cache=romedi_cache_path)
        dictionary = self.generate_dictionary()
        
        super().__init__(key_input, 
                         key_output, 
                         ID, 
                         dictionary, 
                         clean_FUN = clean_FUN, 
                         case_sensitive=case_sensitive, 
                         remove_accents=remove_accents)
        
    
    def generate_dictionary(self): 
            dic = {}
            for i in range(len(self.romedi.infos)): 
                info = self.romedi.infos[i]               
                n_BN_labels = len(info['BN_label'])

                for y in range(n_BN_labels):                     
                    BN_label = info['BN_label'][y]                   
                    
                    if BN_label not in dic.keys():
                        dic[BN_label] = [BN_label]

                n_IN_labels = len(info['IN_label'])
                n_hidden_labels = len(info['IN_hidden_label'])
                
                for y in range(n_IN_labels):                    
                    IN_label = info['IN_label'][y]
                    IN_hidden_label = None
                    
                    if n_hidden_labels >= y+1:
                        IN_hidden_label = info['IN_hidden_label'][y]
                    
                    if IN_label not in dic.keys():
                        dic[IN_label] = [IN_label]
    
                        if IN_hidden_label is not None:
                            dic[IN_label] += [IN_hidden_label]          
            return dic
        
        
class RegexCatcher(Annotator): 
    """
    key_input: 1st Drug, 2nd Sentence
    """
    def __init__(self, key_input, key_output, ID, case_sensitive=False, remove_accents=True ):
        super().__init__(key_input, key_output, ID)
        self.remove_accents = remove_accents
        self.case_sensitive=case_sensitive
        
    def annotate_function(self, _input):
        pass
    
        
        
class DoseCatcher(RegexCatcher):
    """
    key_input: 1st Drug, 2nd Sentence
    """
    
    def __init__(self, key_input, key_output, ID, ignore_case=True, remove_accents=True ):
        super().__init__(key_input, key_output, ID)
        self.remove_accents = remove_accents
        self.ignore_case=ignore_case
        
        self.units = self.define_units()
        self.multiplier = self.define_multiplier()
        self.litteral = self.define_literal()
        self.decimal = self.define_decimal()
        self.number = self.define_number()
        self.number_unit = self.define_number_unit
        
        self.catch_number_unit = self.compose_dose_regex(self.define_number_unit)
        
    def annotate_function(self, _input):
        sentences = self.get_key_input(_input, 0)
        
        for sentence in sentences: 
            self.match_regex()
    
    
    def annotate_function(self, _input):
        drugs = self.get_key_input(_input, 0)
        sentences = self.get_key_input(_input, 1)
        
        res = []
        
        for drug in drugs:
        
            drug_span = drug.span
            source_ID = drug.source_ID
            #logger.debug(drugs[i].value)

            sent = [x for x in sentences if x.ID == source_ID][0]
            drug_mention = sent.value[drug_span[0]:drug_span[1]]

            regex = self.catch_number_unit(drug_mention)
            #logger.debug(drug_mention)
            #logger.debug(regex)
            #logger.debug(sent.value)
            
            matches = self.match_regex(regex, sent.value)
            
            if len(matches) > 0:
                for match in matches: 
                    res.append(Annotation(type=self.key_output, 
                                             value=match[0],
                                             span=match[1],
                                             source = self.ID,
                                             source_ID = sent.ID, 
                                             target_ID = drug.ID))
        return res
        
    
    @staticmethod
    def define_units():
    
        units_patterns = [r"(dose)s?",
               r"(?:ampoule)s?",
               r"bolus",
               r"amp",
               r"mesures*",
               r"gelules*",
               r"gell(?:ul)?es?",
               r"gel",
               r"applications*",
               r"tubes*",
               r"dosettes*",
               r"gouttes*",
               r"sachets*",
               r"gouttes",
               r"unites",
               r"gamma",
               r"gui",
               r"gu",
               r"gbq",
               r"bq",
               r"mol",
               r"l",
               r"ui",
               r"g",
               r"u",
               r"%",
               r"dose(?:s)? ?(?: |\/|\-)? ?(?:poids?|kilos?|kg)",
               r"doses*",
               r"cp",
               r"cpr",
               r"comprimes*",
               r"comp",
               r"injections*",
               r"bouffee?s?",
               r"a.?rosols?",
               r"cuilleres? a? ?cafe",
               r"c\\.?a\\.? ?c\\.?a?f?e?"
              ]
        units_patterns.sort(key=len,reverse = True)
        units_patterns = "|".join(units_patterns)
        units = r"[mµpn]?(?:"+units_patterns+r")(?: ?\/ ?(?:[md]?l|min|h|m²|m2|kg|kilo))?"
        
        return units
    
    @staticmethod
    def define_literal():
        return r"un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix"
    
    @staticmethod
    def define_decimal(): 
        return r"[0-9]{1,7}(?: [,.] [0-9]{1,3})?"
    
    @staticmethod
    def define_multiplier():
        return r'(?:([0-9]x) ?)'
    
    def define_number(self):
        return self.decimal + r'|' + self.litteral

    def define_number_unit(self):
        return r"\b("+ self.multiplier +r"?(" + self.number + r"?) ?(" + self.units + r"))"

    def define_combo_number_unit(self):
        return r"\b(" + self.number + r") ?(?:(" + self.units + r")?)? \/ (" + self.number + r") ?(?:(" + self.units + r")?)?"
    
    def compose_dose_regex(self, FUN):
        def fun(drug): 
            return r"(?<=" + drug + r") ?" + FUN() 
            #return r"(?<=" + drug + r") ?\b((" + self.number + r") ?(?:(" + self.units + r")?)?(?: ?\/ ?("+self.number+r"))? ?(?:("+self.units+r")?)?)"
        return fun
    
    def match_regex(self, regex, txt): 
        res = []
        i = None
        if self.ignore_case:
            i = re.IGNORECASE
        for match in re.finditer( regex , txt, i):
            res.append((match.groups()[0], match.span()))
        return res
