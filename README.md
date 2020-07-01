# pymedext_public
Based on the work of Antoine Neuraz !

wrapper around Pymedext 2 examples:

## Annotation of a file

```bash
cd src
python3 main_regex.py -i ../data/regexdemo.txt -o ../output 

```

will annotate a file and store a results in the output folder. if not specify. Data will be output in the current directory

# Pymedext to Omop
```bash
cd src
python3 omop_prod_norm_graph.py  -i ../output 


```

take the annotation store in a folder and transform the data to the  HEGP omop format
the connection to an omop database will be shown in another git project


# Makefile

```bash
make help
annote                          run annotation with main_regex
build                          Build dinstance
demo                            start a demo pymdext container to run it
help                           Display available commands in Makefile
omop                            transform annotation to omop data
```
