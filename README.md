# Inodevs-back-machine-learning

# Local Installation Guide
To run all this project you need to install the python 3.8, because of the libraries (may need to update your pip to last version).
## Tools:
- [Python](https://www.python.org/downloads/)
- [Jupiter Notebook](https://www.anaconda.com/download)
  
## Local installation manual with virtual environment:
1. In the main folder, run these commands:

```console
pip install virtualenv
```
```console
python -m venv env
```
```console
.\env\Scripts\activate.bat
```
```console
pip install -r requirements.txt
```
```console
cd machine_learning
```
```console
python manage.py runserver
```

## Local installation manual without virtual environment:
1. Run this command in the main folder:
```console
pip install -r requirements.txt
```
```console
cd machine_learning
```
```console
python manage.py runserver
```
