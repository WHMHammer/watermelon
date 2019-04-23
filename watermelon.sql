create database watermelon character set utf8mb4;

create table watermelon.users(
    id int auto_increment primary key,
    -- user info
    username varchar(64) unique,
    email varchar(64) unique,
    avatar varchar,
    -- user status
    catagory varchar(32),
    status varchar(32) default 'unverified',
    -- security
    salt char(16),
    password_hash char(128),
    last_login_time int(10) default 0,
    session char(16),
    challenge char(16)
);

create table watermelon.events(
    id int auto_increment primary key,
    name varchar(32),
    -- owner_id int,
    -- subscriber_id varchar,
    description varchar(128),
    -- begin datetime,
    end_time datetime,
    weekly_0_begin datetime,
    weekly_0_end datetime,
    weekly_1_begin datetime,
    weekly_1_end datetime,
    weekly_2_begin datetime,
    weekly_2_end datetime,
    weekly_3_begin datetime,
    weekly_3_end datetime,
    weekly_4_begin datetime,
    weekly_4_end datetime,
    monthly_0_begin datetime,
    monthly_0_end datetime
);

creat table watermelon.subscriptions(
    event_id varchar(32),
    user_id int,
    role varchar(32),
)

create table watermelon.attendence(
    id int auto_increment primary key,
    event_id int,
    user_id int,
    time, datetime
);