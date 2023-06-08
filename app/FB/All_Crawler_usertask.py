import time, random, requests, re, json, pyodbc
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
sleep35 = random.randrange(4,6)
max_scroll = 150

def FBUserNormalized(url):
    user_regex1 = re.compile(r"(.*)\?eav")
    match1 = user_regex1.search(url)
    if match1 != None:
        url_split = match1.group(1)
        return url_split
    user_regex2 = re.compile(r"(.*)&eav")
    match2 = user_regex2.search(url)
    if match2 != None:
        url_split = match2.group(1)
        return url_split
    return url
    
def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

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
                    print('sleeping 180')
                    time.sleep(180)
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
        msg = 'NoSuchElementException in login()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')
        chrome_browser.delete_all_cookies()
        chrome_browser.quit()

def metadata(output, url, oid):
    try:
        if 'mbasic.facebook.com' in url:
            url = url.replace('mbasic.facebook.com', 'm.facebook.com')
        elif 'www.facebook.com' in url:
            url = url.replace('www.facebook.com', 'm.facebook.com')
        chrome_browser.get(url)
        time.sleep(sleep)
        postmata = chrome_browser.find_element(By.CLASS_NAME, value='async_like')
        data_ft = postmata.get_attribute('data-ft')
        data_ft_json = json.loads(data_ft)
        content_owner_id_new = data_ft_json['content_owner_id_new']
        mf_story_key = data_ft_json['mf_story_key']
        from_id = content_owner_id_new
        output['from_id'] = from_id
        output['page_id'] = data_ft_json['page_id']
        output['post_id'] = data_ft_json['page_id'] +'_'+ mf_story_key
        output['url'] = url       
        try:
            post_time_string = data_ft_json['page_insights'][content_owner_id_new]['post_context']['publish_time']
            struct_time = time.localtime(post_time_string)
            post_time = time.strftime('%Y/%m/%d %H:%M:%S', struct_time)
            output['post_time'] = post_time
        except:
            output['post_time'] = ''
        source = 'fb'
        nowTime = int(time.time()) # 取得現在時間
        struct_time = time.localtime(nowTime) # 轉換成時間元組
        timeString = time.strftime('%Y-%m-%d %I:%M:%S', struct_time) # 將時間元組轉換成想要的字串
        cR = '0'
        cT = '0'
        output['source'] = source
        output['track_time'] = timeString
        output['page_category'] = ''
        output['cR']= cR
        output['cT']= cT
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = '取不到Metadata'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.write('URL：'+ str(url) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')
    except KeyError as e:
        time.sleep(sleep)
        post_time_string = data_ft_json['page_insights'][content_owner_id_new]['post_context']['publish_time']
        from_id = content_owner_id_new
        output['from_id'] = from_id
        struct_time = time.localtime(post_time_string)
        post_time = time.strftime('%Y/%m/%d %H:%M:%S', struct_time)
        output['post_time'] = post_time
        post_id = data_ft_json['page_insights'][content_owner_id_new]['targets'][0]['post_id']
        output['post_id'] = post_id
        output['url'] = url

def body(output):
    try:
        poster = chrome_browser.find_element(By.TAG_NAME, value='strong').text
        post_content = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_5rgt _5nk5']").text
        output['from_name'] = poster
        output['body'] = post_content
        output['page_name'] = poster
        output['title'] = post_content[:20]
        hashtags = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_5rgt _5nk5']").find_elements(By.CSS_SELECTOR, value="[class='_5ayv _qdx']")
        for tag in hashtags:
            hadtag = False
            for newtag in output['hashtag']:
                if(newtag == tag.text):
                    hadtag = True
            if(hadtag == False):
                output['hashtag'].append(tag.text)
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in body()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def photo(output):
    try:
        tag_div = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_5rgu _7dc9 _27x0']")
        tag_anchor = tag_div.find_elements(By.TAG_NAME, value='a')
        for img in tag_anchor:
            imglink = img.get_attribute('href')
            hadimg = False
            for newimg in output['image_link']:
                if(imglink == newimg):
                    hadimg = True
            if(hadimg == False):
                output['image_link'].append(imglink)
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in photo()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：貼文不帶任何照片' + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def video(output):
    try:
        video = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_5rgu _7dc9 _27x0']").find_element(By.CLASS_NAME, value='_53mw').get_attribute('data-store')
        video_json = json.loads(video)
        video_url = video_json['videoURL'].replace(r'\\','')
        hadimg = False
        for newimg in output['image_link']:
            if(video_url == newimg):
                hadimg = True
        if(hadimg == False):
            output['image_link'].append(video_url)
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in video()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：貼文不帶任何影片' + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_basic(output):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        url = chrome_browser.current_url
        if 'm.facebook' in url:
            newurl = url.replace('m.facebook.com','mbasic.facebook.com')
        elif 'www.facebook' in url:
            newurl = url.replace('www','mbasic')
        chrome_browser.get(newurl)
        time.sleep(sleep)
        reaction = chrome_browser.find_element(By.CLASS_NAME, value='y')
        anchors = reaction.find_elements(By.TAG_NAME, value='a')
        for i,a in enumerate(anchors):
            if i == 0:
                continue
            link = a.get_attribute('href')
            link_split = link.split('&')
            totalcount = ''
            reaction_id = ''
            for index, string in enumerate(link_split):
                if 'total_count' in string:
                    link_regex = re.compile(r'total_count=(.*)')
                    match = link_regex.search(string)
                    if match != None:
                        totalcount = match.group(1)
                if 'reaction_id' in string:
                    reaction_id_regex = re.compile(r'reaction_id=(.*)')
                    match = reaction_id_regex.search(string)
                    if match != None:
                        reaction_id = match.group(1)
            if(reaction_id == '1635855486666999'):#讚
                output['cL'] = totalcount
            elif(reaction_id == '613557422527858'):#加油
                output['cU'] = totalcount
            elif(reaction_id == '1678524932434102'):#愛心
                output['cO'] = totalcount
            elif(reaction_id == '115940658764963'):#哈
                output['cH'] = totalcount
            elif(reaction_id == '444813342392137'):#怒
                output['cA'] = totalcount
            elif(reaction_id == '478547315650144'):#哇
                output['cW'] = totalcount
            elif(reaction_id == '908563459236466'):#嗚
                output['cD'] = totalcount
            else:
                continue
        time.sleep(sleep)
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in video()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：此貼文是直播存檔' + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def tcs(output):
    try:
        sharetimes = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_43lx _55wr']")
        tcs = sharetimes.text.split(' ')
        for index, string in enumerate(tcs):
            if(index == 0):
                output['cS'] = string
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in share()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def tcc(output, url):
    try:
        if 'm.facebook' in url:
            newurl = url.replace('m.facebook.com','www.facebook.com')
        elif 'mbasic.facebook' in url:
            newurl = url.replace('mbasic','www')
        else:
            newurl = url
        chrome_browser.get(newurl)
        time.sleep(sleep)
        commenttimes = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='x1jx94hy x12nagc']").find_element(By.TAG_NAME, value='h3')
        if '則留言' in commenttimes.text:
            Cc = commenttimes.text.replace('則留言', '')
            output['cC'] = Cc
    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in share()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def scroll_emoji(reactionID):
    count = 1
    last_height = chrome_browser.execute_script('return document.body.scrollHeight')
    for i in range(max_scroll):
        print(i)
        chrome_browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(sleep35)
        try:
            btn_more = chrome_browser.find_element(By.ID, value='reaction_profile_pager' + str(reactionID))
            ActionChains(chrome_browser).move_to_element(btn_more).perform()
            btn_more.click()
            f = open('./time.txt', 'a', encoding='utf-8')
            f.write('時間：' + str(time.ctime()) + ' emoji click ' + str(count) + '\n')
            f.close()
            count += 1
            time.sleep(sleep35)
        except exceptions.StaleElementReferenceException:
            btn_more = chrome_browser.find_element(By.ID, value='reaction_profile_pager' + str(reactionID))
            ActionChains(chrome_browser).move_to_element(btn_more).perform()
            btn_more.click()
            f = open('./time.txt', 'a', encoding='utf-8')
            f.write('時間：' + str(time.ctime()) + ' emoji click ' + str(count) + '\n')
            f.close()
            count += 1
            time.sleep(sleep35)
        except IndexError:
            break
        except exceptions.ElementNotInteractableException:
            break
        except exceptions.NoSuchElementException:
            break
        new_height = chrome_browser.execute_script('return document.body.scrollHeight')
        if new_height == last_height:  #不再刷新
            break
        last_height = new_height

def emoji_list(reactionID, emoji_userlist, emoji_count, post_id):
    reaction = chrome_browser.find_element(By.ID, value='reaction_profile_browser' + str(reactionID))
    userlist = reaction.find_elements(By.CLASS_NAME, value='_1uja')
    emoji_count = len(userlist)
    for index, user in enumerate(userlist):
        userData = {}
        userData['userName'] = user.find_element(By.CSS_SELECTOR, value="[class='_4mn c']").find_element(By.TAG_NAME, value='a').text
        userurl = user.find_element(By.CLASS_NAME, value='_4mn').find_element(By.TAG_NAME, value='a').get_attribute('href')
        userData['post_id'] = post_id
        userData['url'] = FBUserNormalized(userurl)
        # 取得URL切出ID
        hadID = False
        anchor_split = userData['url'].split('&')
        id_regex = re.compile(r'id=(.*)')
        for string in anchor_split:
            match = id_regex.search(string)
            if match != None:
                userData['userID'] = match.group(1)
                hadID = True
                break
            else:
                continue
        if(hadID == False):
            try:
                div = user.find_element(By.CSS_SELECTOR, value="[class='_4mq ext']")
                like_thumb = div.find_element(By.CLASS_NAME, value='like_thumb_container')
                data_store = like_thumb.get_attribute('data-store')
                data_json = json.loads(data_store)
                userData['userID'] = str(data_json['pageID'])
                hadID = True
            except exceptions.NoSuchAttributeException as e:
                hadID = False
            except exceptions.NoSuchElementException as e:
                hadID = False
        if(hadID == False):
            try:
                div = user.find_element(By.CSS_SELECTOR, value="[class='_4mq ext']")
                data_store = div.get_attribute('data-store')
                data_json = json.loads(data_store)
                userData['userID'] = str(data_json['subject_id'])
                hadID = True
            except exceptions.NoSuchAttributeException as e:
                hadID = False
            except exceptions.NoSuchElementException as e:
                hadID = False
        if hadID == True:
            emoji_userlist.append(userData)
        else:
            emoji_userlist.append(userData)
    return emoji_userlist, emoji_count

def emoji_angry(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 444813342392137):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Angry'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Angry'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_fighting(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 613557422527858):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Fighting'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Fighting'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_haha(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 115940658764963):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Haha'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Haha'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_like(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 1635855486666999):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Like'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Like'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_love(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 1678524932434102):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Love'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Love'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_sad(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 908563459236466):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Sad'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Sad'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def emoji_wow(output, post_id):
    try:
        chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_45m8']").click()
        time.sleep(sleep)
        div = chrome_browser.find_element(By.CLASS_NAME, value='scrollAreaColumn')
        span = div.find_elements(By.CLASS_NAME, value='_10tn')

        for index, i in enumerate(span):
            emoji_userlist = []
            emoji_count = 0
            if index == 0: # 跳過{'reactionID':'all'}
                continue
            attr = i.get_attribute('data-store')
            attr_json = json.loads(attr)
            reactionID = attr_json['reactionID']
            if (reactionID == 478547315650144):
                i.click()
                time.sleep(sleep)
                scroll_emoji(reactionID)
                emoji_userlist, emoji_count = emoji_list(reactionID, emoji_userlist, emoji_count, post_id)
                output['Wow'] = emoji_userlist
            else:
                continue
    except exceptions.NoSuchElementException as e:
        output['Wow'] = []
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in emojiID()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def resetComment():
    output = {}
    output['attachment_type']= ''
    output['attachment_url']= ''
    output['image_links']= []
    output['url']= ''
    output['data_category'] = ''
    output['from_id']= ''
    output['comment_identity']= 'FacebookComment'
    output['from_name']= ''
    output['userURL']= ''
    output['id_Token']= ''
    output['comment_time']= ''
    output['comment_id']= ''
    output['post_id']= ''
    output['body']= ''
    output['nLevel']=1
    output['parent_CommentToken']= ''
    output['image_alts']= []
    output['main_image']= ''
    output['cL'] = 0
    output['cA'] = 0
    output['cD'] = 0
    output['cH'] = 0
    output['cO'] = 0
    output['cW'] = 0
    output['cU'] = 0
    output['cS'] = 0
    output['cC'] = 0
    output['cR']= 0
    output['cT']= 0
    return output

def resetMetadata():
    output = {}
    output['from_name'] = ''
    output['body'] = ''
    output['title'] = ''
    output['hashtag'] = []
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['related_link'] = []
    output['image_link'] = []
    output['cL'] = ''
    output['cA'] = ''
    output['cD'] = ''
    output['cH'] = ''
    output['cO'] = ''
    output['cW'] = ''
    output['cU'] = ''
    output['cS'] = ''
    output['cC'] = ''
    output['source'] = ''
    output['track_time'] = ''
    output['crawler_identity'] = 'FacebookMetadata'
    output['page_category'] = ''
    output['cR']= '0'
    output['cT']= '0'
    output['page_id'] = ''
    output['page_name'] = ''
    return output

def resetShare():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['cs'] = 0
    output['cS'] = ''
    output['Share'] = []
    return output

def resetAngry():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['ca'] = 0
    output['Angry'] = []
    return output

def resetFighting():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['cu'] = 0
    output['Fighting'] = []
    return output

def resetHaha():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['ch'] = 0
    output['Haha'] = []
    return output

def resetLike():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['cl'] = 0
    output['Like'] = []
    return output

def resetLove():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['co'] = 0
    output['Love'] = []
    return output

def resetSad():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['cd'] = 0
    output['Sad'] = []
    return output

def resetWow():
    output = {}
    output['post_id'] = ''
    output['post_time'] = ''
    output['from_id'] = ''
    output['url'] = ''
    output['Wow'] = []
    return output

def scroll_share():
    count = 1
    last_height = chrome_browser.execute_script('return document.body.scrollHeight')
    for i in range(max_scroll):
        chrome_browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(sleep35)
        try:
            btn_more = chrome_browser.find_element(By.ID, value='m_more_item')
            ActionChains(chrome_browser).move_to_element(btn_more).perform()
            btn_more.click()
            f = open('./time.txt', 'a', encoding='utf-8')
            f.write('時間：' + str(time.ctime()) + ' share click ' + str(count) + '\n')
            f.close()
            count += 1
            time.sleep(sleep35)
        except exceptions.StaleElementReferenceException:
            btn_more = chrome_browser.find_element(By.ID, value='m_more_item')
            ActionChains(chrome_browser).move_to_element(btn_more).perform()
            btn_more.click()
            f = open('./time.txt', 'a', encoding='utf-8')
            f.write('時間：' + str(time.ctime()) + ' share click ' + str(count) + '\n')
            f.close()
            count += 1
            time.sleep(sleep35)
        except IndexError:
            break
        except exceptions.ElementNotInteractableException:
            break
        except exceptions.NoSuchElementException:
            break
        new_height = chrome_browser.execute_script('return document.body.scrollHeight')
        if new_height == last_height:  #不再刷新
            break
        last_height = new_height

def share(output, post_id):
    try:
        sharetimes = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='_43lx _55wr']")
        shareanchor = sharetimes.find_element(By.TAG_NAME, value='a')
        shareanchor.click()
        time.sleep(sleep)
        scroll_share()
        time.sleep(sleep)
        userlist = chrome_browser.find_elements(By.CLASS_NAME, value='_1uja')
        sharecount = 0
        sharelist = []
        for user in userlist:
            shareuserData = {}
            hadID = False
            shareuserData['userName'] = user.find_element(By.CLASS_NAME, value='_4mn').find_element(By.TAG_NAME, value='a').text
            useranchor = user.find_element(By.CLASS_NAME, value='_4mn').find_element(By.TAG_NAME, value='a').get_attribute('href')
            shareuserData['url'] = FBUserNormalized(useranchor)
            shareuserData['post_id'] = post_id
            anchor_split = useranchor.split('&')
            id_regex = re.compile(r'id=(.*)')
            for string in anchor_split:
                match = id_regex.search(string)
                if match != None:
                    shareuserData['userID'] = match.group(1)
                    hadID = True
                    break
                else:
                    continue
            if(hadID == False):
                try:
                    div = user.find_element(By.CSS_SELECTOR, value="[class='_4mq ext']")
                    like_thumb = div.find_element(By.CLASS_NAME, value='like_thumb_container')
                    data_store = like_thumb.get_attribute('data-store')
                    if data_store != None:
                        data_json = json.loads(data_store)
                        shareuserData['userID'] = str(data_json['subject_id'])
                        hadID = True
                except exceptions.NoSuchElementException as e:
                    hadID = False
                except exceptions.NoSuchAttributeException as e:
                    hadID = False
                except KeyError:
                    shareuserData['userID']=''
                except TypeError:
                    shareuserData['userID']=''
            if(hadID == False):
                try:
                    div = user.find_element(By.CSS_SELECTOR, value="[class='_4mq ext']")
                    data_store = div.get_attribute('data-store')
                    data_json = json.loads(data_store)
                    shareuserData['userID'] = str(data_json['subject_id'])
                    hadID = True
                except exceptions.NoSuchAttributeException as e:
                    hadID = False
                except exceptions.NoSuchElementException as e:
                    hadID = False
                except KeyError:
                    shareuserData['userID']=''
                except TypeError:
                    shareuserData['userID']=''
            if hadID == True:
                sharelist.append(shareuserData)
                sharecount += 1
            else:
                sharelist.append(shareuserData)
                sharecount += 1
        output['cs'] = sharecount
        output['Share'] = sharelist

    except exceptions.NoSuchElementException as e:
        f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
        msg = 'NoSuchElementException in share()'
        f.write('錯誤：' + msg + ' ')
        f.write('時間：' + str(time.ctime()) + ' ')
        f.write('錯誤資訊：'+ str(e.args) + '\n')
        f.close()
        chrome_browser.save_screenshot('./Error/FB/' + str(time.ctime()).replace(':', '.') + '.png')

def comment_log(output, url, AC, author_id, metaoutput, server):
    newurl = url
    if 'm.facebook' in url:
        newurl = url.replace('m.facebook.com','www.facebook.com')
    elif 'mbasic.facebook' in url:
        newurl = url.replace('mbasic','www')
    chrome_browser.get(newurl)
    time.sleep(sleep)
    
    mostrelated = chrome_browser.find_elements(By.CSS_SELECTOR, value="[class='x6s0dn4 x78zum5 xdj266r x11i5rnm xat24cr x1mh8g0r xe0p6wg']")
    for i in mostrelated:
        if i.text == '最相關':
            ActionChains(chrome_browser).move_to_element(i).perform()
            i.click()
            time.sleep(sleep)
            break
    newest = chrome_browser.find_elements(By.CSS_SELECTOR, value="[class='x78zum5 xdt5ytf xz62fqu x16ldp7u']")
    for i in newest:
        if '所有' in i.text:
            ActionChains(chrome_browser).move_to_element(i).perform()
            i.click()
            time.sleep(sleep)
            break
    
    # 點及查看更多
    last_height = chrome_browser.execute_script('return document.body.scrollHeight')
    while (True):
        try:
            btn_more = chrome_browser.find_elements(By.CSS_SELECTOR, value="[class='x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz x6s0dn4 xi81zsa x1iyjqo2 xs83m0k xsyo7zv xt0b8zv']")
            chrome_browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            if '留言' not in btn_more[-1].text:
                ActionChains(chrome_browser).move_to_element(btn_more[-1]).perform()
                time.sleep(sleep)
                break
            ActionChains(chrome_browser).move_to_element(btn_more[-1]).perform()
            btn_more[-1].click()
            time.sleep(sleep)
            new_height = chrome_browser.execute_script('return document.body.scrollHeight')
            if new_height == last_height:  #不再刷新        
                break
            last_height = new_height
        except exceptions.ElementClickInterceptedException as e:
            chrome_browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            ActionChains(chrome_browser).move_to_element(btn_more[-1]).perform()
            btn_more[-1].click()
            time.sleep(sleep)
        except exceptions.StaleElementReferenceException as e:
            time.sleep(sleep)
            btn_more = chrome_browser.find_elements(By.CSS_SELECTOR, value="[class='x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz x6s0dn4 xi81zsa x1iyjqo2 xs83m0k xsyo7zv xt0b8zv']")
            chrome_browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            ActionChains(chrome_browser).move_to_element(btn_more[-1]).perform()
            btn_more[-1].click()
            time.sleep(sleep)
        # 更改帳號狀態避免被取用
        cnxn = pyodbc.connect(connectionString)
        cursor = cnxn.cursor()
        updateAcLastModified = """update uniqueDB.dbo.Account set status = 1, LastModifiedDT = getdate() where AC = ?"""
        update_insert = (AC)
        try:
            cursor.execute(updateAcLastModified, update_insert)
            cursor.commit()
        except pyodbc.IntegrityError:
            with open('error.txt', 'w', encoding='utf-8') as f:
                f.write(pyodbc.ProgrammingError.args)
        cnxn.close()
    commentlist = chrome_browser.find_element(By.CSS_SELECTOR, value="[class='x1jx94hy x12nagc']").find_elements(By.TAG_NAME, value='li')
    print( 'commentlist', len(commentlist))
    for index, comment in enumerate(commentlist):
        ActionChains(chrome_browser).move_to_element(comment).perform()
        try:#第二層
            last_height = chrome_browser.execute_script('return document.body.scrollHeight')
            while(True):#第二層點開
                try:
                    reply_more = comment.find_element(By.CSS_SELECTOR, value="[class='x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz x6s0dn4 xi81zsa x1iyjqo2 xs83m0k xsyo7zv xt0b8zv']")
                    if '查看' in reply_more.text:
                        ActionChains(chrome_browser).move_to_element(reply_more).perform()
                        time.sleep(1)
                        reply_more.click()
                        time.sleep(sleep)
                    elif '隱藏' in reply_more.text:
                        break
                    else:
                        ActionChains(chrome_browser).move_to_element(reply_more).perform()
                        time.sleep(1)
                        reply_more.click()
                        time.sleep(sleep)
                    new_height = chrome_browser.execute_script('return document.body.scrollHeight')
                    if new_height == last_height:  #不再刷新        
                        break
                    last_height = new_height
                except exceptions.NoSuchElementException as e:
                    break
                # 更改帳號狀態避免被取用
                cnxn = pyodbc.connect(connectionString)
                cursor = cnxn.cursor()
                updateAcLastModified = """update uniqueDB.dbo.Account set status = 1, LastModifiedDT = getdate() where AC = ?"""
                update_insert = (AC)
                try:
                    cursor.execute(updateAcLastModified, update_insert)
                    cursor.commit()
                except pyodbc.IntegrityError:
                    with open('error.txt', 'w', encoding='utf-8') as f:
                        f.write(pyodbc.ProgrammingError.args)
                cnxn.close()
            replylist = comment.find_element(By.CSS_SELECTOR, value="[class='xdj266r xexx8yu x4uap5 x18d9i69 xkhd6sd']").find_element(By.TAG_NAME, value='ul').find_elements(By.TAG_NAME, value='li')
            for reply in replylist:
                last_height = chrome_browser.execute_script('return document.body.scrollHeight')
                while(True):#第三層點開
                    try:
                        replymore_part2 = reply.find_element(By.CSS_SELECTOR, value="[class='x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz x6s0dn4 xi81zsa x1iyjqo2 xs83m0k xsyo7zv xt0b8zv']")
                        if '隱藏' in replymore_part2.text:
                            break
                        else:
                            ActionChains(chrome_browser).move_to_element(replymore_part2).perform()
                            time.sleep(1)
                            replymore_part2.click()
                            time.sleep(sleep)
                        new_height = chrome_browser.execute_script('return document.body.scrollHeight')
                        if new_height == last_height:  #不再刷新        
                            break
                        last_height = new_height
                    except exceptions.NoSuchElementException as e:
                        break
                    # 更改帳號狀態避免被取用
                    cnxn = pyodbc.connect(connectionString)
                    cursor = cnxn.cursor()
                    updateAcLastModified = """update uniqueDB.dbo.Account set status = 1, LastModifiedDT = getdate() where AC = ?"""
                    update_insert = (AC)
                    try:
                        cursor.execute(updateAcLastModified, update_insert)
                        cursor.commit()
                    except pyodbc.IntegrityError:
                        with open('error.txt', 'w', encoding='utf-8') as f:
                            f.write(pyodbc.ProgrammingError.args)
                    cnxn.close()
        except exceptions.NoSuchElementException as e:
            continue

    browser_log = chrome_browser.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    newevents = []
    errorevent = []
    third = []
    for event in events:
        if 'Network.response' in event['method']:
            try:
                if (event['params']['response']['url'] == 'https://www.facebook.com/api/graphql/'):
                    try:
                        body = chrome_browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': event['params']['requestId']})
                        newevents.append(body)
                    except exceptions.WebDriverException:
                        continue
            except KeyError:
                continue
    print(len(newevents))
    for event in newevents:
        body = event['body'].replace('\r\n', '@@')
        body = body.split('@@')
        for b in body:
            try:
                data = json.loads(b)
            except:
                print(b)
                break
            try:
                if (data['data']['node']['__typename'] == 'Feedback'):#1和2
                    node = data['data']['node']
                    comment = node['display_comments']['edges']
                    errorevent.append(comment)
            except KeyError:
                pass
            try:
                if (data['data']['feedback'] != None):#第3層
                    feedback = data['data']['feedback']
                    reply = feedback['display_comments']['edges']
                    third.append(reply)
            except KeyError:
                pass
    Outputlist = []
    print(len(errorevent))
    for e in errorevent:
        # 更改帳號狀態避免被取用
        cnxn = pyodbc.connect(connectionString)
        cursor = cnxn.cursor()
        updateAcLastModified = """update uniqueDB.dbo.Account set status = 1, LastModifiedDT = getdate() where AC = ?"""
        update_insert = (AC)
        try:
            cursor.execute(updateAcLastModified, update_insert)
            cursor.commit()
        except pyodbc.IntegrityError:
            with open('error.txt', 'w', encoding='utf-8') as f:
                f.write(pyodbc.ProgrammingError.args)
        cnxn.close()
        for data in e:
            try:
                print(data['node']['id'])
            except TypeError:
                continue
            output = resetComment()
            output = metaoutput
            # 留言者ID
            userID = data['node']['author']['id']
            # comment_identity
            if (userID == author_id):
                comment_identity = 'owner'
            else:
                comment_identity = 'visit'
            # 留言者Name
            userName = data['node']['author']['name']
            # 留言者URL
            userURL = data['node']['author']['url']
            # 留言ID token
            comment_id = data['node']['id']
            # 留言時間
            comment_time = data['node']['created_time']
            # 留言ID
            legacy_token = data['node']['legacy_token']
            # 貼文id 短
            parent_feedbackID = data['node']['parent_feedback']['share_fbid']
            # 留言內容
            try:
                comment_body = data['node']['body_renderer']['text']
            except KeyError:
                comment_body = 'null'
            except TypeError:
                comment_body = 'null'
            nLevel = 0
            # 上層留言
            parent_CommentID = ''
            if (data['node']['comment_parent'] != None):
                nLevel = 2
                parent_CommentID = data['node']['comment_parent']['id']
            else:
                nLevel = 1
            # 留言影片/圖片
            output['attachment_type'] = ''
            output['attachment_url'] = ''
            output['image_links'] = []
            attachments = data['node']['attachments']
            for attachment in attachments:
                try:
                    output['attachment_type'] = attachment['style_type_renderer']['attachment']['media']['__typename']
                    output['attachment_url'] = attachment['style_type_renderer']['attachment']['media']['image']['uri']
                    output['image_links'].append(attachment['style_type_renderer']['attachment']['media']['image']['uri'])
                except:
                    pass
                try:
                    output['attachment_type'] = attachment['style_type_renderer']['attachment']['target']['__typename']
                    output['attachment_url'] = attachment['style_type_renderer']['attachment']['media']['fallback_image']['uri']
                    output['image_links'].append(attachment['style_type_renderer']['attachment']['media']['fallback_image']['uri'])
                except:
                    pass
            #留言url
            Commenturls = data['node']['comment_action_links_renderer']['comment']['commentActionLinks']
            for Commenturl in Commenturls:
                if (Commenturl['__typename'] == 'XFBCommentTimeStampActionLink'):
                    try:
                        output['url'] = Commenturl['comment']['url']
                    except:
                        output['url'] = ''
                # comment reaction
                output['cL'] = 0
                output['cU'] = 0
                output['cO'] = 0
                output['cH'] = 0
                output['cA'] = 0
                output['cW'] = 0
                output['cD'] = 0
                output['cS'] = 0
                output['cC'] = 0
                if (Commenturl['__typename'] == 'XFBCommentReactionActionLink'):
                    reactionlist = Commenturl['comment']['feedback']['top_reactions']['edges']
                    for reaction in reactionlist:
                        try:
                            reaction_id = reaction['node']['id']
                            reaction_count = reaction['reaction_count']
                            if(reaction_id == '1635855486666999'):#讚
                                output['cL'] = reaction_count
                            elif(reaction_id == '613557422527858'):#加油
                                output['cU'] = reaction_count
                            elif(reaction_id == '1678524932434102'):#愛心
                                output['cO'] = reaction_count
                            elif(reaction_id == '115940658764963'):#哈
                                output['cH'] = reaction_count
                            elif(reaction_id == '444813342392137'):#怒
                                output['cA'] = reaction_count
                            elif(reaction_id == '478547315650144'):#哇
                                output['cW'] = reaction_count
                            elif(reaction_id == '908563459236466'):#嗚
                                output['cD'] = reaction_count
                            else:
                                continue
                        except KeyError:
                            output['cL'] = 0
                            output['cU'] = 0
                            output['cO'] = 0
                            output['cH'] = 0
                            output['cA'] = 0
                            output['cW'] = 0
                            output['cD'] = 0

            output['data_category'] = 'comment'
            output['from_id'] = userID
            output['comment_identity']= comment_identity
            output['from_name'] = userName
            output['userURL'] = userURL
            output['id_Token'] = comment_id
            # 時間戳轉日期時間
            struct_time = time.localtime(comment_time) # 轉成時間元組
            timeString = time.strftime('%Y-%m-%d %H:%M:%S', struct_time) # 轉成字串
            output['comment_time'] = timeString
            output['comment_id'] = legacy_token
            output['post_id'] = parent_feedbackID
            output['body'] = comment_body
            output['nLevel'] = nLevel
            output['parent_CommentToken'] = parent_CommentID
            output['image_alts']= []
            output['main_image']= ''
            Outputlist.append(output)
            # post to server
            try:
                output = json.dumps(output, ensure_ascii=False).encode('utf-8')
                requests.post( server, data=output)
            except:
                statusCode = 400
                print(statusCode)

            cnxn = pyodbc.connect(connectionString)
            cursor = cnxn.cursor()
            insertComment = '''
                declare @re bit
                set nocount on
                exec IntelligentCrawler.dbo.xp_insertFB_CommentWithLog @userID=?, @userName=?, @userURL=?, @comment_id=?, @comment_timestamp=?,	@legacy_token=?, @comment_body=?, @nLevel=?, @post_id=?, @parent_CommentID=?, @repeat=@re output
                select @re
            ''' 
            Comment_value = (userID, userName, userURL, comment_id, comment_time, legacy_token, comment_body, nLevel, parent_feedbackID, parent_CommentID)
            try:
                cursor.execute(insertComment, Comment_value)
                result = cursor.fetchall()
                cursor.commit()
            except pyodbc.IntegrityError:
                with open('error.txt', 'w', encoding='utf-8') as f:
                    f.write(pyodbc.ProgrammingError.args)
            cnxn.close()
    print(len(third))
    third = json.dumps(third, ensure_ascii=False)
    fw = open('third2.json', 'w', encoding='utf-8')
    fw.write(third)
    fw.close()
    for t in third:
        # 更改帳號狀態避免被取用
        cnxn = pyodbc.connect(connectionString)
        cursor = cnxn.cursor()
        updateAcLastModified = """update uniqueDB.dbo.Account set status = 1, LastModifiedDT = getdate() where AC = ?"""
        update_insert = (AC)
        try:
            cursor.execute(updateAcLastModified, update_insert)
            cursor.commit()
        except pyodbc.IntegrityError:
            with open('error.txt', 'w', encoding='utf-8') as f:
                f.write(pyodbc.ProgrammingError.args)
        cnxn.close()
        for data in t:
            try:
                print(data['node']['id'])
            except TypeError:
                continue
            output = resetComment()
            output = metaoutput

            # 留言者ID
            userID = data['node']['author']['id']
            # comment_identity
            if (userID == author_id):
                comment_identity = 'owner'
            else:
                comment_identity = 'visit'
            # 留言者Name
            userName = data['node']['author']['name']
            # 留言者URL
            userURL = data['node']['author']['url']
            # 留言ID token
            comment_id = data['node']['id']
            # 留言時間
            comment_time = data['node']['created_time']
            # 留言ID
            legacy_token = data['node']['legacy_token']
            # 貼文id 短
            parent_feedbackID = data['node']['parent_feedback']['share_fbid']
            # 留言內容
            try:
                comment_body = data['node']['body_renderer']['text']
            except KeyError:
                comment_body = 'null'
            except TypeError:
                comment_body = 'null'
            nLevel = 3
            # 上層留言
            parent_CommentID = ''
            if (data['node']['comment_parent'] != None):
                parent_CommentID = data['node']['comment_parent']['id']
            # 留言影片/圖片
            output['attachment_type'] = ''
            output['attachment_url'] = ''
            output['image_links'] = []
            attachments = data['node']['attachments']
            for attachment in attachments:
                try:
                    output['attachment_type'] = attachment['style_type_renderer']['attachment']['media']['__typename']
                    output['attachment_url'] = attachment['style_type_renderer']['attachment']['media']['image']['uri']
                    output['image_links'].append(attachment['style_type_renderer']['attachment']['media']['image']['uri'])
                except:
                    pass
                try:
                    output['attachment_type'] = attachment['style_type_renderer']['attachment']['target']['__typename']
                    output['attachment_url'] = attachment['style_type_renderer']['attachment']['media']['fallback_image']['uri']
                    output['image_links'].append(attachment['style_type_renderer']['attachment']['media']['fallback_image']['uri'])
                except:
                    pass
            Commenturls = data['node']['comment_action_links_renderer']['comment']['commentActionLinks']
            for Commenturl in Commenturls:
                #留言url
                if (Commenturl['__typename'] == 'XFBCommentTimeStampActionLink'):
                    try:
                        output['url'] = Commenturl['comment']['url']
                    except:
                        output['url'] = ''
                # comment reaction
                output['cL'] = 0
                output['cU'] = 0
                output['cO'] = 0
                output['cH'] = 0
                output['cA'] = 0
                output['cW'] = 0
                output['cD'] = 0
                output['cS'] = 0
                output['cC'] = 0
                if (Commenturl['__typename'] == 'XFBCommentReactionActionLink'):
                    reactionlist = Commenturl['comment']['feedback']['top_reactions']['edges']
                    for reaction in reactionlist:
                        try:    
                            reaction_id = reaction['node']['id']
                            reaction_count = reaction['reaction_count']
                            if(reaction_id == '1635855486666999'):#讚
                                output['cL'] = reaction_count
                            elif(reaction_id == '613557422527858'):#加油
                                output['cU'] = reaction_count
                            elif(reaction_id == '1678524932434102'):#愛心
                                output['cO'] = reaction_count
                            elif(reaction_id == '115940658764963'):#哈
                                output['cH'] = reaction_count
                            elif(reaction_id == '444813342392137'):#怒
                                output['cA'] = reaction_count
                            elif(reaction_id == '478547315650144'):#哇
                                output['cW'] = reaction_count
                            elif(reaction_id == '908563459236466'):#嗚
                                output['cD'] = reaction_count
                            else:
                                continue
                        except KeyError:
                            output['cL'] = 0
                            output['cU'] = 0
                            output['cO'] = 0
                            output['cH'] = 0
                            output['cA'] = 0
                            output['cW'] = 0
                            output['cD'] = 0

            output['data_category'] = 'comment'
            output['from_id'] = userID
            output['comment_identity']= comment_identity
            output['from_name'] = userName
            output['userURL'] = userURL
            output['id_Token'] = comment_id
            # 時間戳轉日期時間
            struct_time = time.localtime(comment_time) # 轉成時間元組
            timeString = time.strftime('%Y-%m-%d %H:%M:%S', struct_time) # 轉成字串
            output['comment_time'] = timeString
            output['comment_id'] = legacy_token
            output['post_id'] = parent_feedbackID
            output['body'] = comment_body
            output['nLevel'] = nLevel
            output['parent_CommentToken'] = parent_CommentID
            output['image_alts']= []
            output['main_image']= ''
            Outputlist.append(output)
            # post to server
            try:
                output = json.dumps(output, ensure_ascii=False).encode('utf-8')
                requests.post( server, data=output)
            except:
                statusCode = 400
                print(statusCode)

            cnxn = pyodbc.connect(connectionString)
            cursor = cnxn.cursor()
            insertComment = '''
                declare @re bit
                set nocount on
                exec IntelligentCrawler.dbo.xp_insertFB_CommentWithLog @userID=?, @userName=?, @userURL=?, @comment_id=?, @comment_timestamp=?,	@legacy_token=?, @comment_body=?, @nLevel=?, @post_id=?, @parent_CommentID=?, @repeat=@re output
                select @re
            ''' 
            Comment_value = (userID, userName, userURL, comment_id, comment_time, legacy_token, comment_body, nLevel, parent_feedbackID, parent_CommentID)
            try:
                cursor.execute(insertComment, Comment_value)
                result = cursor.fetchall()
                cursor.commit()
            except pyodbc.IntegrityError:
                with open('error.txt', 'w', encoding='utf-8') as f:
                    f.write(pyodbc.ProgrammingError.args)
            cnxn.close()
    Outputlist = json.dumps(Outputlist, ensure_ascii=False)
    fw = open('CommentData0504.json', 'w', encoding='utf-8')
    fw.write(Outputlist)
    fw.close()

def PostToServer(output, oid, server):
    statusCode = 0
    try:
        output = json.dumps(output, ensure_ascii=False).encode('utf-8')
        requests.post( server, data=output)
    except:
        statusCode = 400
        print(statusCode)

    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.cursor()
    if statusCode == 0:
        SQL_hadPost = '''
            set nocount on;
            exec uniqueDB.dbo.xp_updateUTUOStatus @OID=?
        '''
        hadPost_value = (oid)
        cursor.execute(SQL_hadPost, hadPost_value)
        cursor.commit()
    cursor.commit()
    cnxn.close()

def PostCommentToServer(oid):
    statusCode = 0
    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.cursor()
    if statusCode == 0:
        SQL_hadPost = '''
            set nocount on;
            exec uniqueDB.dbo.xp_updateUTUOStatus @OID=?
        '''
        hadPost_value = (oid)
        cursor.execute(SQL_hadPost, hadPost_value)
        cursor.commit()
    cursor.commit()
    cnxn.close()

def writeJSONMetadata(output, oid, server):
    f = open('Metadata.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONShare(output, oid, server):#Fieldbits 9
    f = open('Share.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONAngry(output, oid, server):#Fieldbits 2
    f = open('Angry.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONFighting(output, oid, server):#Fieldbits 3
    f = open('Fighting.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONHaha(output, oid, server):#Fieldbits 4
    f = open('Haha.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONLike(output, oid, server):#Fieldbits 5
    f = open('Like.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONLove(output, oid, server):#Fieldbits 6
    f = open('Love.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONSad(output, oid, server):#Fieldbits 7
    f = open('Sad.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def writeJSONWow(output, oid, server):#Fieldbits 8
    f = open('Wow.json', 'w', encoding='utf-8')
    json_output = json.dumps(output, ensure_ascii=False)
    f.write(json_output)
    f.close()

    PostToServer(output, oid, server)

def Comment(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)

    writeJSONMetadata(output, oid, server)
    author_id = output['from_id']
    metaoutput = {
        'source': output['source'],
        'track_time': output['track_time'],
        'crawler_identity': 'FacebookComment',
        'page_category': output['page_category'],
        'post_id': output['post_id'],
        'post_time': output['post_time'],
        'page_id': output['page_id'],
        'page_name': output['page_name']
    }
    
    comment_log(output, url, AC, author_id, metaoutput, server)
    PostCommentToServer(oid)

def Wow(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)

    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookWow'

    metadata(metaoutput, url, oid)
    emoji_wow(metaoutput, post_id)
    writeJSONWow(metaoutput, oid, server)

def Sad(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookSad'

    metadata(metaoutput, url, oid)
    emoji_sad(metaoutput, post_id)
    writeJSONSad(metaoutput, oid, server)

def Love(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookLove'

    metadata(metaoutput, url, oid)
    emoji_love(metaoutput, post_id)
    writeJSONLove(metaoutput, oid, server)

def Like(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookLike'

    metadata(metaoutput, url, oid)
    emoji_like(metaoutput, post_id)
    writeJSONLike(metaoutput, oid, server)

def Haha(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookHaha'

    metadata(metaoutput, url, oid)
    emoji_haha(metaoutput, post_id)
    writeJSONHaha(metaoutput, oid, server)

def Fighting(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookFighting'

    metadata(metaoutput, url, oid)
    emoji_fighting(metaoutput, post_id)
    writeJSONFighting(metaoutput, oid, server)

def Angey(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookAngey'

    metadata(metaoutput, url, oid)
    emoji_angry(metaoutput, post_id)
    writeJSONAngry(metaoutput, oid, server)

def Share(url, oid, AC, server):
    output = resetMetadata()
    metadata(output, url, oid)
    body(output)
    photo(output)
    video(output)
    tcs(output)
    emoji_basic(output)
    tcc(output, url)
    writeJSONMetadata(output, oid, server)
    post_id = output['post_id']
    metaoutput = output
    metaoutput['crawler_identity'] = 'FacebookShare'

    metadata(metaoutput, url, oid)
    share(metaoutput, post_id)
    writeJSONShare(metaoutput, oid, server)
 
try:
    options = Options()
    options.add_argument("--start-maximized")  #最大化視窗
    options.add_argument("--incognito")#開啟無痕模式
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
    options.add_argument('--user-agent=%s' % user_agent)
    webdriver_path = ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    chrome_browser = webdriver.Chrome(service=webdriver_path, options = options, desired_capabilities=caps)
    chrome_browser.get('https://m.facebook.com/home.php')
    time.sleep(sleep)
    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.cursor()
    SQLString_insert = '''set nocount on;exec uniqueDB.dbo.xp_UpdateUserQueueTaskStatus'''
    try:
        cursor.execute(SQLString_insert)
        row = cursor.fetchall()
        articlelist = row
        cursor.commit()
    except pyodbc.IntegrityError:
        with open('error.txt', 'w', encoding='utf-8') as f:
            f.write(pyodbc.ProgrammingError.args)
    cnxn.close()
    if articlelist[0][0] is not None:
        AC, PWD = login()
        time.sleep(sleep)
        print(articlelist)
        for index, url in enumerate(articlelist):
            try:
                if('@@share' in url[1]):
                    url[1] = url[1].replace('@@share','')
                    Share(url[1], url[0], AC, url[2])
                elif ('@@angry' in url[1]):
                    url[1] = url[1].replace('@@angry','')
                    Angey(url[1], url[0], AC, url[2])
                elif ('@@comment' in url[1]):
                    url[1] = url[1].replace('@@comment','')
                    Comment(url[1], url[0], AC, url[2])
                elif ('@@fighting' in url[1]):
                    url[1] = url[1].replace('@@fighting','')
                    Fighting(url[1], url[0], AC, url[2])
                elif ('@@haha' in url[1]):
                    url[1] = url[1].replace('@@haha','')
                    Haha(url[1], url[0], AC, url[2])
                elif ('@@like' in url[1]):
                    url[1] = url[1].replace('@@like','')
                    Like(url[1], url[0], AC, url[2])
                elif ('@@love' in url[1]):
                    url[1] = url[1].replace('@@love','')
                    Love(url[1], url[0], AC, url[2])
                elif ('@@sad' in url[1]):
                    url[1] = url[1].replace('@@sad','')
                    Sad(url[1], url[0], AC, url[2])
                elif ('@@wow' in url[1]):
                    url[1] = url[1].replace('@@wow','')
                    Wow(url[1], url[0], AC, url[2])
            except exceptions.NoSuchElementException as e:
                cnxn = pyodbc.connect(connectionString)
                cursor = cnxn.cursor()
                try:
                    SQLString = '''update uniqueDB.dbo.Object set status = -1 where OID = ?''' 
                    values = (url[0])
                    print('ERROR！')
                    cursor.execute(SQLString, values)
                    cursor.commit()
                except pyodbc.IntegrityError:
                    with open('error.txt', 'w', encoding='utf-8') as f:
                        f.write(pyodbc.ProgrammingError.args)
                cnxn.close()
                chrome_browser.save_screenshot('./Error/FB' + str(time.ctime()).replace(':', '.') + '.png')
        cnxn = pyodbc.connect(connectionString)
        cursor = cnxn.cursor()
        SQLString_insert = '''
        declare @result bit, @re bit
        exec uniqueDB.dbo.xp_updateAccountState @Account=?, @PWD=?, @result=@re output
        select @re
        ''' 
        updateAccountState_input = (AC, PWD)
        try:
            cursor.execute(SQLString_insert, updateAccountState_input)
            result = cursor.fetchone()
            if (result[0] == True):
                print('Success')
            else:
                print('Error')
        except pyodbc.IntegrityError:
            with open('error.txt', 'w', encoding='utf-8') as f:
                f.write(pyodbc.ProgrammingError.args)
        cursor.commit()
        cnxn.close()
    chrome_browser.delete_all_cookies()
    chrome_browser.quit()
except exceptions.NoSuchElementException as e:
    f = open('FB_ErrorText.txt', 'a', encoding='utf-8')
    msg = '最外層NoSuchElementException'
    f.write('錯誤：' + msg + ' ')
    f.write('時間：' + str(time.ctime()) + ' ')
    f.write('錯誤資訊：'+ str(e.args) + '\n')
    f.close()
    chrome_browser.save_screenshot('./Error/FB' + str(time.ctime()).replace(':', '.') + '.png')
    chrome_browser.delete_all_cookies()
    chrome_browser.quit()