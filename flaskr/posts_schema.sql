--TODO: UPDATE TO USE GOOD DATABASE CONVENTIONS. SEE https://stackoverflow.com/questions/7662/database-table-and-column-naming-conventions

drop table if exists Posts;
drop table if exists Tags;
drop table if exists PostsToTags;

create table Posts (
  post_id integer primary key autoincrement,
  post_title text not null unique,
  post_byline text not null,
  post_slug text not null,
  post_date date not null
);

create table Tags (
  tag_id integer primary key autoincrement,
  tag_title text not null unique,
  tag_slug text not null unique,
  tag_color text not null
);

-- TODO: INDEX? store by post_id, tag_id?
create table PostsToTags (
  post_slug text not null,
  tag_slug text not null,
  unique(post_slug, tag_slug)  -- TODO: ALSO MAKE PRIMARY KEY
);
