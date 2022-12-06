# Connect4

Connect 4 spinoff with Go and Vue 3.

## Prereqs
- [Docker](https://docs.docker.com/engine/install/)
- [Node.js](https://nodejs.org/en/)
- [Python 3.10 or greater](https://www.python.org/downloads/)
- [Quasar CLI](https://quasar.dev/start/quasar-cli) 

## Installation
- Start docker
- Start backend
```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
docker-compose up -d
uvicorn main:app --reload
```
- Start front
```bash
cd ..
cd frontend
quasar dev
```
## License
[MIT](https://choosealicense.com/licenses/mit/)