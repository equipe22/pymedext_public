# pymedext_public

wrapper around Pymedext 2 examples:

## Annotation of a file

```bash
cd src
python3 main_regex_v0.0.1.py -i ../data/regexdemo.txt -o ../output 

```

will annotate a file and store a results in the output folder. if not specify. Data will be output in the current directory

# Pymedext to Omop pandas dataframe
```bash
cd src
python3 pymedext_to_omop.py  -i ../output 



```

take the annotation store in a folder and transform the data to the  HEGP omop format
# Pymedext to Omop DB
```bash
cd src
python3 pymedext_to_omopdb.py  -i ../output 



```


the connection tothe HEGP omop database. need access 	https://github.com/equipe22/pymedext_omop 

# Makefile

```bash

make help
annote                         run annotation with main_regex
build                          Build dinstance
demo                           start a demo pymdext container to run it
help                           Display available commands in Makefile
omopdb                         WARNING load data to omopdb. Need to be in the docker ( make demo)
omop                            transform annotation to omop data
install                        local install of pymedext packages
uninstall                      uninstall local pymedext packages

```

# Add Annotators
if you want to expand pymedext and add a new annotator you will have to 

```python 
#from core import annotators
from pymedext_core import annotators

# Implement a new class which extend annotators.Annotator
class PreprocessText(annotators.Annotator):
# you need to implement the function annotate_function and
# return a list of annotors.Annotation object
    def annotate_function(self, _input): 
        inp = self.get_first_key_input(_input)[0]
        
        clean = self.clean_text(inp.value)
        
        return [annotators.Annotation(type=self.key_output,
                         value = clean, 
                         span = (0, len(clean)),
                         source_ID = inp.ID,
                         source= self.ID)]



```
in the pymedtator.py script add your annotators to the list

```python

from .annotators import regexFast, PreprocessText, SentenceTokenizer, DictionaryCatcher, RomediCatcher, DoseCatcher
from .romedi import Romedi


```

# Use pymedext in a py script

``` python
#import dependencies
from pymedext import pymedtator # contains your annotators
from pymedext_core import pymedext # contains Document and other pymed connector object

thisDoc=pymedext.Document(raw_text= " a document demo you want to work with"
, ID="your doc id")

#define your annotator
preprocessor = pymedtator.PreprocessText(["raw_text"], "preprocessed_text", 'ProprocessText.v1')

# add all your annotators in a list
annotators =[preprocessor]
# annotate your document
thisDoc.annotate(annotators)

#write your annotation in pymedext json
thisDoc.writeJson("outputfile.txt")


```
