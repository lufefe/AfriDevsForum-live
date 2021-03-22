import requests
from flask import Blueprint, redirect, flash
from flask import render_template, request, current_app, g, url_for
from flask_login import current_user
from flask_mail import Message
from flaskblog import mail
from sqlalchemy import or_

from flaskblog import db
from flaskblog.decorators import admin_required
from flaskblog.models import Post, Tag, User
from flaskblog.posts.forms import SearchForm

app = current_app._get_current_object()

main = Blueprint('main', __name__)


@main.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.search_form = SearchForm()


# CHECK USER LOCATION - IP ADDRESS.
def get_user_ip(ip_address):
    try:
        response = requests.get(
            "http://ip-api.com/json/{}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,query".format(
                ip_address))
        data = response.json()
        return data
    except Exception as e:
        return "Unknown"


def subscribe_user(email, user_group, api_key):
    resp = requests.post(f"https://api.eu.mailgun.net/v3/lists/{user_group}/members",
                         auth = ("api", api_key),
                         data = {"subscribed": True, "address": email})

    print(resp.status_code)


@main.route("/")
@main.route("/home")
def home():
    # TODO: use HTTP_X_FORWARDED_FOR to get ip address on nginx (Production)
    ip_address = request.remote_addr
    user_data = get_user_ip(ip_address)

    user_count = db.session.query(User).count()
    post_count = db.session.query(Post).count()
    # we will use the paginate function to limit the number of posts appearing in the home page - ...
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page,
                                                                  per_page = current_app.config[
                                                                      'FLASKY_POSTS_PER_PAGE'])

    # tags = Tag.query.distinct(Tag.name).limit(8)
    tags = db.session.query(Tag.name).distinct().limit(6)
    return render_template('home.html', posts = posts, tags = tags, user_count = user_count, post_count = post_count)


# TODO -> You have successfully subscribed message
@main.route("/subscribe", methods = ["GET", "POST"])
def subscribe():
    if request.method == "POST":
        email = request.form.get('submail')
        subscribe_user(email,
                       "newsletter@app.afridevsforum.com",
                       app.config['MAIL_API_KEY'])
        flash('You have successfully subscribed!', 'success')
        return redirect(url_for('main.home'))


@main.route("/about")
def about():
    return render_template('about.html', title = 'About')


@main.route("/advertising")
def advertising():
    return render_template('advertising.html', title = 'Advertising')


@main.route("/contact")
def contact():
    return render_template('contactus.html', title = 'Contact Us')


@main.route("/admin")
@admin_required
def admin():
    pass


@main.route('/search_results/<query>')
# @login_required
def search_results(query):
    print(query)
    page = request.args.get('page', 1, type = int)
    query_formatted = "%{}%".format(query)
    query_test = Post.query.filter(or_(Post.title.like(query_formatted), Post.content.like(query_formatted)))

    return render_template('search_results.html', posts = query_test, query = query)


@main.route('/search', methods = ['POST'])
# @login_required
def search():
    query = request.form.get('query')
    if not query:
        return redirect(url_for('main.home'))
    return redirect(url_for('main.search_results', query = query))


@main.route("/adscontact", methods = ["GET", "POST"])
def adscontact():
    if request.method == 'POST':
        name = request.form['name']
        ad_email = request.form['ad_email']
        message = request.form['message']
        subject = 'Ads Enquiry - ' + name
        msg = Message(subject = subject,
                      sender = (name, app.config['MAIL_USERNAME']),
                      recipients = ['ads@afridevsforum.com'])
        message_body = message + '\n\nContact: ' + ad_email
        msg.body = message_body
        mail.send(msg)
        flash('Thank you for showing interest in advertising, our team will contact you!', 'success')
        return redirect(url_for('home.advertising'))


@main.route("/contactnow", methods = ["GET", "POST"])
def contactnow():
    if request.method == 'POST':
        name = request.form['name']
        c_email = request.form['c_email']
        message = request.form['message']
        subject = request.form['subject']
        msg = Message(subject = subject,
                      sender = (name, app.config['MAIL_USERNAME']),
                      recipients = ['info@afridevsforum.com'])
        message_body = message + '\n\nContact: ' + c_email
        msg.body = message_body
        mail.send(msg)
        flash('Your message has been sent, our team will contact you!', 'success')
        return redirect(url_for('main.contact'))

#
# @main.route("/")
# def maintenance():
#     return render_template('under_maintenance.html')
