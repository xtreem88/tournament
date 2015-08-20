-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- drop the database in case there is duplicate database name
DROP DATABASE IF EXISTS tournament;
-- create new database
CREATE DATABASE tournament;
-- connect to the database
\c tournament
-- table for players
CREATE TABLE players (
    id SERIAL primary key, 
    name text
    );

CREATE TABLE tournaments (
    id SERIAL primary key,
    name TEXT );

-- table for matches
CREATE TABLE matches (
    id SERIAL primary key, 
    tournament SERIAL references tournaments(id),
    winner SERIAL references players(id), 
    loser SERIAL references players(id),
    draw BOOLEAN
    );


CREATE TABLE scorecard (
    id SERIAL primary key, 
	tournament SERIAL references tournaments(id),
    player SERIAL references players(id), 
    score INTEGER,
    played INTEGER,
    bye INTEGER );


