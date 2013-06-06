My BMTC Miles
=============

*Built at Random Hacks of Kindness 2013, Bangalore.*

Earn miles by using public transport! Upload tickets from your journeys via the
Bangalore Metropolitan Transport Corporation (BMTC) and redeem your miles
for rewards.

Execute the following commands to pull in dependencies:

    cd bmtc-miles
    python virtualenv.py flask
    flask/bin/pip install flask
    flask/bin/pip install flask-login
    flask/bin/pip install flask-openid
    flask/bin/pip install flask-mail
    flask/bin/pip install flask-wtf
    flask/bin/pip install flask-babel
    flask/bin/pip install flup

## Develop

We recommend Python 2.7.x, [pip](http://www.pip-installer.org/en/latest/) and [virtualenv](https://pypi.python.org/pypi/virtualenv)
installed prior to hacking on this code.

   * Activate the virtualenv: `source bmtcmiles/bin/activate`
