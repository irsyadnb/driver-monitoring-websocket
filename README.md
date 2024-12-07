# Driver Monitoring Websocket
Websocket server for driver monitoring.

# How to run
0. Make the `.env` file by copying duplicating from the `.env.example` file.

1. Create a virtual environment: <br/> ```python -m venv venv```

2. Activate the virtual environment:
* Windows: <br/>
`venv\Scripts\activate`
* Linux/macOS: <br/>
`source venv/bin/activate`

3. Install the required packages: <br/>
`pip install -r src/requirements.txt`

4. Run the server in development: <br/>
`python3 src/app.py `

5. Run the server in production <br/>
`gunicorn --worker-class eventlet 'src.app:app' `