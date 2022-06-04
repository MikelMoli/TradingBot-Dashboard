#cat wsgi.py
import sys
sys.path.insert(0,"/var/www/TradingBot-Dashboard")
from app import app as application



import sys
# add your app directory to the sys.path
project_home = u'/var/www/TradingBot-Dashboard' #specify to the correct path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
# see https://plot.ly/dash/deployment
from app import app
application = app.server
#app.config.update({
#    # as the proxy server will remove the prefix
#    #'routes_pathname_prefix': '',
#    # the front-end will prefix this string to the requests
#    # that are made to the proxy server
#    'requests_pathname_prefix': '/dashboard/index.wsgi/'
#})
