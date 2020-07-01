# pymedext_public
Based on the work of Antoine Neuraz !

wrapper around Pymedext 2 examples:

## Annotation of a file

```bash
cd src
python3 main_regex.py -i ../data/regexdemo.txt -o ../output 

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

```
