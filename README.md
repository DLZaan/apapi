# APAPI

**APAPI** is an unofficial library that allows you to connect to Anaplan APIs using
Python. Currently, you can authenticate using either Basic Authentication
(email & password), or OAuth2 (client_id & refresh_token, both non-rotatable and 
rotatable) - Cert based authentication is on the roadmap.
Use Bulk, Transactional, ALM and Audit endpoints, with more coming soon!

As an abstract example, here we export some CSV and import it back to Anaplan:

```python
>> > import apapi
>> > with apapi.BasicAuth(f"{email}:{password}") as authentication:
    >> > my_connection = apapi.BulkConnection(authentication)
>> > my_connection.run_export(model_id, export_id)
>> > data = my_connection.get_file(model_id, export_id)
>> > print(data.decode())
Versions, Data, Text
Actual, 1, test
Budget, 2.5, ąćęłńśżź
Forecast, -3,😂
>> > my_connection.put_file(model_id, file_id, data)
>> > my_connection.run_import(model_id, import_id)
```
Full documentation can be found [here](https://dlzaan.github.io/apapi/apapi.html).
Check [examples](https://github.com/DLZaan/apapi/tree/master/examples)
or [tests](https://github.com/DLZaan/apapi/tree/master/tests)
for more examples and hints about usage.

## Installing Anaplan Python API and Supported Versions

APAPI is available on [PyPI](https://pypi.org/project/apapi/):
```console
$ python -m pip install apapi
```
APAPI supports Python 3.8+.

## More Info
- [Official Anaplan APIs Postman Collection](https://www.postman.com/apiplan/workspace/official-anaplan-collection/overview)
- [Official documentation of Anaplan APIs](https://help.anaplan.com/da432e9b-24dd-4884-a70e-a3e409201e5c-Anaplan-API)
- [Official documentation of Anaplan Connect V4 (Java)](https://anaplanenablement.s3.amazonaws.com/Community/Anapedia/Anaplan-Connector-Informatica-V.4.2.1.pdf)
- [Official Anaplan Connect repository](https://github.com/anaplaninc/anaplan-java-client)

## How to Contribute

Contributions are welcome, even if you can't code it - in such case, please submit 
an issue if you need any additional feature (preferably in the form of User Story, 
like *"As {who} I need {what} because {why}"*).
If you encounter any bugs, please report the problem with a description and error log.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apapi)
[![PyPI - License](https://img.shields.io/pypi/l/apapi)](https://github.com/DLZaan/apapi/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)