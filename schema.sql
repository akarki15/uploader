create table if not exists entries (
  id integer primary key autoincrement,
  filename text not null,
  annotation text,
  patientname text,
  patientid text
);

create table if not exists users (  
  username text primary key not null,
  pass text not null
);