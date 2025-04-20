# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<your secret key>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['roy.hopto.org', 'localhost', '127.0.0.1']


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'finesauces',
#        'USER': 'finesaucesadmin',
#        'PASSWORD': 'faraday7',
#        'HOST': 'localhost'
#    }
#}

STRIPE_PUBLISHABLE_KEY='pk_test_51Pg9ipRtrR1NtHHvQhFwwDEwdx6wgKKudQNrVHkmQPOZ9gbVU4yXQEsiOQtPrpyF8oq6kWvFLPjgM1o7Sz9j15Zr00wv4FO0LX'
STRIPE_SECRET_KEY='sk_test_51Pg9ipRtrR1NtHHvDwWCAVT8GvO11RQxCgnSFDzjzAqSBmNn4wBIcPTgMfXpgBsQ1xiZQW5HvgRciBjLaDlp9DUY00lQILfgGe'
STRIPE_API_VERSION = '2024-04-10'

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER ='khaemba.nganga1111@gmail.com'
#EMAIL_HOST_PASSWORD ='faraday7'
#EMAIL_PORT = 587
#EMAIL_USE_SSL = True
#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
