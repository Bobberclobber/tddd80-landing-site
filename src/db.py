__author__ = "josfa"

import sqlite3
from flask import g


def connect_db():
    conn = sqlite3.connect("database.db")
    return conn


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_db()
    return db


def init():
    c = get_db()
    c.execute("DROP TABLE IF EXISTS entries")
    c.execute("DROP TABLE IF EXISTS groups")
    c.execute(
        "CREATE TABLE entries (first_name TEXT, last_name TEXT, e_mail TEXT, country TEXT, city TEXT, friend_relatives TEXT, google TEXT, facebook TEXT, twitter TEXT, search_engine TEXT, other TEXT, other_text TEXT)")
    c.execute("CREATE TABLE groups (first_name TEXT, last_name TEXT, e_mail TEXT, accepted INTEGER, group_name TEXT)")
    c.commit()


def add_data(first_name, last_name, e_mail, country, city, friend_relative, google, facebook, twitter, search_engine,
             other, other_text):
    c = get_db()
    c.execute(
        "INSERT INTO entries (first_name,last_name,e_mail,country,city,friend_relatives,google,facebook,twitter,search_engine,other,other_text) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (first_name, last_name, e_mail, country, city, friend_relative, google, facebook, twitter, search_engine, other,
         other_text))
    c.commit()


def email_exists(e_mail):
    c = get_db()
    cur = c.execute("SELECT e_mail FROM entries")
    for row in cur:
        if e_mail in row:
            return True
    return False


def get_row_count():
    c = get_db()
    cur = c.execute("SELECT * FROM entries")
    row_count = 0
    for row in cur:
        if row is not None:
            row_count += 1
    return row_count


def get_all_members():
    c = get_db()
    cur = c.execute("SELECT first_name, last_name, e_mail FROM entries")
    member_list = []
    for row in cur:
        member_list += (row,)
    return member_list


def add_to_group(group_name, member_list):
    c = get_db()
    for member in member_list:
        if not already_in_group(member[2], group_name):
            c.execute("INSERT INTO groups (first_name,last_name,e_mail,accepted,group_name) VALUES (?,?,?,?,?)",
                      (member[0], member[1], member[2], -1, group_name))
    c.commit()


def already_in_group(e_mail, group_name):
    c = get_db()
    cur = c.execute("SELECT e_mail,group_name FROM groups")
    for row in cur:
        if e_mail in row and group_name in row:
            return True
    return False


def get_groups():
    c = get_db()
    cur = c.execute("SELECT * FROM groups")
    group_dict = {}
    group_list = []
    temp_id = ""
    for row in cur:
        if temp_id != row[4]:
            if temp_id != "":
                group_dict[temp_id] = group_list
                group_list = []
            temp_id = row[4]
        group_list += (row,)
    group_dict[temp_id] = group_list
    return group_dict


def status_e_mail_sent(user_e_mail, group_name):
    c = get_db()
    args = (user_e_mail, group_name)
    c.execute("UPDATE groups SET accepted=0 WHERE e_mail=? AND group_name=? AND accepted=-1", args)
    c.commit()


def status_invitation_accepted(user_e_mail, group_name):
    c = get_db()
    args = (user_e_mail, group_name)
    c.execute("UPDATE groups SET accepted=1 WHERE e_mail=? AND group_name=? AND accepted=0", args)
    c.commit()


def destroy():
    c = get_db()
    c.execute("DROP TABLE IF EXISTS entries")
    c.execute("DROP TABLE IF EXISTS groups")
    c.commit()


def close():
    get_db().close()