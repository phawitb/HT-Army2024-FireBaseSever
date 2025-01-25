import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import requests
from datetime import datetime
import requests
import time

def is_internet_available(url='http://www.google.com'):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def wait_for_internet_connection():
    print("Checking for internet connection...")
    while not is_internet_available():
        print("No internet connection. Waiting...")
        time.sleep(5)  # Wait for 5 seconds before checking again
    print("Internet connection is available!")

wait_for_internet_connection()


TOKEN_GROUP_ALL = '2QsPCWXYqqOOc3RHnKyrGGxrpoOGOOIjwKSWCtGWD1S'

def line_noti(token,msg):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
    r = requests.post(url, headers=headers, data = {'message':msg})
    return r.text

def create_msg(x,unit):
    w = ''
    t = ''
    if x["flag"] == 'WHITE':
        w = '1/2'
        t = 'ต่อเนื่อง'
    elif x["flag"] == 'GREEN':
        w = '1/2'
        t = '50 นาที พัก: 10 นาที'
    elif x["flag"] == 'YELLOW':
        w = 1
        t = '45 นาที พัก: 15 นาที'
    elif x["flag"] == 'RED':
        w = 1
        t = '30 นาที พัก: 30 นาที'
    elif x["flag"] == 'BLACK':
        w = 1
        t = '20 นาที พัก: 40 นาที'
        
    msg = f'{unit}\n'
    msg += f'⛰สัญญาณธง: {x["flag"]}\n'
    msg += f'⛰อุณหภูมิ: {x["temperature"]} °C\n'
    msg += f'⛰ความชื้นสัมพัทธ์: {x["humidity"]} %\n'
    msg += f'⛰ปริมาณน้ำดื่ม: {w} ลิตร/ชม.\n'
    msg += f'⛰แนะนำให้ฝึก: {t}'

    return msg

def get_time():
    Times = []
    everyhour = False
    for k in db.reference("/UsersData").get().keys():
        ref = db.reference(f"/UsersData/{k}/config/time")
        data = ref.get()
        if data:
            Times += data
            
        ref = db.reference(f"/UsersData/{k}/config/everyhour/status")
        data = ref.get()
        if data:
            everyhour = True
            
        
    Times = [x for x in set(Times) if x]
    
    if everyhour:
        for i in range(0,24):
            if len(str(i)) == 1:
                Times.append(f'0{i}:00')
            else:
                Times.append(f'{i}:00')
    Times = set(Times)
    return Times      

INTERVALTIME_NOTIFY = 300 #sec
cred = credentials.Certificate('/home/phawit/Documents/HT-Army-FireBaseSever/ht-army-firebase-adminsdk-yfrij-c875f63e00.json')
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://ht-army-default-rtdb.asia-southeast1.firebasedatabase.app/'})




firsttime = True
sent = False

U = {}
IDKEYS = db.reference("/UsersData").get().keys()
for k in IDKEYS:
    u = db.reference(f"/UsersData/{k}/config/unit/name").get()
    U[k] = u
print('U',U)

line_noti(TOKEN_GROUP_ALL,'v2')
#delete history every saturday
timestamp = datetime.now().timestamp()
dt_object = datetime.fromtimestamp(timestamp)
day_of_week = dt_object.strftime("%A")
if day_of_week=='Saturday':
    for k in IDKEYS:
        ref_his = db.reference(f'/UsersData/{k}/historys')
        ref_his.delete()
    msg = f'delete all history! {day_of_week}'
    print(msg)
    line_noti(TOKEN_GROUP_ALL,msg)

while True:
    # try:
        if firsttime:
            T = get_time()
            firsttime = False

            print(f'HT-Army -->sever start!!! {T}')
            line_noti(TOKEN_GROUP_ALL,f'HT-Army -->sever start!!! {T}')
            

        time.sleep(10)

        if sent:
            if datetime.now().strftime("%H:%M") != now:
                now = datetime.now().strftime("%H:%M")
                sent = False
        else:
            now = datetime.now().strftime("%H:%M")

        if datetime.now().strftime("%M") == "29":
            T = get_time()
        

        # now = '08:00'
        if now in T and not sent:
        # while True:
        #     time.sleep(2)
            T = get_time()
            # for k in K:
            msg_status = ''
            for k in db.reference("/UsersData").get().keys():
                print('\nk',k)

                ref = db.reference(f"/UsersData/{k}/last")
                last = ref.get()
                #check online
                # print(float(last['timestamp']))
                print('last',last)
                if last and time.time() - float(last['timestamp']) < INTERVALTIME_NOTIFY:
                    print('online')
                    try:
                        msg_status += f'{U[k]} {k[:5]} ->🟢\n'
                    except:
                        pass

                    
                    #check time match
                    ref = db.reference(f"/UsersData/{k}/config/time")
                    t = ref.get()
                    print('tttt',t)
                    if t:
                        t = list(set(t))
                    else:
                        t = []

                    ref2 = db.reference(f"/UsersData/{k}/config/everyhour/status")
                    data = ref2.get()
                    if data:
                        for i in range(0,24):
                            if len(str(i)) == 1:
                                t.append(f'0{i}:00')
                            else:
                                t.append(f'{i}:00')

                    print('t',t)
                    t = [x for x in t if x]
                    if t:
                        if now in set(t):
                            print('match...',now)
                            # ref = db.reference(f"/UsersData/{k}/last")
                            # last = ref.get()
                            
                            # #check online
                            # print(float(last['timestamp']))
                            # if time.time() - float(last['timestamp']) < INTERVALTIME_NOTIFY:
                            #     print('online')
                                
                            #get token line
                            ref = db.reference(f"/UsersData/{k}/config/line")
                            token = ref.get()
                            #get unit name
                            ref = db.reference(f"/UsersData/{k}/config/unit/name")
                            unit = ref.get()
                            print(unit,token)
                            #create msg
                            msg = create_msg(last,unit)
                            print(msg)
                                
                            line_noti(TOKEN_GROUP_ALL,msg)
                            #line noti
                            for tok in token:
                                if tok:
                                    line_noti(tok,msg)

                    print('xxxx')
                else:
                    print('offline')
                    msg_status += f'{U[k]} {k[:5]} ->❌\n'
            line_noti(TOKEN_GROUP_ALL,msg_status)
                                    
            sent = True

    # except Exception as e:
    #     print('Error',e)
    #     time.sleep(10)




