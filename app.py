from flask import Flask, jsonify, request
import configparser
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from flask_cors import CORS,cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/')
def helloWorld():
    return "Flask App Running"

@cross_origin()
@app.route('/subscribe', methods=['POST','GET'])
def subscribe():
    email = request.args.get('email') 
    browser_path = os.environ.get("GOOGLE_CHROME_BIN")
    options = webdriver.ChromeOptions()
    options.add_argument(browser_path)
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    driver.get("https://beyondexams.substack.com/")
    time.sleep(5)
    input_box = driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[2]/div/div/div[1]/form/div[1]/input')
    input_box.send_keys(email)
    input_box.send_keys(Keys.ENTER)
    print(email + " subscribed")
    return jsonify({'status' : "Success", 'status_code' : 200, 'message' : "Email subscribed successfully!", 'data' : email})


if __name__ == "__main__":
    app.run('127.0.0.1', port=5000, debug=True)
