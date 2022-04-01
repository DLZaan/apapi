# APAPI

**APAPI** is a library that allows you to connect to Anaplan API v2 (Bulk, and soon Transactional) using Python. 
Here we export some CSV and import it back to Anaplan:
```python
>>> import apapi
>>> my_connection = apapi.Connection(f"{email}:{password}")
>>> my_connection.run_export(workspace_id, model_id, export_id)
>>> data = my_connection.download_data(workspace_id, model_id, export_id)
>>> print(data.decode())
Versions,Data,Text
Actual,1,test
Budget,2.5,ąćęłńśżź
Forecast,-3,😂
>>> my_connection.upload_data(workspace_id, model_id, file_id, data)
>>> my_connection.run_import(workspace_id, model_id, import_id)
```
Check [tests/test_connection.py](tests/test_connection.py) for more examples and hints about usage.

## Installing Anaplan Python API and Supported Versions

APAPI is available on PyPI:
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