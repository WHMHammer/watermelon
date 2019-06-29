create database watermelon character set utf8mb4;

create table watermelon.users(
    id int not null auto_increment,
    -- user info
    username varchar(64) unique,
    email varchar(64) unique,
    avatar varchar(512),
    -- user status
    status varchar(32) default 'unverified',
    role varchar(32),
    -- password
    salt char(16),
    password_hash char(128),
    challenge char(16),
    primary key(id)
);

create table watermelon.sessions(
    user_id int not null,
    session char(16) not null,
    expire_time int(10) not null,
    foreign key(user_id) references watermelon.users(id)
);

create table watermelon.events(
    id int auto_increment,
    title varchar(32),
    description varchar(128),
    -- all times are in the form of unix_timestamp // 60, stored by int(8) data type
    end_time int(8),   -- end time of the whole event
    -- weekly schedules
    weekly0 int(8),
    weekly1 int(8),
    weekly2 int(8),
    weekly3 int(8),
    weekly4 int(8),
    weekly_window int(3),   -- in minutes
    -- monthly schedules
    monthly0 int(8),
    monthly_window int(3),  -- in minutes
    primary key(id)
);

create table watermelon.roles(
    event_id int not null,
    user_id int not null,
    role varchar(32) default 'subscriber',
    foreign key(event_id) references watermelon.events(id),
    foreign key(user_id) references watermelon.users(id)
);

create table watermelon.attendance(
    event_id int not null,
    user_id int not null,
    time int(8),
    foreign key(event_id) references watermelon.events(id),
    foreign key(user_id) references watermelon.users(id)
);
