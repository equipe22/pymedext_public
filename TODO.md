# Data wrangling
* Summary
** data wrangling
how the data are transformed, from document
to other format type
** data source
how to send data into a a database, just the
communication with a database
** data connector
just the basic connector type ssh, api, database

* general recommendations
- [ ] use logger instead of print
- [ ] comments
- [ ] UML schema of the code

* Data wrangling [0%]
- [-] add doccano
- [ ] add Brat
- [ ] BioC
- [ ] COnnL
- [ ] FhiR
- [ ] universal dependencies
- [ ] BioNLP

* data source [20%]
 - [ ] Source  abstract class factorize
 - [X] OmopSource with optimize load function
 - [ ] FhirSource APIconnection to FhiR
 - [ ] doccanoSource APIConnection to doccano api
 - [ ] bratSource SSHconnection send data to server

* data connector [28%]
- [ ] factorize the code better connection between each class
- [ ] Connector general and abstract class
- [ ] ApiConnector factorize doccano code
- [ ] DatabaseConnector factorize
- [ ] sshConnector within paramiko
- [X] POstgreConnector
- [X] CxOracleConnector (done but not provided)
