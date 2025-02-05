# FROM python:3.7.2-slim
FROM pymedext-core:v0.0.1
# need pymedext-core
# HEGP NECKER
#special variables to define in order to process
#and generate the provenance of the script

MAINTAINER william.digan@aphp.fr
ENV containerName='pymedext-ehr'
ENV inputData=folder
ENV typeSearch="store data to OMOP"
ENV output="stdout"
ENV command="python3 /home/src/omop_prod_norm_graph.py -i $input"
ENV whenConditions=""
ENV metaParameters=""
ENV lowerText="True"
ENV treatFolder="True"
ENV sources="{'romedi':'','rxnorm':'-s'}"

WORKDIR /home
RUN mkdir pubsrc
COPY src pubsrc/
RUN pip3 install git+https://github.com/equipe22/pymedext_public.git

# RUN pip3 install -r /home/pubsrc/pymedext/requirements.txt
# RUN pip3 install -r /home/pubsrc/pyromedi/requirements.txt

# RUN pip3 install SPARQLWrapper
# ADD ressources/ /home/src/ressources/
# COPY lower_output.RRF src/
WORKDIR /home/data
COPY bin/installstopword.py .
RUN python3 installstopword.py

# RUN apt-get update && apt-get install -y --allow-unauthenticated procps
CMD ["python3", "/home/src/omop_prod_norm_graph.py ","--inputFolder","$input"]
