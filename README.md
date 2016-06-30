# Phenopacket-Scraper Api

REST API for phenopacket-scraper

##Setup:

To get the project's source code, clone the github repository:

    $ git clone https://github.com/monarch-initiative/phenopacket-scraper-api.git

Install VirtualEnv using the following:

    $ [sudo] pip install virtualenv

Create and activate your virtual environment:

    $ virtualenv venv
    $ source venv/bin/activate

Install all the required packages:

	$ venv/bin/pip install -r requirements.txt

Create your database and the superuser by running this from the `phenopacketscraper/` directory of the repository:

	$ python manage.py migrate
	$ python manage.py createsuperuser


##Usage

To run the server enter the following in the root directory of phenopacketscraper

	$ python manage.py runserver

Now you can go to your browser and test the api using:

	http://localhost:8000/api/test/

To scrape data from a url you can enter the following in your browser:

	http://localhost:8000/api/scrape/?url=[url]

To annotate data from a url you can enter the following in your browser:

	http://localhost:8000/api/annotate/?url=[url]



Or by using curl in your terminal. For annotation you can enter the following

	$ curl -H 'Accept: application/json; indent=4' http://localhost:8000/api/annotate/?url=[url]

For instance you can use `http://molecularcasestudies.cshlp.org/content/2/2/a000703.abstract` in place of [url] for testing.


