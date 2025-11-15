-- SCHEMAS

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS friendship;

-- EXTENSION (UUID)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TABLE: auth.users

CREATE TABLE IF NOT EXISTS auth.users (
    id UUID primary key default uuid_generate_v4(),
    email varchar(320) unique not null,
    hashed_password varchar not null,
    is_active boolean not null default true,
    is_superuser boolean not null default false,
    is_verified boolean not null default false,
    role varchar(20) not null default 'student'
);

-- TABLE: friendship.friendships

CREATE TABLE IF NOT EXISTS friendship.friendships (
    id UUID primary key default uuid_generate_v4(),
    user_id UUID not null references auth.users(id) on delete cascade,
    friend_id UUID not null references auth.users(id) on delete cascade,
    friendship_status varchar(20) not null default 'pending',
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    constraint uq_user_friend unique (user_id, friend_id),
    constraint check_not_self_friend check (user_id <> friend_id)
);