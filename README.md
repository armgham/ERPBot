# ERPBot
address of bot: https://telegram.me/guilan_sada_bot

commands for create database:
create table USER_DATA (user_id INT, data VARCHAR(10000));
create table CHAT_DATA (chat_id INT, data VARCHAR(100));
create table CONVERSATIONS (conversation_name VARCHAR(50));

## TODO

- [x] flush command handler
- [x] fix bugs! (when press get the edited table first time, ...)
- [x] a function to give telegram bot connection for other modules to send message ...
- [x] make phantomjs lighter and faster
- [x] send logs to users.
- [ ] handle urllib3.connection.HTTPConnection error