import http.cookiejar
import http.client
from urllib import parse
import xml.dom.minidom


class REST:
    cookie = ""
    host = "app5.internal.bis2.net"
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
        params = parse.urlencode({'j_username': 'irina', 'j_password': 'developer'})
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
