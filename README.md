# CrytoBoard
# Docker 
## build image and start service
    docker-compose up --build
## stop and remove container
    docker-compose down
## possible error
If you encounter something like the image below, this indicate the host machine’s port specify in the docker-compose.yaml is being used. Here, ports:- "5001:5000", the 5001 is the host machine’s port. We can solve this problem by use a different port or free the host port. For example, this error appear because I use ports:- "5000:5000" for backend but 5000 is occupied, so I change it to ports:- "5001:5000". The frontend ports error can solved by the same methods for the backend. 
![Error Screenshot](possible_error.png)

When you change the backend port, the 
    const host = "http://127.0.0.1:5001/" #line22 in CrytoBoard/frontend/src/Price/Price.tsx
need to be changed accordingly.

## access the website
http://localhost:8080

# Dev Mode (Skip if docker executed successfully)
## backend: Python Flask
    
    cd backend    

    python3 -m venv .venv

    . .venv/bin/activate

    pip install Flask flask_pymongo apscheduler requests

    pip install numpy

    python main.py

## frontend: TypeScript React

First, go to frontend/src/Price/Price.tsx (line 22), change *host*  to your backend url

Then, run

    cd frontend    

    npm install

    npm start