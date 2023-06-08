import time, random, requests, re, datetime, json, pyodbc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

SQLserver = '10.21.24.113'
username = 'sa2'
password = 'labwke405'
database = 'uniqueDB'
driver = '{FreeTDS}'
connectionString = 'DRIVER={0};SERVER={1};PORT=1433;DATABASE={2};UID={3};PWD={4}'.format(driver, SQLserver, database, username, password)

sleep = random.randrange(5,7)
def scroll():
    last_height = chrome_browser.execute_script("return document.body.scrollHeight")
    for i in range(20):
        chrome_browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(sleep)
        new_height = chrome_browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  #不再刷新
            break
        last_height = new_height

def normalized(url):
    if 'facebook.com' in url:
        if ('story_fbid=pfbid' in url):
            post_regex = re.compile(r"(.*story_fbid=pfbid.*)&eav")
            match = post_regex.search(url)
            if match != None:
                url_split = match.group(1)
                return url_split
            else:
                return url
        elif('story_fbid' in url):
            post_regex = re.compile(r"(.*id=.*)&eav")
            match = post_regex.search(url)
            if match != None:
                url_split = match.group(1)
                return url_split
            else:
                return url
        elif('/events/' in url):
            event_regex = re.compile(r"(.*)&eav")
            match = event_regex.search(url)
            if match != None:
                url_split = match.group(1)
                return url_split
            else:
                url = url.replace('www', 'm')
                return url
        elif('photo' in url):
            photo_regex = re.compile(r"(.*)&eav")
            match = photo_regex.search(url)
            if match != None:
                url_split = match.group(1)
                return url_split
            else:
                url_regex = re.compile(r"(.*)\?")
                match = url_regex.search(url)
                if match != None:
                    url_split = match.group(1)
                    url_split = url_split.replace('www', 'm')
                    return url_split
                else:
                    url = url.replace('www', 'm')
                    return url
        elif('video' in url):
            video_regex = re.compile(r"(.*)\?")
            match = video_regex.search(url)
            if match != None:
                url_split = match.group(1)
                return url_split
            else:
                url = url.replace('www', 'm')
                return url
        elif ('l.facebook.com' in url):
            redirect_urlregex = re.compile(r"l\.php\?u=(.*)&h")
            match = redirect_urlregex.search(url)
            if match != None:
                url_split = match.group(1)
                url_split = url_split.replace('%3A', ':')
                url_split = url_split.replace('%2F', '/')
                url_split = url_split.replace('%3F', '?')
                url_split = url_split.replace('%3D', '=')
                url_split = url_split.replace('%21', '!')
                url_split = url_split.replace('%23', '#')
                url_split = url_split.replace('%24', '$')
                url_split = url_split.replace('%26', '&')
                url_split = url_split.replace('%27', "'")
                url_split = url_split.replace('%28', '(')
                url_split = url_split.replace('%29', ')')
                url_split = url_split.replace('%2A', '*')
                url_split = url_split.replace('%2B', '+')
                url_split = url_split.replace('%2C', ',')
                url_split = url_split.replace('%3B', ';')
                url_split = url_split.replace('%40', '@')
                url_split = url_split.replace('%5B', '[')
                url_split = url_split.replace('%5D', ']')
                while True:
                    urlheader = requests.get(url_split)
                    print(urlheader)
                    if(len(urlheader.history) != 0):
                        for index, history in enumerate(urlheader.history):
                            if (index == len(urlheader.history) - 1):
                                url_split = history.headers["Location"]
                        print('hello')
                    else:
                        return url_split
            else:
                return url
        elif('www.facebook.com' in url):
            url_regex = re.compile(r"(.*)\?")
            match = url_regex.search(url)
            if match != None:
                url_split = match.group(1)
                url_split = url_split.replace('www', 'm')
                return url_split
            else:
                url = url.replace('www', 'm')
                return url
        else:
            return url
    else:
        try:
            urlheader = requests.get(url)
            if(len(urlheader.history) != 0):
                for index, history in enumerate(urlheader.history):
                    if (index == len(urlheader.history) - 1):
                        return history.headers["Location"]
            else:
                return url
        except requests.exceptions.SSLError as e:
            fNormalizeError = open("./NormalizeError.txt", "a", encoding='utf-8')
            fNormalizeError.write('問題網址：' + url + ' 錯誤資訊：' + str(e.args) + '\n')
            fNormalizeError.close()
        except requests.exceptions.ConnectionError as e:
            fNormalizeError = open("./NormalizeError.txt", "a", encoding='utf-8')
            fNormalizeError.write('問題網址：' + url + ' 錯誤資訊：' + str(e.args) + '\n')
            fNormalizeError.close()

def login():
    try:
        while True:
            cnxn = pyodbc.connect(connectionString)
            cursor = cnxn.cursor()
            SQLString_insert = '''
                declare @AC nvarchar(max), @Password nvarchar(max), @AID int
                exec uniqueDB.dbo.xp_getidleAccount @Account=@AC output, @PWD=@Password output, @AccountID=@AID output
                select @AC, @Password, @AID
            '''
            try:
                cursor.execute(SQLString_insert)
                result = cursor.fetchall()
                cursor.commit()
                if result[0][0] != None and result[0][1] != None:
                    Account = result[0][0]
                    Password = result[0][1]
                    AID = result[0][2]
                    break
                else:
                    print('sleeping 600')
                    time.sleep(300)
            except pyodbc.IntegrityError:
                with open('error.txt', 'w', encoding='utf-8') as f:
                    f.write(pyodbc.ProgrammingError.args)
            cursor.commit()
            cnxn.close()
        ac = chrome_browser.find_element( By.NAME, value='email')
        ac.send_keys(Account)
        pwd = chrome_browser.find_element(By.NAME, value='pass')
        pwd.send_keys(Password)
        time.sleep(sleep)
        login = chrome_browser.find_element(By.NAME, value='login')
        login.click()
        time.sleep(sleep)
        return Account, Password
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = "NoSuchElementException in login()"
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

try:
    options = Options()
    options.add_argument("--start-maximized")  #最大化視窗
    options.add_argument("--incognito")#開啟無痕模式
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    webdriver_path = ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    chrome_browser = webdriver.Chrome(service=webdriver_path, options = options, desired_capabilities=caps)

    chrome_browser.get("https://m.facebook.com/home.php")
    time.sleep(sleep)

    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.cursor()
    SQLString_insert = """
        set nocount on; exec xp_FansPageTask
    """ 
    try:
        cursor.execute(SQLString_insert)
        target = cursor.fetchall()
        cursor.commit()
    except pyodbc.IntegrityError:
        with open('error.txt', 'w', encoding='utf-8') as f:
            f.write(pyodbc.ProgrammingError.args)  
    cnxn.close()
    if target[0][0] is not None:
        AC, PWD = login()
        time.sleep(sleep)
        for index, targetlink in enumerate(target):
            targeturl = ''
            if 'www.facebook.com' in targetlink[1]:
                targeturl = targetlink[1].replace('www.facebook.com', 'm.facebook.com')
            elif 'mbasic.facebook.com' in targetlink[1]:
                targeturl = targetlink[1].replace('mbasic.facebook.com', 'm.facebook.com')
            else:
                targeturl = targetlink[1]
            print(targeturl)
            chrome_browser.get(targeturl)
            time.sleep(sleep)
            try:
                scroll()
                articles = chrome_browser.find_elements(By.TAG_NAME, value='article')
                for a in articles:
                    post_time = ''
                    try:
                        data_ft = a.get_attribute('data-ft')
                        data_ft_json = json.loads(data_ft)
                        content_owner_id_new = data_ft_json["content_owner_id_new"]
                        post_time_string = data_ft_json["page_insights"][content_owner_id_new]["post_context"]["publish_time"]
                        struct_time = time.localtime(post_time_string)
                        post_time = time.strftime("%Y/%m/%d %H:%M:%S", struct_time)
                    except KeyError:
                        post_time = ''
                        pass
                    except TypeError:
                        post_time = ''
                        pass
                    anchor = a.find_element(By.CSS_SELECTOR, value="[data-sigil='feed-ufi-trigger']")
                    url = anchor.get_attribute('href')
                    newurl = normalized(url)
                    print(newurl)
                    cnxn = pyodbc.connect(connectionString)
                    cursor = cnxn.cursor()
                    SQLString_insert = """
                        declare @ar bit
                        exec uniqueDB.dbo.xp_arrive_targettime @posturl=?, @post_time=?, @origintime=?, @targettime=?, @typemask=?, @output=?, @arrive=@ar output
                        select @ar
                    """ 
                    values_insert = (newurl, post_time, targetlink[4], targetlink[5], targetlink[3], targetlink[2])
                    print(values_insert)
                    try:
                        cursor.execute(SQLString_insert, values_insert)
                        arrive = cursor.fetchall()
                        cursor.commit()
                        if arrive == True:
                            print('bye')
                            cnxn.close()
                            break
                        else:
                            print(post_time)
                    except pyodbc.IntegrityError:
                        with open('error.txt', 'w', encoding='utf-8') as f:
                            f.write(pyodbc.ProgrammingError.args)
                    except pyodbc.ProgrammingError as e:
                        with open('error.txt', 'w', encoding='utf-8') as f:
                            f.write(url + post_time)
                    cnxn.close()

            except exceptions.NoSuchElementException as e:
                print(e.args)
            except exceptions.StaleElementReferenceException:
                ActionChains(chrome_browser).move_to_element(a).perform()
                time.sleep(sleep)
    
        cnxn = pyodbc.connect(connectionString)
        cursor = cnxn.cursor()
        SQLString_insert = """
        declare @result bit, @re bit
        exec xp_updateAccountState @Account=?, @PWD=?, @result=@re output
        select @re
        """ 
        updateAccountState_input = (AC, PWD)
        try:
            cursor.execute(SQLString_insert, updateAccountState_input)
            result = cursor.fetchone()
            if (result[0] == True):
                print("Success")
            else:
                print("Error")
        except pyodbc.IntegrityError:
            with open('error.txt', 'w', encoding='utf-8') as f:
                f.write(pyodbc.ProgrammingError.args)
        cursor.commit()
        cnxn.close()
    
    chrome_browser.delete_all_cookies()
    chrome_browser.quit()
except exceptions.InvalidArgumentException as e:
    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.cursor()
    SQLString_insert = """
    declare @result bit, @re bit
    exec uniqueDB.dbo.xp_updateAccountState @Account=?, @PWD=?, @result=@re output
    select @re
    """ 
    updateAccountState_input = (AC, PWD)
    try:
        cursor.execute(SQLString_insert, updateAccountState_input)
        result = cursor.fetchone()
        if (result[0] == True):
            print("Success")
        else:
            print("Error")
    except pyodbc.IntegrityError:
        with open('error.txt', 'w', encoding='utf-8') as f:
            f.write(pyodbc.ProgrammingError.args)
    cursor.commit()
    cnxn.close()

    chrome_browser.delete_all_cookies()
    chrome_browser.quit()