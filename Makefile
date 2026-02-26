
create_env:
	python -m venv venv


req:
	pip install requirements.txt


run:
	source venv/bin/activate && python main.py

run_windows:
	venv\Scripts\activate && python main.py