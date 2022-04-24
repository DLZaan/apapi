# APAPI

**APAPI** is an unofficial library that allows you to connect to Anaplan API v2 (Bulk and Transactional) using Python. 
Here we export some CSV and import it back to Anaplan:
```python
>>> import apapi
>>> with apapi.Connection(f"{email}:{password}") as my_connection:
>>>     my_connection.run_export(model_id, export_id)
>>>     data = my_connection.download_file(model_id, export_id)
>>>     print(data.decode())
Versions,Data,Text
Actual,1,test
Budget,2.5,ąćęłńśżź
Forecast,-3,😂
>>>     my_connection.upload_file(model_id, file_id, data)
>>>     my_connection.run_import(model_id, import_id)
```
Check [tests/test_connection.py](tests/test_connection.py) for more examples and hints about usage.

## Installing Anaplan Python API and Supported Versions

APAPI is available on [PyPI](https://pypi.org/project/apapi/):
```console
$ python -m pip install apapi
```
APAPI supports Python 3.9+.

## More Info
- [Official documentation of Anaplan Integration API V2](https://anaplanbulkapi20.docs.apiary.io)
- [Official documentation of Anaplan Connect V3 (Java)](https://anaplanenablement.s3.amazonaws.com/Community/Anapedia/Anaplan_Connect_User_Guide_v3.0.0.pdf)
- [Official Anaplan Connect repository](https://github.com/anaplaninc/anaplan-java-client)

## How to Contribute

Contributions are welcome, even if you can't code it - in such case, please submit an issue if you need any additional feature (preferably in the form of User Story, like _"As {who} I need {what} because {why}"_).
If you encounter any bugs, please report the problem with a description and error log.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apapi)
![PyPI - License](https://img.shields.io/pypi/l/apapi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)