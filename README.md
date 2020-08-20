# SADABot
address of bot: https://telegram.me/guilan_sada_bot


## How to run

1. Install `python`(3), `pip`, `virtualenv`, MySQL, [phantomjs](https://phantomjs.org/quick-start.html) (add it to path variable) in your system.
2. Clone the project `https://github.com/armgham/ERPBot`.
3. Make development environment ready using commands below;

  ```bash
  git clone https://github.com/armgham/ERPBot && cd ERPBot
  virtualenv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
4. in the app folder, rename the `config.py.sample` to `config.py` and do proper changes.
5. db configs are in config.py. Create the db and grant all access to the specified user with specified password.
6. Run `python app/app.py`

## Run On Windows

If You're On A Windows Machine , Make Environment Ready By Following Steps Below:
1. Install `python`(3), `pip`, `virtualenv`, MySQL, [phantomjs](https://phantomjs.org/quick-start.html) (add it to path variable).
2. Clone the project using:  `git clone https://github.com/armgham/ERPBot`.
3. Make Environment Ready Like This:
``` Command Prompt
cd ERPBot
virutalenv -p "PATH\TO\Python.exe" build # Give Full Path To python.exe
build\Scripts\activate # Activate The Virutal Environment
pip install -r requirements.txt
```
4. in the app folder, rename the `config.py.sample` to `config.py` and do proper changes.
5. db configs are in config.py. Create the db and grant all access to the specified user with specified password.
6. Run `python app/app.py`


## Example of creating db and granting access:

> Note: this is just a sample. You have to find your own systems commands.

```
create database sadasql;
create user 'sadasql'@'localhost' identified by 'sadasql';
grant all privileges on sadasql.* to 'sadasql'@'localhost';
flush privileges;
use sadasql;

create table USER_DATA (user_id INT, data VARCHAR(10000));
create table CHAT_DATA (chat_id INT, data VARCHAR(100));
create table CONVERSATIONS (conversation_name VARCHAR(50));
create table PROXY (proxy VARCHAR(50));
```

## TODO

- [x] flush command handler
- [x] fix bugs! (when press get the edited table first time, ...)
- [x] a function to give telegram bot connection for other modules to send message ...
- [x] make phantomjs lighter and faster
- [x] send logs to users.
- [x] handle urllib3.connection.HTTPConnection(urllib3.exceptions.ProtocolError) error
- [x] find a way for debtor students
- [x] use requests for web-scrapping
- [x] memory management while using matplotlib
- [x] add_proxy command to use Iran_proxy_server (or pptp vpn) (to remove proxy use /addproxy without argument).
- [x] http to https
- [x] add button to select other terms!
- [x] show error of connection to user. (without Iran_proxy:[x] or maybe with proxy:[ ])
- [x] handle 'time_column_index' problem. (when table is empty)
- [x] show error of evalution
- [x] add a feature to fill evalList