### Pre-requisites
Installed locally:
* node.js
* Android Studio
* Python
* Pytest
* Appium Server

### Python
* Run pip install -r requirements.txt
* pytest==8.2.0
* Appium-Python-Client==3.2.1
* selenium==4.20.0
* pytest-html==4.1.1
* python-dotenv==1.0.1


### Configuration
[pytest]
* addopts = -v --html=report.html --self-contained-html
* testpaths = tests

### Set-up
* Run Appium. I run it in Pycharm using the terminal for the project
* Open Android Studio
* Open Virtual Device manager (or attach to a physical device via ADB)
* install the following app on the device (drag and drop from Windows or install natively)
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
