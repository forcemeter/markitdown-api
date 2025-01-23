python3.11 -m venv venv
source venv/bin/activate
pip3.11 install -r requirements.txt

uvicorn main:app --reload