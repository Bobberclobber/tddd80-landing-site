__author__ = 'josfa'

from flask import Flask, render_template, request, jsonify

import smtplib
import db
import facebook_integration
import twitter_integration

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/init_db')
def init_db():
    db.init()
    return "db setup"


@app.route('/_get_test_user')
def get_test_user():
    test_dict = {"username": [{"bleh": "Bleh"}, {"foo": "Bar"}, "Meh"], "email": "E-Mail", "id": "User ID"}
    return jsonify(test_dict)


@app.route('/api/groups')
def json_groups():
    group_name_list = []
    for key in db.get_groups():
        group_name_list += [{"name": key}]
    return jsonify(groups=group_name_list)


@app.route('/api/groups/<group_name>')
def json_specific_group(group_name):
    group_exists = False
    groups = db.get_groups()

    for key in groups:
        if key == group_name:
            group_exists = True

    if group_exists:
        member_list = []
        for member in groups[group_name]:
            member_name = member[0] + " " + member[1]
            member_e_mail = member[2]
            member_accepted = member[3]
            member_list += [{"name": member_name, "e-mail": member_e_mail, "accepted": member_accepted}]
        return jsonify(members=member_list)
    else:
        return "Invalid Group Name"


# This is a function which imitates the json_specific_group()-function's
# method to create a list of member. This function, instead of returning a
# json-object instead returns that list.
# This function exists to help with checking that json_specific_group() creates the
# correct input for the json-object it creates.
def get_json_member_list(group_name):
    group_exists = False
    groups = db.get_groups()

    for key in groups:
        if key == group_name:
            group_exists = True

    if group_exists:
        member_list = []
        for member in groups[group_name]:
            member_name = member[0] + " " + member[1]
            member_e_mail = member[2]
            member_accepted = member[3]
            member_list += [{"name": member_name, "e-mail": member_e_mail, "accepted": member_accepted}]
        return member_list
    else:
        return "Invalid Group Name"


@app.route('/admin_page')
def admin_page():
    return render_template("admin_page.html")


@app.route('/create_groups')
def create_group():
    return render_template("create_groups.html", member_list=db.get_all_members())


@app.route('/add_group', methods=['POST'])
def add_group():
    group_name = request.form['new_group_name']
    group_member_list = []
    for member in request.form.getlist('member'):
        temp_list = member.split(':', 3)
        group_member_list.append(temp_list)
    db.add_to_group(group_name, group_member_list)
    return render_template("groups_added.html")


@app.route('/add_member')
def add_member():
    return render_template("add_member.html", groups_list=db.get_groups(), member_list=db.get_all_members())


@app.route('/add_new_member', methods=['POST'])
def add_new_member():
    group_name = request.form['group_name']
    group_member_list = []
    for member in request.form.getlist('member'):
        temp_list = member.split(':', 3)
        group_member_list.append(temp_list)
    db.add_to_group(group_name, group_member_list)
    return render_template("members_added.html")


@app.route('/view_groups')
def view_group():
    return render_template("view_groups.html", groups_list=db.get_groups())


@app.route('/e_mail_group', methods=['POST'])
def e_mail_group():
    group_name = request.form['group_name']
    member_list = db.get_groups()[group_name]
    for member in member_list:
        user_e_mail = member[2]
        e_mail_user(user_e_mail, "localhost:5000/invitation_accepted/" + group_name + "/" + user_e_mail)
        db.status_e_mail_sent(user_e_mail, group_name)
    return render_template("e_mail_sent.html")


def e_mail_user(user_e_mail, url):
    SERVER = "smtp.gmail.com"
    FROM = "josfa969@student.liu.se"
    TO = [user_e_mail]
    SUBJECT = "Hello!"
    TEXT = "Hello World! - " + url

    # Prepare actual message
    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail
    server = smtplib.SMTP(SERVER, 587)
    server.starttls()
    server.login('j.g.fagerstrom@gmail.com', 'In666Flames666')
    server.sendmail(FROM, TO, message)
    server.quit()


@app.route('/invitation_accepted/<group_name>/<user_e_mail>')
def invitation_accepted(group_name, user_e_mail):
    db.status_invitation_accepted(user_e_mail, group_name)
    return render_template("invitation_accepted.html")


@app.route('/about_me')
def about_me():
    return render_template("about_me.html")


@app.route('/register_interest')
def register_interest():
    return render_template("register_interest.html", row_count=db.get_row_count())


# Retrievs the data from the registration form
@app.route('/add', methods=['POST'])
def add():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    e_mail = request.form['e_mail']
    country = request.form['country']
    city = request.form['city']
    friend_relative = request.form['friend_relative']
    google = request.form['google']
    facebook = request.form['facebook']
    twitter = request.form['twitter']
    search_engine = request.form['search_engine']
    other = request.form['other']
    other_text = request.form['other_text']

    # Checks if the e-mail has been entered already
    if db.email_exists(e_mail):
        return render_template("already_registered.html")
    else:
        db.add_data(first_name, last_name, e_mail, country, city, friend_relative, google, facebook, twitter,
                    search_engine,
                    other, other_text)
        # Posts a tweet
        tweet(first_name, last_name)
        return render_template("registry_complete.html", tweet_list=twitter_integration.get_tweet_list())


# Posts on the users facebook wall
@app.route('/publish_custom_story', methods=['POST'])
def publish_custom_story():
    oauth_token = request.cookies.get("oauth_token")
    return facebook_integration.publish_custom_story(oauth_token)


# Posts a tweet
@app.route('/tweet')
def tweet(f_name, l_name):
    twitter_integration.tweet(f_name, l_name, db.get_row_count())


if __name__ == '__main__':
    app.run(host='localhost')
