from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading

class LocalServer(BaseHTTPRequestHandler):

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        LocalServer.code = query_components.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        #处理code
        
        html = '<html><body><h1>登录完成，可以关闭此页面!</h1></body></html>'
        self.wfile.write(bytes(html, 'gbk'))
        threading.Thread(target=self.shutdown_server).start()

    def shutdown_server(self):
        self.server.shutdown()

    @classmethod
    def get_response_data(cls):
        return cls.code

def start_server():

    address = '127.0.0.1'
    port = 40935

    url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=1cbfda79-fc84-47f9-8110-f924da9841ec&response_type=code&redirect_uri=http://127.0.0.1:40935&response_mode=query&scope=XboxLive.signin offline_access"
    webbrowser.open(url)

    server = HTTPServer((address, port), LocalServer)
    server.serve_forever()
    return LocalServer.get_response_data()
    
