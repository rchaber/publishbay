config = {

# environment this app is running on: localhost, testing, production
'environment': "localhost",

# webapp2 sessions
'webapp2_extras.sessions': {'secret_key': 'gs5tJE$5n6jsfrg'},

# webapp2 authentication
'webapp2_extras.auth': {'user_model': 'boilerplate.models.User',
                        'cookie_name': 'session_name'},

# jinja2 templates
'webapp2_extras.jinja2': {'template_path': ['templates','boilerplate/templates', 'admin/templates'],
                          'environment_args': {'extensions': ['jinja2.ext.i18n']}},

# application name
'app_name': "PublishBay",

# the default language code for the application.
# should match whatever language the site uses when i18n is disabled
'app_lang': 'en_US',

# Locale code = <language>_<territory> (ie 'en_US')
# to pick locale codes see http://cldr.unicode.org/index/cldr-spec/picking-the-right-language-code
# also see http://www.sil.org/iso639-3/codes.asp
# Language codes defined under iso 639-1 http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# Territory codes defined under iso 3166-1 alpha-2 http://en.wikipedia.org/wiki/ISO_3166-1
# disable i18n if locales array is empty or None
'locales': ['en_US'],

# contact page email settings
'contact_sender': "rchaber@gmail.com",
'contact_recipient': "PUT_RECIPIENT_EMAIL_HERE",

# Password AES Encryption Parameters
'aes_key': "770A8A65DA156D24EE2A093277530142",
'salt': "4gTd6",

# get your own consumer key and consumer secret by registering at https://dev.twitter.com/apps
# callback url must be: http://[YOUR DOMAIN]/login/twitter/complete
'twitter_consumer_key': 'PUT_YOUR_TWITTER_CONSUMER_KEY_HERE',
'twitter_consumer_secret': 'PUT_YOUR_TWITTER_CONSUMER_SECRET_HERE',

#Facebook Login
# get your own consumer key and consumer secret by registering at https://developers.facebook.com/apps
#Very Important: set the site_url= your domain in the application settings in the facebook app settings page
# callback url must be: http://[YOUR DOMAIN]/login/facebook/complete
'fb_api_key': 'PUT_YOUR_FACEBOOK_PUBLIC_KEY_HERE',
'fb_secret': 'PUT_YOUR_FACEBOOK_PUBLIC_KEY_HERE',

#Linkedin Login
#Get you own api key and secret from https://www.linkedin.com/secure/developer
'linkedin_api': 'PUT_YOUR_LINKEDIN_PUBLIC_KEY_HERE',
'linkedin_secret': 'PUT_YOUR_LINKEDIN_PUBLIC_KEY_HERE',

# Github login
# Register apps here: https://github.com/settings/applications/new
'github_server': 'github.com',
'github_redirect_uri': 'http://www.example.com/social_login/github/complete',
'github_client_id': 'PUT_YOUR_GITHUB_CLIENT_ID_HERE',
'github_client_secret': 'PUT_YOUR_GITHUB_CLIENT_SECRET_HERE',

# get your own recaptcha keys by registering at http://www.google.com/recaptcha/
'captcha_public_key': "6LfXYNwSAAAAAEoJDglhwZKYEgygSLa5qYQeJGfL",
'captcha_private_key': "6LfXYNwSAAAAAAQFjA66WcyLUOnK0ei3hJXRJjih",

# Leave blank "google_analytics_domain" if you only want Analytics code
'google_analytics_domain': "publishbay.com",
'google_analytics_code': "UA-XXXXX-X",

# add status codes and templates used to catch and display errors
# if a status code is not listed here it will use the default app engine
# stacktrace error page or browser error page
'error_templates': {
    403: 'errors/default_error.html',
    404: 'errors/default_error.html',
    500: 'errors/default_error.html',
},

# Enable Federated login (OpenID and OAuth)
# Google App Engine Settings must be set to Authentication Options: Federated Login
'enable_federated_login': True,

# jinja2 base layout template
'base_layout': 'base.html',

# send error emails to developers
'send_mail_developer': False,

# fellas' list
'developers': (
    ('Richard Haber', 'rchaber@gmail.com'),
),

# If true, it will write in datastore a log of every email sent
'log_email': True,

# If true, it will write in datastore a log of every visit
'log_visit': True,

# ----> ADD MORE CONFIGURATION OPTIONS HERE <----

'joblist': ['Publisher', 'Manager', 'Editor', 'Professional Reader', 'Designer', 'Translator', 'Proofreader'],

}  # end config
