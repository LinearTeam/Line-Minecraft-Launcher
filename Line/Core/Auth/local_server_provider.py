import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class LLocalServer(BaseHTTPRequestHandler):

    def do_GET(self):
        queryComponents = parse_qs(urlparse(self.path).query)
        LLocalServer.code = queryComponents.get("code", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # 处理code

        html = "<html><body><h1>登录完成，可以关闭此页面!</h1></body></html>"
        self.wfile.write(bytes(html, "gbk"))
        threading.Thread(target=self.shutdownServer).start()

    def shutdownServer(self):
        self.server.shutdown()

    @classmethod
    def getResponseData(cls):
        return cls.code


def startServer():

    address = "127.0.0.1"
    port = 40935

    url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=1cbfda79-fc84-47f9-8110-f924da9841ec&response_type=code&redirect_uri=http://127.0.0.1:40935&response_mode=query&scope=XboxLive.signin offline_access"
    webbrowser.open(url)

    server = HTTPServer((address, port), LLocalServer)
    server.serve_forever()
    return LLocalServer.getResponseData()
