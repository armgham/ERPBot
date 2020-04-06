# ERPBot
address of bot: https://telegram.me/guilan_sada_bot

commands for create database:
create table USER_DATA (user_id INT, data VARCHAR(10000));
create table CHAT_DATA (chat_id INT, data VARCHAR(100));
create table CONVERSATIONS (conversation_name VARCHAR(50));
create table PROXY (proxy VARCHAR(50));

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
