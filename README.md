# ERPBot
address of bot: https://telegram.me/guilan_sada_bot

commands for create database:
create table USER_DATA (user_id INT, data VARCHAR(10000));
create table CHAT_DATA (chat_id INT, data VARCHAR(100));
create table CONVERSATIONS (conversation_name VARCHAR(50));

## TODO

- [ ] flush command handler
- [ ] fix bugs! (when press get the edited table first time, ...)
- [ ] write a method return the bot object to other files can send_message ...
- [ ] make phantomjs lighter and faster

