-- DROP TABLE IF EXISTS users;

create table if not exists users (
       id integer primary key AUTOINCREMENT,
    fname text ,
    lname text,
    email text,
    registerNo text,
    pass text,
    confPass text
)

-- CREATE TABLE users (
--    id integer auto increment primary key,
--     fname text ,
--     lname text,
--     email text,
--     registerNo text,
--     pass text,
--     confPass text
-- );