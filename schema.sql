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
    end_time datetime,
    weekly0 datetime,
    weekly1 datetime,
    weekly2 datetime,
    weekly3 datetime,
    weekly4 datetime,
    weekly_window int(3),
    monthly0 datetime,
    monthly_window int(3),
    primary key(id)
);

create table watermelon.roles(
    event_id int not null,
    user_id int not null,
    role varchar(32) default 'subscriber',
    foreign key(event_id) references watermelon.events(id),
    foreign key(user_id) references watermelon.users(id)
);

create table watermelon.attendence(
    event_id int not null,
    user_id int not null,
    time datetime,
    foreign key(event_id) references watermelon.events(id),
    foreign key(user_id) references watermelon.users(id)
);
