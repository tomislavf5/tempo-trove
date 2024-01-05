# tempo-trove
Similarity-based recommender system for music.
Music metadata (.csv file) downloaded from [Kaggle](https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs)
Downloaded file needs to be manually added to the _db_ directory because it's too large to be committed (.gitignore ensures it stays uncommitted)

## Tech stack
* [MongoDB](https://www.mongodb.com/)
* [Docker](https://www.docker.com/)
* [Python ](https://www.python.org/) ([FastAPI](https://fastapi.tiangolo.com/), [scikit-learn](https://scikit-learn.org/stable/), [Uvicorn](https://www.uvicorn.org/), [pandas](https://pandas.pydata.org/))
* [React](https://react.dev/) / [Vite](https://vitejs.dev/) / [Tailwind](https://tailwindcss.com/)

## Prerequisites
* [Python](https://www.python.org/downloads/) 
    * version 3.11.6 used
    * `python --version` -> to confirm the installation, and check the installed version

* [Node.js](https://nodejs.dev/en/download/)
    * version 18.14.2 used
    * `node -v` -> to confirm the installation, and check the installed version
    * Run `pip install fastapi scikit-learn uvicorn pandas` to install the necessary Python modules.

* Yarn
    * version 1.22.19 used
    * Once Node.js is installed, install yarn using the following command: `npm install --global yarn`

    * `yarn --version` -> to confirm the installation, and check the installed version

* [Docker](https://docs.docker.com/get-docker/)
    * Used version 24.0.7, build afdd53b4e3
    * docker-compose version 2.23.3 used
    * For Linux systems:

        * Debian, Ubuntu -> `sudo apt-get install docker docker-compose`

        * Arch based -> `sudo pacman -S docker docker-compose`

    * Check the documentation for other distributions

    * MAC and Windows:

        * Follow the documentation to install Docker Desktop

        * docker and docker-compose are bundled

        * Use `docker -v` and `docker-compose -v` to confirm the installation, and check the installed versions

        * Additionally, use `docker run hello-world` to fetch, build and run a dummy container


## Running the application
* Database
    * Docker is used to run a Mongo database. Tag 'latest' is used by default, the project was developed using a mongo version 6.0.3.

     * To compose and start a fresh database, navigate to the _db_ directory and run `docker-compose up -d`.

    * The database port, root user, and root password are defined in the _docker-compose.yml_ file.
    * Use `docker exec -it tempo-trove mongosh -u "admin" -p "password"` to connect to the database with a mongo shell and be able to execute queries.
    * Run the _parseAndStoreToDB.py_ script to read data from provided csv file, store them to the database and configure metadata structure (`python parseAndStoreToDB.py`)
* API
    * Run `uvicorn main:app --reload` command from the api directory to start the api.
* WebUI
    * Navigate to the _tempo-trove-webui_ directory
    * Use `yarn install` to install all the project dependencies
    * Use `yarn run dev` to start a dev server (should run on localhost:5173)