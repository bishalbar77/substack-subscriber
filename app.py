import configparser
from lib2to3.pgen2 import driver
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os


# config_parser = configparser.RawConfigParser()
# config_file_path = 'D:/ProFoo/substack/mysettings.txt'
# config_parser.read(config_file_path)

# browser = config_parser.get('config', 'BROWSER')
# browser_path = config_parser.get('config', 'BROWSER_PATH')
browser_path = os.environ.get("GOOGLE_CHROME_BIN")

options = webdriver.ChromeOptions()
options.add_argument(browser_path)

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
driver.get("https://beyondexams.substack.com/")
time.sleep(5)

def send_message(email):
    input_box = driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[2]/div/div/div[1]/form/div[1]/input')
    input_box.send_keys(email)
    input_box.send_keys(Keys.ENTER)
    print(email + " subscribed")

# if __name__ == '__main__':
#     main()

send_message("bishalranabr01@gmail.com")