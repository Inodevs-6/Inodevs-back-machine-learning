# To run all this project you need to install the python 3.8, because of the libraries and may need to update your pip to last version.

# If you just want to run without a virtual enviroment for the python libraries, you can jus do the following commands on the main folder:
```
  pip install -r requirements.txt
```
### This will install all the libraries in your machine to run the code.

# Now if you want to configure one virtual enviroment for the python libraries, run the following commands:
```
  pip install virtualenv

  python -m venv env

  .\env\Scripts\activate.bat

  cd ../..

  pip install -r requirements.txt
```

### To run the code you have to click "Run" in the cell of Jupyter Notebook that I created.

# The scrap code is a little different because the libraries that we will use are to make the requests and modify the body of the html page as an object.

## This code will make the scraping and save the results in the folder csv with the name 'scrap.csv' with all the candidates toke from the page that we did the request.

# Have Fun :)
