import http.cookiejar
import http.client
from urllib import parse
from urllib import request
from urllib import error
import xml.etree.ElementTree as ET

class REST:

    file = open('config.xml', 'r')
    config = ''
    for i in file:
        config += i
    file.close()

    root = ET.fromstring(config)

    host = root.find('./URLSettings/URL').text
    user = root.find('./URLSettings/URLuser').text
    password = root.find('./URLSettings/URLpass').text

    cookie = ""
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "*/*"}

    def getcookie(self):
        REST.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "*/*"}
        conn = http.client.HTTPConnection(REST.host)
        conn.request("GET", "/rest/user", "", REST.headers)
        response = conn.getresponse()
        # print(response.status, response.reason)
        REST.cookie = response.getheader('set-cookie')
        REST.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "*/*", "Cookie": REST.cookie}
        conn.close()

    def authentify(self):
        params = parse.urlencode({'j_username': REST.user, 'j_password': REST.password})
        conn = http.client.HTTPConnection(REST.host)
        conn.request("POST", "/rest/j_security_check", params, REST.headers)
        response = conn.getresponse()
        # print(response.status, response.reason)
        conn.close()

    def getUser(self):
        conn = http.client.HTTPConnection(REST.host)
        conn.request("GET", "/rest/user", "", REST.headers)
        response = conn.getresponse()
        data = response.read()
        # print(data)
        conn.close()

    def list(value):
        conn = http.client.HTTPConnection(REST.host)
        conn.request("GET", "/rest/" + value, "", REST.headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        # print(data)
        return data

    def listalt(value, image):
        conn = http.client.HTTPConnection(REST.host)
        try:
            conn.request("GET", "/" + value, "", REST.headers)
            request.urlretrieve('http://' + REST.host + "/" + value, image + '.png')
        except error.HTTPError:
            pass
        # print(conn.request("GET", "/" + value, "", REST.headers))
        response = conn.getresponse()
        data = response.read()
        conn.close()
        # print(data)
        return data