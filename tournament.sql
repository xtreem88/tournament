-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- table for players
CREATE TABLE players (
    id SERIAL primary key, 
    name text
    );

-- table for matches
CREATE TABLE matches (
    id SERIAL primary key, 
    tournament INTEGER,
    winner INTEGER, 
    loser INTEGER,
    draw BOOLEAN
    );

CREATE TABLE tournaments (
	id SERIAL primary key,
    name TEXT );


CREATE TABLE scorecard (
    id SERIAL primary key, 
	tournament INTEGER,
    player INTEGER, 
    score INTEGER,
    played INTEGER,
    bye INTEGER );


