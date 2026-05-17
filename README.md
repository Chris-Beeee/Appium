### Overview
This is intended as a proof-of-concept to make sure my Appium setup is working, and to demonstrate a basic front-end UI scrape with back-end verification method.

### Pre-requisites
Installed locally:
* Node.js
* Android Studio
* Python
* Pytest
* Appium Server

### Python
* Run pip install -r requirements.txt
* Pytest==8.2.0
* Appium-Python-Client==3.2.1
* Selenium==4.20.0
* Pytest-html==4.1.1
* Python-dotenv==1.0.1

### Configuration
[pytest.ini]
* addopts = -v --html=report.html --self-contained-html
* testpaths = tests

### Set-up
* Run Appium. I run it in Pycharm using the terminal for the project
* Open Android Studio
* Open Virtual Device manager (or attach to a physical device via ADB)
* Install the following app on the device (drag and drop from Windows or install natively)
* https://github.com/saucelabs/my-demo-app-android/releases/download

### Test scope
1) Open App
2) Scrape front page (item name, price)
3) Ingest any items that do not currently exist on dummy backend, ignore them for current run
4) Compare to (dummy ) backend
5) Compare titles and prices for a configured number of items
6) Scroll until number of items is reached
7) Use Xpath to ensure all items are matched to each other correctly, avoiding mismatch due to scrolling logic
8) Return error if any item prices do not match

### Limitations
This app does not have a robust way to display user ratings, so I have not yet found a way to return those as well. Only to return the fact that they exist. 

### How to Run
**Powershell/CMD**
```powershell
# Create the virtual environment
python -m venv venv
# Activate it
.\venv\Scripts\Activate.ps1
# Install dependencies
pip install -r requirements.txt
# Run tests
pytest
