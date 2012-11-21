drop table if exists weibosearch2;

create table author (
  id BIGINT not null,
  name VARCHAR(100) not null,
  url VARCHAR(500) not null,
  PRIMARY KEY (id)
) engine=innodb default charset=utf8;

CREATE INDEX author_id ON author (id);

create table feed (
  id BIGINT not null,
  author_id BIGINT,
  FOREIGN KEY (author_id) references author(id),
  content VARCHAR(500) not null,
  replies INTEGER,
  retweets INTEGER,
  timestamp TIMESTAMP,
  PRIMARY KEY (id)
) engine=innodb default charset=utf8;

CREATE INDEX feed_id on feed(id);