create table if not exists entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

create table if not exists users (  
  username text primary key not null,
  pass text not null
);