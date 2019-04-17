# Welcome to Good Place Platform!

This platform becomes the core of multiple others. A CRM core for other kind of apps.

## Requirements

* Python 3
* Mysql
Sorry, more detailed requirements are yet to come.

## Installation
These are instructions for development installation. You can also deploy it using Docker, or Vagrant. See more on the [Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux)

### Install requirements
`$ pip install -r requirements.txt`

Update requirements:
`$ pip freeze > requirements.txt`

### Environment configuration
Generate an`.env` file, see `example.env` file.

### App configuration
See `config.py`file for database and other configurations

## Database migrations
To initialize the database, just `$ flask db upgrade`.

## Translations
For updating translations you have to  `$ flask translate update` and then edit the `.po` file with PoEdit or similar software.
Once completed, `$ flask translate compile` to generate the `.mo` file.

For now, only Spanish translation is available. You can use `$ flask translate init <language-code>` to install a new language.

### live transactions
You may have a Google azure translator API and setup in config file.

# Run App
First: Activate environment with `$ source venv/bin/activate`.
Then: Use command `$ flask run`.
For testing `$ flask shell`.

--

**NOTE**: This is a development made from the example application featured in [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).
