DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS program;
DROP TABLE IF EXISTS celebrity;
DROP TABLE IF EXISTS perform;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS favorite;
DROP VIEW IF EXISTS favorite_program;
DROP VIEW IF EXISTS perform_info;

CREATE TABLE stations (id int, name text, address text);
CREATE TABLE program (id INTEGER primary key AUTOINCREMENT, name text UNIQUE, station_id int , start text, end text, day text, description text);
CREATE TABLE celebrity (id INTEGER primary key AUTOINCREMENT, name text, company text);
CREATE TABLE perform (program_id int, celebrity_id int, role text, primary key(program_id, celebrity_id));
CREATE TABLE user (id INTEGER primary key AUTOINCREMENT, username text, email text, introduction text, password text, is_public int default 1, pict text, UNIQUE(username, email));
CREATE TABLE favorite (user_id int, program_id int, is_favorite int, primary key(user_id, program_id));

CREATE VIEW favorite_program as select u.id as user_id, u.username as user_name, p.id as program_id, p.name as program_name , p.station_id as channnel, s.name as station, p.start, p.end, p.day from user u, program p, stations s, favorite f where (f.user_id = u.id and f.program_id = p.id and f.is_favorite=1) and p.station_id = s.id;
CREATE VIEW perform_info as select p.id as program_id, p.name as program, c.id as celebrity_id, c.name as celebrity, f.role as role from program p, celebrity c, perform f where f.program_id = p.id and f.celebrity_id = c.id ;
