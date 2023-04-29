from __future__ import unicode_literals
from keep_alive import keep_alive
import sys
import os
import time
from time import thread_time
import websockets
import asyncio
import json
import urllib
import random
import requests
from urllib.parse import urlencode
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

import base64
import textwrap
from io import BytesIO
from datetime import date
from pytz import timezone
from datetime import datetime
######### OTHERs ########
ID = "id"
NAME = "name"
USERNAME = "username"
PASSWORD = "password"
ROOM = "room"
TYPE = "type"
ROLE = "role"
HANDLER = "handler"
ALLOWED_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
########## ------- ##########

########## SOCKET ########
SOCKET_URL = os.getenv('WS_ADDRESS')

########## ------- ##########

######## MSGs #########
MSG_BODY = "body"
USER_ROLE = "role"
MSG_FROM = "from"
MSG_TO = "to"
MSG_TYPE_TXT = "text"
MSG_TYPE_IMG = "image"
MSG_TYPE_AUDIO = "audio"
MSG_URL = "url"
MSG_LENGTH = "length"
########## ------- ##########

######### Handlers #########
HANDLER_LOGIN = "login"
HANDLER_LOGIN_EVENT = "login_event"
HANDLER_ROOM_JOIN = "room_join"
HANDLER_ROOM_LEAVE = "room_leave"
HANDLER_ROOM_EVENT = "room_event"
HANDLER_ROOM_MESSAGE = "room_message"
HANDLER_CHAT_MESSAGE = "chat_message"
HANDLER_PROFILE_OTHER = "profile_other"
HANDLER_PROFILE_UPDATE = "profile_update"
EVENT_TYPE_SUCCESS = "success"
HANDLER_ROOM_ADMIN = "room_admin"
########## ------- ##########

######### CREDENTIALS AND ROOM SETTINGS - CHANGE THIS #########
BOT_MASTER_ID =  os.getenv('BOT_MASTER')
GROUP_TO_INIT_JOIN = "friends"
BOT_ID = os.getenv('BOT_ID')
BOT_MASTER = os.getenv('BOT_MASTER')
BOT_PWD = os.getenv('BOT_PWD')

########## ------- ##########

IMG_TYPE_PNG = "image/png"
IMG_TYPE_JPG = "image/jpeg"
IMG_BG_COLOR = "black"
TEXT_FONT_COLOR = "black"
AUDIO_DURATION = 0
last_played_song = None  # LAST PLAYED SONG
LAST_MUSIC_URL = ''
IMG_TXT_FONTS = r'fonts/Merienda-Regular.ttf'
is_wc_on = False
sys.setrecursionlimit(999999999)

TEMP_USERS = []
tempTarget = ""
tempMsg = ""
confMode = ""


def gen_random_str(length):
  return ''.join(random.choice(ALLOWED_CHARS) for i in range(length))


async def on_pvtMessage(ws, data):
  #print(data)
  global IMG_BG_COLOR
  global TEXT_FONT_COLOR
  global tempTarget
  global tempMsg
  global confMode
  #print(data)

  msg = data["body"]
  frm = data["from"]
  room = "friends"
  #print (msg)

  if msg.startswith("help") or msg.startswith("Help") or msg.startswith(
      "HELP"):
    print("in help")

    await send_pvt_msg(
      ws, frm,
      f"Welcome to Confession bot.\nCommands :\n.CONFESS MSG :  Set confess message \n.ACONFESS MSG : Confess Anonymously\nABOUT : To know about bot"
    )

  sentence = msg
  words_list = sentence.split()

  if words_list[0] == ".confess" or words_list[0] == ".CONFESS" or words_list[
      0] == ".Confess":
    tempTarget = frm
    tempMsg = msg[8:]
    confMode = ""
    confMode = "public"
    await get_room_users(ws, data)

  if words_list[0] == ".aconfess" or words_list[
      0] == ".ACONFESS" or words_list[0] == ".Aconfess":

    tempTarget = frm
    tempMsg = msg[9:]
    confMode = ""
    confMode = "anon"
    await get_room_users(ws, data)

  if msg.startswith(".rcu") or msg.startswith(".RCU"):
    with open("data.json", "r+") as file:
      data = file.read()
      json_dict = json.loads(data)
      print(json_dict)
      dataN1 = json_dict[0]['ogName']
      dataN2 = json_dict[1]['ogName']
      dataN3 = json_dict[2]['ogName']
      dataN4 = json_dict[3]['ogName']
      dataN5 = json_dict[4]['ogName']
      FullMsg = "Recent confessions by :\n1. " + dataN1 + "\n2. " + dataN2 + "\n3. " + dataN3 + "\n4. " + dataN4 + "\n5. " + dataN5
      await send_pvt_msg(ws, frm, FullMsg)

  if msg.startswith("about") or msg.startswith("About") or msg.startswith(
      "ABOUT"):
    await send_pvt_msg(
      ws, frm,
      "Name : Confession Bot\nVersion : 1.0\nWritten in Python 🐍\nDeveloper : Void\nContact : https://t.me/voidrulz\nPeople behind this project :\n1. αяуαи\n2. anthelios"
    )


async def on_RoomMessage(ws, data):
  #print(data)
  global IMG_BG_COLOR
  global TEXT_FONT_COLOR
  #print(data)

  msg = data[MSG_BODY]
  frm = data[MSG_FROM]
  room = data[ROOM]
  role = data[USER_ROLE]
  user_avi = data['avatar_url']

  if frm == BOT_ID:
    return

  if user_avi is None:
    return

  if msg.startswith("!kick "):
    target = msg[6:]
    await setKick(ws, room, target)

  if msg.startswith("help") or msg.startswith("Help") or msg.startswith(
      "HELP"):
    await send_group_msg(
      ws, room,
      f"Welcome to Confession bot.\nCommands :\n.CONFESS MSG :  Set confess message \n.ACONFESS MSG : Confess Anonymously\nABOUT : To know about bot"
    )

  sentence = msg
  words_list = sentence.split()

  if words_list[0] == ".confess" or words_list[0] == ".CONFESS" or words_list[
      0] == ".Confess":
    if role == "member" or role == "admin" or role == "owner" or role == "creator":
      conf = msg[8:]
      if len(conf) > 250:
        await send_group_msg(
          ws, room, frm + " limit exceeded! type msg upto 250 characters")
      else:
        currDate = datetime.now(
          timezone("Asia/Kolkata")).strftime('%B %d, %Y | %I:%M %p IST')
        with open("data.json", "r+") as file:
          data = file.read()
          json_dict = json.loads(data)
          json_dict.pop()
          file.close()
          json_dict.insert(0, {
            'ogName': frm,
            'name': frm,
            'msg': conf,
            'time': currDate
          })
        with open("data.json", 'r+') as file:
          data = json.load(file)
          data.clear()
          data = json_dict.copy()
          file.close()

        with open("data.json", 'w') as file:
          json.dump(data, file)

        dataN1 = json_dict[0]['name']
        dataM1 = json_dict[0]['msg']
        dataT1 = json_dict[0]['time']

        dataN2 = json_dict[1]['name']
        dataM2 = json_dict[1]['msg']
        dataT2 = json_dict[1]['time']

        dataN3 = json_dict[2]['name']
        dataM3 = json_dict[2]['msg']
        dataT3 = json_dict[2]['time']

        dataN4 = json_dict[3]['name']
        dataM4 = json_dict[3]['msg']
        dataT4 = json_dict[3]['time']

        dataN5 = json_dict[4]['name']
        dataM5 = json_dict[4]['msg']
        dataT5 = json_dict[4]['time']

        FullMsg = "<big><b>CONFESSIONS </b></big> <br><br><b>🔥 Message : </b>" + dataM1 + "<br><b>Author : </b><i>" + dataN1 + "</i><br><b>Time : </b><i> " + dataT1 + "</i><br>_________________________________________<br><b>Message : </b>" + dataM2 + "<br><b>Author : </b><i>" + dataN2 + "</i><br><b>Time : </b><i> " + dataT2 + "</i><br><br><b>Message : </b>" + dataM3 + "<br><b>Author : </b><i>" + dataN3 + "</i><br><b>Time : </b><i> " + dataT3 + "</i><br><br><b>Message : </b>" + dataM4 + "<br><b>Author : </b><i>" + dataN4 + "</i><br><b>Time : </b><i> " + dataT4 + "</i><br><br><b>Message : </b>" + dataM5 + "<br><b>Author : </b><i>" + dataN5 + "</i><br><b>Time : </b><i> " + dataT5 + "</i><br><b<br><br>"

      if conf is None or len(conf) == 0:
        await send_group_msg(
          ws, room,
          "Type '.CONFESS MSG' to confess\Example :\n.CONFESS I love you")
      else:
        await set_Subject(ws, room, FullMsg)
        file.close()

    else:
      await send_group_msg(
        ws, room, frm +
        " : your id must member to use this command\ncontact room admin/owner to get access"
      )

  if msg.startswith(".cru") or msg.startswith(".CRU"):
    with open("data.json", "r+") as file:
      data = file.read()
      json_dict = json.loads(data)
      print(json_dict)
      dataN1 = json_dict[0]['ogName']
      dataN2 = json_dict[1]['ogName']
      dataN3 = json_dict[2]['ogName']
      dataN4 = json_dict[3]['ogName']
      dataN5 = json_dict[4]['ogName']
      if frm == "void":
        FullMsg = "Recent confessions by :\n1. " + dataN1 + "\n2. " + dataN2 + "\n3. " + dataN3 + "\n4. " + dataN4 + "\n5. " + dataN5
        await send_group_msg(ws, room, FullMsg)

  if words_list[0] == ".aconfess" or words_list[
      0] == ".ACONFESS" or words_list[0] == ".Aconfess":
    if role == "member" or role == "admin" or role == "owner" or role == "creator":
      conf = msg[9:]
      if len(conf) > 250:
        await send_group_msg(
          ws, room, frm + " limit exceeded! type msg upto 250 characters")
      else:
        currDate = datetime.now(
          timezone("Asia/Kolkata")).strftime('%B %d, %Y | %I:%M %p IST')
        with open("data.json", "r+") as file:
          data = file.read()
          json_dict = json.loads(data)
          json_dict.pop()
          file.close()
          json_dict.insert(
            0, {
              'ogName': frm,
              'name': "Not Available",
              'msg': conf,
              'time': currDate
            })
        with open("data.json", 'r+') as file:
          data = json.load(file)
          data.clear()
          data = json_dict.copy()
          file.close()

        with open("data.json", 'w') as file:
          json.dump(data, file)

        dataN1 = json_dict[0]['name']
        dataM1 = json_dict[0]['msg']
        dataT1 = json_dict[0]['time']

        dataN2 = json_dict[1]['name']
        dataM2 = json_dict[1]['msg']
        dataT2 = json_dict[1]['time']

        dataN3 = json_dict[2]['name']
        dataM3 = json_dict[2]['msg']
        dataT3 = json_dict[2]['time']

        dataN4 = json_dict[3]['name']
        dataM4 = json_dict[3]['msg']
        dataT4 = json_dict[3]['time']

        dataN5 = json_dict[4]['name']
        dataM5 = json_dict[4]['msg']
        dataT5 = json_dict[4]['time']

        FullMsg = "<big><b>CONFESSIONS </b></big> <br><br><b>🔥 Message : </b>" + dataM1 + "<br><b>Author : </b><i>" + dataN1 + "</i><br><b>Time : </b><i> " + dataT1 + "</i><br>_________________________________________<br><b>Message : </b>" + dataM2 + "<br><b>Author : </b><i>" + dataN2 + "</i><br><b>Time : </b><i> " + dataT2 + "</i><br><br><b>Message : </b>" + dataM3 + "<br><b>Author : </b><i>" + dataN3 + "</i><br><b>Time : </b><i> " + dataT3 + "</i><br><br><b>Message : </b>" + dataM4 + "<br><b>Author : </b><i>" + dataN4 + "</i><br><b>Time : </b><i> " + dataT4 + "</i><br><br><b>Message : </b>" + dataM5 + "<br><b>Author : </b><i>" + dataN5 + "</i><br><b>Time : </b><i> " + dataT5 + "</i><br><b<br><br>"

      if conf is None or len(conf) == 0:
        await send_group_msg(
          ws, room,
          "Type '.ACONFESS MSG' to confess\Example :\n.ACONFESS I love you")
      else:
        await set_Subject(ws, room, FullMsg)
        file.close()

    else:
      await send_group_msg(
        ws, room, frm +
        " : your id must member to use this command\ncontact room admin/owner to get access"
      )

  if msg.startswith("about") or msg.startswith("About") or msg.startswith(
      "ABOUT"):
    await send_group_msg(
      ws, room,
      "Name : Confession Bot\nVersion : 1.0\nWritten in Python 🐍\nDeveloper : Void\nContact : https://t.me/voidrulz\nPeople behind this project :\n1. αяуαи\n2. anthelios"
    )


async def on_roomUsersList(ws, data):
  users = data['occupants']
  global tempMsg
  global tempTarget

  #print(users)

  def find(arr, id):
    for x in arr:
      #print(x)
      if x['username'] == id:
        return x

  bbb = find(users, tempTarget)
  print(tempTarget)
  print(bbb)

  if bbb == None:
    print(tempTarget)
    print("NA found")
    await send_pvt_msg(ws, tempTarget,
                       "You must be in the room to use this command")

  else:
    print("NOT NA")
    if bbb['role'] == "member" or bbb['role'] == "admin" or bbb[
        'role'] == "owner" or bbb['role'] == "creator":
      #conf = msg[8:]
      if len(tempMsg) > 250:
        await send_pvt_msg(
          ws, tempTarget,
          tempTarget + " limit exceeded! type msg upto 250 characters")
      else:
        currDate = datetime.now(
          timezone("Asia/Kolkata")).strftime('%B %d, %Y | %I:%M %p IST')
        with open("data.json", "r+") as file:
          data = file.read()
          json_dict = json.loads(data)
          json_dict.pop()
          file.close()
          if confMode == "public":
            json_dict.insert(
              0, {
                'ogName': tempTarget,
                'name': tempTarget,
                'msg': tempMsg,
                'time': currDate
              })

          if confMode == "anon":
            json_dict.insert(
              0, {
                'ogName': tempTarget,
                'name': "Not Available",
                'msg': tempMsg,
                'time': currDate
              })

        with open("data.json", 'r+') as file:
          data = json.load(file)
          data.clear()
          data = json_dict.copy()
          file.close()

        with open("data.json", 'w') as file:
          json.dump(data, file)

        dataN1 = json_dict[0]['name']
        dataM1 = json_dict[0]['msg']
        dataT1 = json_dict[0]['time']

        dataN2 = json_dict[1]['name']
        dataM2 = json_dict[1]['msg']
        dataT2 = json_dict[1]['time']

        dataN3 = json_dict[2]['name']
        dataM3 = json_dict[2]['msg']
        dataT3 = json_dict[2]['time']

        dataN4 = json_dict[3]['name']
        dataM4 = json_dict[3]['msg']
        dataT4 = json_dict[3]['time']

        dataN5 = json_dict[4]['name']
        dataM5 = json_dict[4]['msg']
        dataT5 = json_dict[4]['time']

        FullMsg = "<big><b>CONFESSIONS </b></big> <br><br><b>🔥 Message : </b>" + dataM1 + "<br><b>Author : </b><i>" + dataN1 + "</i><br><b>Time : </b><i> " + dataT1 + "</i><br>_________________________________________<br><b>Message : </b>" + dataM2 + "<br><b>Author : </b><i>" + dataN2 + "</i><br><b>Time : </b><i> " + dataT2 + "</i><br><br><b>Message : </b>" + dataM3 + "<br><b>Author : </b><i>" + dataN3 + "</i><br><b>Time : </b><i> " + dataT3 + "</i><br><br><b>Message : </b>" + dataM4 + "<br><b>Author : </b><i>" + dataN4 + "</i><br><b>Time : </b><i> " + dataT4 + "</i><br><br><b>Message : </b>" + dataM5 + "<br><b>Author : </b><i>" + dataN5 + "</i><br><b>Time : </b><i> " + dataT5 + "</i><br><b<br><br>"

      if tempMsg is None or len(tempMsg) == 0:
        await send_pvt_msg(
          ws, tempTarget,
          "Type '.CONFESS MSG' to confess\Example :\n.CONFESS I love you")
      else:
        await set_Subject(ws, "friends", FullMsg)
        file.close()

    else:
      await send_pvt_msg(
        ws, tempTarget,
        "Your id must member to use this command\ncontact room admin/owner to get access"
      )

  tempMsg = ""
  tempTarget = ""


async def get_room_users(ws, data):
  jsonbody = {
    "handler": "room_admin",
    "id": gen_random_str(20),
    "type": "occupants_list",
    "room": "friends",
    "t_username": "username",
    "t_role": "none"
  }
  await ws.send(json.dumps(jsonbody))


async def wc_user(ws, data):
  user = data[USERNAME]
  room = data[NAME]
  wcString = f"Hi {user} 😃\nWelcome to {room}\nI am a bot, helping people to confess 🙂\nType HELP to know more"
  #await send_group_msg(ws, room, wcString)


async def login(ws):
  jsonbody = {
    "handler": "login",
    "id": gen_random_str(20),
    "username": BOT_ID,
    "password": BOT_PWD
  }
  #print(jsonbody)
  await ws.send(json.dumps(jsonbody))


async def grant_member(ws, data):
  user = data[USERNAME]
  room = data[NAME]
  await setMember(ws, room, user)


async def join_group(ws, group):
  jsonbody = {HANDLER: HANDLER_ROOM_JOIN, ID: gen_random_str(20), NAME: group}
  await ws.send(json.dumps(jsonbody))


async def rejoin_group(ws, group):
  await leave_group(ws, group)
  time.sleep(1)
  await join_group(ws, group)


def get_as_base64(url):
  return base64.b64encode(requests.get(url).content)


async def send_pvt_msg(ws, to, msg):
  jsonbody = {
    "handler": HANDLER_CHAT_MESSAGE,
    "id": gen_random_str(20),
    "to": to,
    "type": "text",
    MSG_URL: "",
    "body": msg,
    MSG_LENGTH: ""
  }
  #jsonbody = {HANDLER: HANDLER_CHAT_MESSAGE, ID: gen_random_str(20), MSG_TO: to, type: "text", body: msg}
  await ws.send(json.dumps(jsonbody))


async def update_profile(ws, group, url):
  print(
    get_as_base64(
      "https://static.remove.bg/sample-gallery/graphics/bird-thumbnail.jpg"))
  jsonbody = {
    HANDLER: HANDLER_PROFILE_UPDATE,
    ID: gen_random_str(20),
    TYPE: "photo",
    "value": ""
  }
  await ws.send(json.dumps(jsonbody))


async def send_group_msg(ws, room, msg):
  jsonbody = {
    HANDLER: HANDLER_ROOM_MESSAGE,
    ID: gen_random_str(20),
    ROOM: room,
    TYPE: MSG_TYPE_TXT,
    MSG_URL: "",
    MSG_BODY: msg,
    MSG_LENGTH: ""
  }
  await ws.send(json.dumps(jsonbody))


async def set_Subject(ws, room, msg):
  jsonbody = {
    HANDLER: HANDLER_ROOM_ADMIN,
    ID: gen_random_str(20),
    TYPE: "change_subject",
    ROOM: room,
    "t_username": msg,
    "t_role": "none"
  }
  await ws.send(json.dumps(jsonbody))


async def setMember(ws, room, target):
  jsonbody = {
    HANDLER: HANDLER_ROOM_ADMIN,
    ID: gen_random_str(20),
    TYPE: "change_role",
    ROOM: room,
    "t_username": target,
    "t_role": "member"
  }
  await ws.send(json.dumps(jsonbody))


async def setAdmin(ws, room, target):
  jsonbody = {
    HANDLER: HANDLER_ROOM_ADMIN,
    ID: gen_random_str(20),
    TYPE: "change_role",
    ROOM: room,
    "t_username": target,
    "t_role": "admin"
  }
  await ws.send(json.dumps(jsonbody))


async def setKick(ws, room, target):
  jsonbody = {
    HANDLER: HANDLER_ROOM_ADMIN,
    ID: gen_random_str(20),
    TYPE: "kick",
    ROOM: room,
    "t_username": target,
    "t_role": "none"
  }
  await ws.send(json.dumps(jsonbody))


async def setOwner(ws, room, target):
  jsonbody = {
    HANDLER: HANDLER_ROOM_ADMIN,
    ID: gen_random_str(20),
    TYPE: "change_role",
    ROOM: room,
    "t_username": target,
    "t_role": "owner"
  }
  await ws.send(json.dumps(jsonbody))


async def start_bot():
  try:
    websocket = await websockets.connect(SOCKET_URL, ssl=True)
    await login(websocket)
  except:
    print("Error")
    time.sleep(10)
    await start_bot()

  while True:
    websocket = await websockets.connect(SOCKET_URL, ssl=True)
    await login(websocket)
    if not websocket.open:
      try:
        websocket = await websockets.connect(SOCKET_URL, ssl=True)
        print('Websocket is NOT connected. Reconnecting...')
        time.sleep(15)
        #await login(websocket)
      except websockets.exceptions.WebSocketException as ex:
        time.sleep(15)
        await start_bot()
        print("Error: " + ex)

    try:
      async for payload in websocket:
        if payload is not None:
          data = json.loads(payload)
          # print(data)
          handler = data[HANDLER]

          if handler == HANDLER_LOGIN_EVENT and data[
              TYPE] == EVENT_TYPE_SUCCESS:
            print("Logged In SUCCESS")
            await join_group(websocket, GROUP_TO_INIT_JOIN)

          elif handler == HANDLER_ROOM_EVENT and data[TYPE] == MSG_TYPE_TXT:
            await on_RoomMessage(websocket, data)

          elif handler == "chat_message" and data[TYPE] == "text":
            await on_pvtMessage(websocket, data)

          elif handler == "room_admin" and data[TYPE] == "occupants_list":
            await on_roomUsersList(websocket, data)

          if handler == HANDLER_ROOM_EVENT and data[TYPE] == "user_joined":
            await wc_user(websocket, data)

            #if handler == HANDLER_ROOM_EVENT and data[
            #    TYPE] == "user_joined" and data[ROLE] == "none":
            #await grant_member(websocket, data)

            #if handler == HANDLER_ROOM_EVENT and data[TYPE] == "you_joined" and data[USERNAME] == BOT_ID:
            #await send_group_msg(websocket, GROUP_TO_INIT_JOIN, "Ready!\nType HELP to get started")

            print("Owner")
          #await send_group_msg websocket, GROUP_TO_INIT_JOIN, "Hi I am bot. confession bot. helping people to confess their feelings.\nGrant me owner to activate this bot" )

          if handler == HANDLER_ROOM_EVENT and data[
              TYPE] == "role_changed" and data["new_role"] == "owner" and data[
                "t_username"] == BOT_ID:
            await send_group_msg(websocket, GROUP_TO_INIT_JOIN,
                                 data["actor"] + " Thank you for the owner 😃")
            await rejoin_group(websocket, GROUP_TO_INIT_JOIN)

    except:
      print('Error receiving message from websocket.')
      #time.sleep(10)
      #await start_bot()


if __name__ == "__main__":
  keep_alive()
  loop = asyncio.get_event_loop()
  time.sleep(10)
  loop.run_until_complete(start_bot())
  loop.run_forever()
