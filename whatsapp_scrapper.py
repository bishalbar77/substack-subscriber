"""
Importing the libraries that we are going to use
for loading the settings file and scraping the website
"""
import csv
import pdb
import re
import glob
import os
import time
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import base64
from tabulate import tabulate


class WhatsappScrapper():
    def __init__(self, page, browser, browser_path, downloads):
        self.page = page
        self.browser = browser
        self.browser_path = browser_path
        self.downloads = downloads
        self.driver = self.load_driver()

        # Open the web page with the given browser
        self.driver.get(self.page)
        time.sleep(6)
        self.driver.get_screenshot_as_file("whatsapp.png")

    def load_driver(self):
        """
        Load the Selenium driver depending on the browser
        (Edge and Safari are not running yet)
        """
        driver = None
        if self.browser == 'firefox':
            firefox_profile = webdriver.FirefoxProfile(
                self.browser_path)
            driver = webdriver.Firefox(firefox_profile)
        elif self.browser == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option( "prefs", {'profile.default_content_setting_values.automatic_downloads': 1})
            if self.browser_path:
                chrome_options.add_argument('user-data-dir=' +
                                            self.browser_path)
            driver = webdriver.Chrome(ChromeDriverManager().install())

        elif self.browser == 'safari':
            pass
        elif self.browser == 'edge':
            pass

        return driver

    def open_conversation(self, name):
        """
        Function that search the specified user by the 'name' and opens the conversation.
        """
        self.name = name
        while True:
            for chatter in self.driver.find_elements_by_xpath("//div[@id='pane-side']/div/div/div/div"):
                chatter_path = ".//span[@title='{}']".format(
                    name)

                # Wait until the chatter box is loaded in DOM
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(@title,'{}')]".format(
                                name)))
                    )
                except StaleElementReferenceException:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(@title,'{}')]".format(
                                name)))
                    )

                try:
                    chatter_name = chatter.find_element_by_xpath(
                        chatter_path).text
                    if chatter_name == name:
                        chatter.find_element_by_xpath(
                            ".//div/div").click()
                        return True
                except Exception as e:
                    pass

    def hover_click(self, elem):
        height, width = elem.size.values()

        # ActionChains(self.driver).move_to_element_with_offset(elem,width/2,height/2)
        hover = ActionChains(self.driver).move_to_element_with_offset(elem,width/2,height/2)
        # down_context = self.driver.find_element_by_xpath('//span[contains(@data-testid,"down-context")]')
        # ActionChains(self.driver).move_to_element(down_context).click().perform()
        hover.click()
        hover.perform()

    def capture_image(self, elem):
        print("Capturing Image")
        time.sleep(1)
        # height, width = elem.size.values()
        # ActionChains(self.driver).move_to_element_with_offset(elem,width/2,height/2)
        # down_context = elem.find_element_by_xpath('//span[contains(@data-testid,"down-context")]')
        # ActionChains(self.driver).move_to_element(down_context).click().perform()
        # download_button = elem.find_element_by_xpath('//div[contains(@label,"Download")]')
        # download_button.click()
        # time.sleep(2)
        try:
            down = elem.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
            down.click()
            time.sleep(2)
        except:
            pass

        self.hover_click(elem.find_element_by_xpath('.//img[contains(@src, "blob")]'))
        time.sleep(2)
        download = self.driver.find_element_by_xpath('//span[contains(@data-testid,"download")]')
        download.click()
        close_window = self.driver.find_element_by_xpath('//span[contains(@data-testid,"x-viewer")]')
        close_window.click()
        time.sleep(2)
        list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        media = "Photo"
        file_loc = latest_file

        return media, file_loc

    def capture_video(self, elem):
        print("Capturing Video")
        try:
            down = elem.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
            down.click()
            time.sleep(2)
        except:
            pass
        time.sleep(2)
        self.hover_click(elem.find_element_by_xpath('.//span[contains(@data-testid, "media-play")]'))
        time.sleep(15)
        download = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@data-testid,'download')]")))
        # download = self.driver.find_element_by_xpath('//span[contains(@data-testid,"download")]')
        download.click()
        close_window = self.driver.find_element_by_xpath('//span[contains(@data-testid,"x-viewer")]')
        close_window.click()
        time.sleep(3)
        list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        media = "Video"
        file_loc = latest_file

        return media, file_loc

    def capture_audio(self, elem):
        try:
            down = elem.find_element_by_xpath('.//span[contains(@data-testid,"audio-download")]')
            down.click()
        except:
            pass
        down_context = elem.find_element_by_xpath('.//span[contains(@data-testid,"audio-play")]')
        down_context.click()
        down_context = elem.find_element_by_xpath('.//span[contains(@data-testid,"down-context")]')
        down_context.click()
        time.sleep(1)
        download_button = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Download")]')
        download_button.click()
        time.sleep(2)
        list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        media = "Audio"
        file_loc = latest_file

        return media, file_loc

    def convert_to_datetime(self, time_date):
        time, dates = time_date
        in_format = '%m/%d/%Y'
        out_format = '%Y-%m-%d'
        dates = datetime.strptime(dates, in_format).strftime(out_format)
        date_time = dates + ' ' + time
        return date_time

    def return_filetype(self, ext):    
        extensions = {
            "Photo" : {'jpg', 'thumb', 'png', 'tiff', 'jpeg'},
            "Audio" : {'aac', 'm4a', 'amr', 'opus'},
            "Video" : {'mov', 'mp4'},
            "Document" : {'pdf', 'doc', 'docx', 'csv', 'xslx', 'ppt', 'pptx'}        
        }
        for filetype in extensions:
            if ext in extensions[filetype]:
                return filetype

        return 'File'

    def return_lastdate(self, container):
        date_pattern = r'[0-3]?[0-9]\/[0-3]?[0-9]\/(?:[0-9]{2})?[0-9]{2}|MONDAY|SUNDAY|TUESDAY|WEDNESDAY|FRIDAY|SATURDAY|THURSDAY|YESTERDAY|TODAY'
        content = container.get_attribute('innerHTML')
        dateif = re.findall(date_pattern, content)
        if dateif:
            last_date = dateif[-1]
            if last_date in ['MONDAY', 'SUNDAY', 'TUESDAY', 'WEDNESDAY', 
            'THURSDAY', 'WEDNESDAY', 'FRIDAY', 'SATURDAY', 'YESTERDAY', 'TODAY']:
                if last_date == 'TODAY':
                    last_date = date.today().strftime('%Y-%m-%d')
                elif last_date == 'YESTERDAY':
                    last_date = (date.today() + relativedelta(days=-1)).strftime('%Y-%m-%d')
                elif last_date == 'MONDAY':
                    last_date = (date.today() + relativedelta(weekday=MO(-1))).strftime('%Y-%m-%d')
                elif last_date == 'TUESDAY':
                    last_date = (date.today() + relativedelta(weekday=TU(-1))).strftime('%Y-%m-%d')
                elif last_date == 'WEDNESDAY':
                    last_date = (date.today() + relativedelta(weekday=WE(-1))).strftime('%Y-%m-%d')
                elif last_date == 'THURSDAY':
                    last_date = (date.today() + relativedelta(weekday=TH(-1))).strftime('%Y-%m-%d')
                elif last_date == 'FRIDAY':
                    last_date = (date.today() + relativedelta(weekday=FR(-1))).strftime('%Y-%m-%d')
                elif last_date == 'SATURDAY':
                    last_date = (date.today() + relativedelta(weekday=SA(-1))).strftime('%Y-%m-%d')
                elif last_date == 'SUNDAY':
                    last_date = (date.today() + relativedelta(weekday=SU(-1))).strftime('%Y-%m-%d')

        return last_date

    def scroll_n_save(self, n):
        """
        Reading the last message that you got in from the chatter
        Params:
        n = number of scrolls to go above in chat
        """
        i = 0

        while(i<n):
            chat_section = self.driver.find_element_by_xpath(
                "//div[@aria-label='Message list. Press right arrow key on a message to open message context menu.']"
            )
            chat_section.send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            i = i+1

        # for media_down in self.driver.find_elements_by_xpath('//span[contains(@data-testid,"media-download)]'):

        all_messages = []

        timestamps = []

        all_message_containers = self.driver.find_elements_by_xpath(
        "//div[contains(@class,'message-in')] | //div[contains(@class,'message-out')]")

        all_containers =  self.driver.find_elements_by_xpath("//div[contains(@class,'focusable-list-item')]")

        date_pattern = r'[0-3]?[0-9]\/[0-3]?[0-9]\/(?:[0-9]{2})?[0-9]{2}|MONDAY|SUNDAY|TUESDAY|WEDNESDAY|FRIDAY|SATURDAY|THURSDAY|YESTERDAY|TODAY'
        time_pattern = r"\d\d?:\d\d\s?(?:AM|am|pm|PM|Am|Pm)|\d\d:\d\d"
        for container in all_containers:
            content = container.get_attribute('innerHTML')
            dateif = re.findall(date_pattern, content)
            timeif = re.findall(time_pattern, content)
            if dateif:
                last_date = dateif[-1]
                if last_date in ['MONDAY', 'SUNDAY', 'TUESDAY', 'WEDNESDAY', 
                'THURSDAY', 'WEDNESDAY', 'FRIDAY', 'SATURDAY', 'YESTERDAY', 'TODAY']:
                    if last_date == 'TODAY':
                        last_date = date.today().strftime('%Y-%m-%d')
                    elif last_date == 'YESTERDAY':
                        last_date = (date.today() + relativedelta(days=-1)).strftime('%Y-%m-%d')
                    elif last_date == 'MONDAY':
                        last_date = (date.today() + relativedelta(weekday=MO(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'TUESDAY':
                        last_date = (date.today() + relativedelta(weekday=TU(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'WEDNESDAY':
                        last_date = (date.today() + relativedelta(weekday=WE(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'THURSDAY':
                        last_date = (date.today() + relativedelta(weekday=TH(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'FRIDAY':
                        last_date = (date.today() + relativedelta(weekday=FR(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'SATURDAY':
                        last_date = (date.today() + relativedelta(weekday=SA(-1))).strftime('%Y-%m-%d')
                    elif last_date == 'SUNDAY':
                        last_date = (date.today() + relativedelta(weekday=SU(-1))).strftime('%Y-%m-%d')

            if timeif:
                try:
                    x = [timeif[-1], last_date]
                    datetime = self.convert_to_datetime(x)
                    timestamps.append(datetime)
                except:
                    pass
                 

        print('no. of messages', len(all_containers))

        for messages in all_message_containers:

            try:
                last_date = self.return_lastdate(messages)
            except:
                pass

            emojis = ''

            text_present = len(messages.find_elements_by_xpath(".//span[contains(@class,'selectable-text copyable-text')]"))
            image_present = len(messages.find_elements_by_xpath('.//img[contains(@src, "blob")]'))
            video_present = len(messages.find_elements_by_xpath('.//span[contains(@data-testid, "media-play")]'))

            try:
                if text_present:

                    message_container = messages.find_element_by_xpath(
                        ".//div[contains(@class,'copyable-text')]")
                    message_details = message_container.get_attribute("data-pre-plain-text").replace("]", ",").strip("[")
                    message_info = message_details.split(', ')
                    message_info[2] = message_info[2][:-2]
                    message_info[0] = self.convert_to_datetime(message_info[0:2])
                    message_info.pop(1)

                    message = message_container.find_element_by_xpath(
                        ".//span[contains(@class,'selectable-text copyable-text')]"
                    ).text

                    for emoji in message_container.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text copyable-text')]"
                    ):
                        emojis += (emoji.get_attribute("data-plain-text"))
                    message += emojis

                    if image_present or video_present:
                        print('I am image or video and text')
                        try:
                            media, file_loc = self.capture_image(messages)
                        except NoSuchElementException:
                            pass
                        try:
                            media, file_loc = self.capture_video(messages)
                        except NoSuchElementException:
                            pass
                        message_info.append(file_loc)
                        message_info.append(media)
                        all_messages.append(message_info)
                        text_of_media = message_info[:]
                        text_of_media[-2] = message
                        text_of_media[-1] = 'text'
                        all_messages.append(text_of_media)
                    else:
                        print('I am only text')
                        message_info.append(message)
                        message_info.append('text')
                        all_messages.append(message_info)

                elif image_present or video_present:
                    print(' I am only image')
                    try:
                        media, file_loc = self.capture_image(messages)
                    except NoSuchElementException:
                        pass
                    try:
                        media, file_loc = self.capture_video(messages)
                    except NoSuchElementException:
                        pass
                    dates = (file_loc.split('/')[-1])[15:25]
                    name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
                    timestamp = messages.find_elements_by_xpath('.//span[@dir]')[1].text
                    date_time = dates + ' ' + timestamp
                    message_info = [date_time, name, file_loc, media]
                    print(message_info)
                    all_messages.append(message_info)
                else:
                    print('I am either a pdf or a voicenote')
                    try:
                        media, file_loc = self.capture_audio(messages)
                        dates = (file_loc.split('/')[-1])[13:23]
                        name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
                        # media = self.return_filetype(((messages.find_elements_by_xpath('.//span[@dir]')[1].text).split('.'))[-1])
                        timestamp = messages.find_elements_by_xpath('.//span[@dir]')[1].text
                        date_time = dates + ' ' + timestamp
                        message_info = [date_time, name, file_loc, media]
                        all_messages.append(message_info)
                    except:
                        pass

                    try:
                        print("inside pdf try loop")
                        try:
                            down = messages.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
                            down.click()
                        except:
                            pass

                        try:
                            media_download = messages.find_element_by_xpath('.//span[contains(@data-testid,"audio-download")]')
                            media_download.click()
                        except Exception as e:
                            pass

                        time.sleep(2)
                        list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
                        latest_file = max(list_of_files, key=os.path.getctime)
                        print(latest_file)
                        dates = last_date
                        timestamp = messages.find_elements_by_xpath('.//span[@dir]')[2].text
                        name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
                        date_time = dates + ' ' + timestamp
                        media = self.return_filetype(((messages.find_elements_by_xpath('.//span[@dir]')[1].text).split('.'))[-1])
                        message_info = [date_time, name, latest_file, media]
                        print("DOCU INFO")
                        print(message_info)
                        all_messages.append(message_info)
                    except:
                        try: #when only emojis in message
                            message_container = messages.find_element_by_xpath(
                                                ".//div[contains(@class,'copyable-text')]")
                            message_details = message_container.get_attribute("data-pre-plain-text").replace("]", ",").strip("[")
                            message_info = message_details.split(', ')
                            message_info[2] = message_info[2][:-2]
                            message_info[0] = self.convert_to_datetime(message_info[0:2])
                            message_info.pop(1)

                            for emoji in message_container.find_elements_by_xpath(
                                    ".//img[contains(@class,'selectable-text copyable-text')]"
                            ):
                                emojis += (emoji.get_attribute("data-plain-text"))
                            message_info.append(emojis)
                            message_info.append('text')
                            all_messages.append(message_info)
                        except:
                            pass
            except:
                pass




        # print(tabulate(all_messages))

            # if text_present and image_present:
            #     print('I am image and text')
            # elif text_present and video_present:
            #     print('I am video and text')
            # elif image_present and not text_present:
            #     media, file_loc = self.capture_image(messages)
            # elif video_present and not text_present:
            #     print('I am video')
            # elif text_present and not image_present and not video_present:
            #     print('I am text')
            # # elif image_present 
            # else:
            #     print('Document')

        # for messages in all_message_containers:
        # # "//div[contains(@class,'focusable-list-item')]"):
        #     time.sleep(1)
        #     final_message = ""
        #     # get message text and emojis
            
        #     try:
        #         message = ""
        #         emojis = ""
        #         media = "No"
        #         file_loc = ""
        #         message_container = messages.find_element_by_xpath(
        #             ".//div[contains(@class,'copyable-text')]")

        #         message_details = message_container.get_attribute("data-pre-plain-text").replace("]", ",").strip("[")
        #         message_info = message_details.split(', ')

        #         try:
        #             down = messages.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
        #             down.click()
        #         except:
        #             pass

        #         try: #This Try Block checks and downloads images
        #             if len(message_container.find_elements_by_xpath('.//img[contains(@src, "blob")]')) > 0:
        #                 media, file_loc = self.capture_image(message_container)
        #         except NoSuchElementException:
        #             pass

        #         try: #This Try Block checks and downloads video
        #             if len(message_container.find_elements_by_xpath('.//span[contains(@data-testid, "media-play")]')) > 0:
        #                 media, file_loc = self.capture_video(message_container)
        #         except NoSuchElementException:
        #             pass
                
                
        #         message_info[2] = message_info[2][:-2]
        #         message_info[0] = self.convert_to_datetime(message_info[0:2])
        #         message_info.pop(1)
        #         final_message += message_details
                
        #         message = message_container.find_element_by_xpath(
        #             ".//span[contains(@class,'selectable-text copyable-text')]"
        #         ).text
        #         final_message += message

        #         for emoji in message_container.find_elements_by_xpath(
        #             ".//img[contains(@class,'selectable-text copyable-text')]"
        #         ):
        #             emojis += (emoji.get_attribute("data-plain-text"))
        #         message += emojis

        #         if file_loc != "": #cases when image and video are attached with a text
        #             message_info.append(file_loc)
        #             message_info.append(media)
        #             all_messages.append(message_info)
        #             text_of_media = message_info[:]
        #             text_of_media[-2] = message
        #             text_of_media[-1] = 'text'
        #             all_messages.append(text_of_media)
        #         else:
        #             message_info.append(message)
        #             message_info.append('text')
        #             all_messages.append(message_info)
                    
        #     except NoSuchElementException:  # In case there are only emojis in the message

        #         try:
        #             message = ""
        #             emojis = ""
        #             message_container = messages.find_element_by_xpath(
        #                 ".//div[contains(@class,'copyable-text')]")
        #             message_details = message_container.get_attribute("data-pre-plain-text").replace("]", ",").strip("[")
        #             message_info = message_details.split(', ')
        #             message_info[2] = message_info[2][:-2]
        #             message_info[0] = self.convert_to_datetime(message_info[0:2])
        #             message_info.pop(1)
        #             final_message += message_details
        #             for emoji in message_container.find_elements_by_xpath(
        #                     ".//img[contains(@class,'selectable-text copyable-text')]"
        #             ):
        #                 emojis += (emoji.get_attribute("data-plain-text"))
        #             message_info.append(emojis)
        #             message_info.append('text')
        #             all_messages.append(message_info)
        #         except NoSuchElementException:
        #             try:
        #                 elem = messages
        #                 ActionChains(self.driver).move_to_element(messages)
        #                 time.sleep(2)
        #                 try:
        #                     down = elem.find_element_by_xpath('.//span[contains(@data-testid,"audio-download")]')
        #                     down.click()
        #                 except:
        #                     pass
        #                 down_context = messages.find_element_by_xpath('.//span[contains(@data-testid,"audio-play")]')
        #                 down_context.click()
        #                 down_context = messages.find_element_by_xpath('.//span[contains(@data-testid,"down-context")]')
        #                 down_context.click()
        #                 time.sleep(1)
        #                 download_button = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Download")]')
        #                 download_button.click()
        #                 time.sleep(2)
        #                 list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        #                 latest_file = max(list_of_files, key=os.path.getctime)
        #                 media = "Audio"
        #                 file_loc = latest_file
        #                 dates = (latest_file.split('/')[-1])[13:23]
        #                 name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
        #                 # media = self.return_filetype(((messages.find_elements_by_xpath('.//span[@dir]')[1].text).split('.'))[-1])
        #                 timestamp = messages.find_elements_by_xpath('.//span[@dir]')[1].text
        #                 date_time = dates + ' ' + timestamp
        #                 message_info = [date_time, name, latest_file, media]
        #                 all_messages.append(message_info)
        #             except:
        #                 try:
        #                     try:
        #                         down = elem.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
        #                         down.click()
        #                     except:
        #                         pass
        #                     media_download = messages.find_element_by_xpath('.//span[contains(@data-testid, "audio-download")]')
        #                     media_download.click()
        #                     time.sleep(2)
        #                     list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        #                     latest_file = max(list_of_files, key=os.path.getctime) 
        #                     dates = (latest_file.split('/')[-1])[15:25]
        #                     timestamp = messages.find_elements_by_xpath('.//span[@dir]')[1].text
        #                     name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
        #                     date_time = dates + ' ' + timestamp
        #                     media = self.return_filetype(((messages.find_elements_by_xpath('.//span[@dir]')[1].text).split('.'))[-1])
        #                     message_info = [date_time, name, latest_file, media]
        #                     all_messages.append(message_info)
        #                 except NoSuchElementException:
        #                     try:
        #                         try:
        #                             down = elem.find_element_by_xpath('.//span[contains(@data-testid,"media-download")]')
        #                             down.click()
        #                             time.sleep(2)
        #                         except:
        #                             pass
        #                         try:
        #                             media, file_loc = self.capture_image(messages)
        #                         except:
        #                             pass
        #                         try:
        #                             media, file_loc = self.capture_video(messages)
        #                         except:
        #                             pass
        #                         dates = (file_loc.split('/')[-1])[15:25]
        #                         name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
        #                         timestamp = messages.find_elements_by_xpath('.//span[@dir]')[1].text
        #                         date_time = dates + ' ' + timestamp
        #                         message_info = [date_time, name, file_loc, media]
        #                         if media != 'No':
        #                             all_messages.append(message_info)
        #                     except Exception as e:
        #                         # print(messages.get_attribute('innerHTML'))
        #                         pass

        #             # try:
        #             #     media_download = messages.find_element_by_xpath('.//span[contains(@data-testid, "audio-download")]')
        #             #     media_download.click()
        #             #     time.sleep(2)
        #             #     list_of_files = glob.glob(self.downloads + '/*') # * means all if need specific format then *.csv
        #             #     latest_file = max(list_of_files, key=os.path.getctime) 
        #             #     date = datetime.fromtimestamp(os.path.getmtime(latest_file)).strftime('%Y-%m-%d')
        #             #     timestamp = messages.find_elements_by_xpath('.//span[@dir]')[2].text
        #             #     name = (messages.find_elements_by_xpath('.//span[@dir]')[0].text)
        #             #     date_time = date + ' ' + timestamp
        #             #     media = self.return_filetype(((messages.find_elements_by_xpath('.//span[@dir]')[1].text).split('.'))[-1])
        #             #     message_info = [date_time, name, latest_file, media]
        #             #     all_messages.append(message_info)
        #             # except NoSuchElementException:
        #             #     pass

        fields = ['datetime', 'name', 'message', 'File Type']

        
        extracted_timestamps = []
        for extracted_message in all_messages:
            message_time = (extracted_message[0])
            extracted_timestamps.append(message_time)

        for ts in extracted_timestamps:
            if ts in timestamps:
                timestamps.remove(ts)

        print('FINAL', timestamps)

        with open(self.name + '.csv', 'w', encoding='utf-8') as f:
      
            # using csv.writer method from CSV package 
            write = csv.writer(f) 
            
            write.writerow(fields) 
            write.writerows(all_messages)

    
