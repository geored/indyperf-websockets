import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import time
import uuid
import json
import datetime


class WSHandler(tornado.websocket.WebSocketHandler):

    SESSIONS = []

    def open(self, *args, **kwargs):
        print('Connection is open')
        if self not in self.SESSIONS:
            self.SESSIONS.append(self)
            print('Client Session added: {}'.format(self))

    def on_close(self):
        print('Connection is closed')
        if self in self.SESSIONS:
            self.SESSIONS.remove(self)
            print('Client Session removed from sessions: {}'.format(self))

    def on_message(self, message):
        print('Message recived: {}'.format(message))

    @classmethod
    def broadcast(cls,data):
        for session in cls.SESSIONS:
            session.write_message(data)

    def check_origin(self, origin):
        return True

class MainHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write({'status':'ok'})

    def post(self, *args, **kwargs):
        headers = {
            x: self.request.headers[x] for x in self.request.headers
        }
        payload = self.request.body.decode('utf-8')
        data = {
            'id': str(uuid.uuid4()),
            'headers': headers,
            'timestamp': str(int(time.time() * 1000)),
            'payload': payload
        }
        WSHandler.broadcast(data)
        self.write(json.dumps({
            'method': 'POST',
            'time': str(datetime.datetime.now().time()),
            'status': 'ok'
        }))


if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(
        tornado.web.Application(
            [
                (r'/ws',WSHandler),
                (r'/', MainHandler)
            ],
            websocket_ping_interval=10
        )
    )
    http_server.listen(8182)
    tornado.ioloop.PeriodicCallback(WSHandler.heartbeat, 30000).start()
    tornado.ioloop.IOLoop.instance().start()