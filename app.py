import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import logging
import time
import uuid


class WSHandler(tornado.websocket.WebSocketHandler):

	sessions = set()

	def open(self):
		print('Connection open')
		if self not in self.sessions:
			self.sessions.add(self)
		self.write_message('Connection Established')

	def on_message(self,message):
		print('Message from User: ' + message)
		self.write_message("Message from Server: " + message)

	def on_close(self):
		print('Closing Connection to client')
		if self in self.sessions:
			self.sessions.remove(self)

	def check_origin(self,origin):
		return True

	@classmethod
	def sendWebHookPayload(cls,data):
		for session in cls.sessions:
			session.write_message(data)

	@classmethod
	def heartbeat(cls):
		return "OK"

class GitPushHandler(tornado.web.RequestHandler):

	# @web.asynchronous
	def get(self,*args):
		print("Got GET request from user side...")
		self.write("OK")

	# @web.asynchronous
	def post(self,*args):
		print(self.request.body)
		headers ={ x:self.request.headers[x] for x in self.request.headers }
		data = {
			'id': str(uuid.uuid4()) ,
			'headers': headers,
			'timestamp': str(int(time.time()*1000)),
			'payload': self.request.body.decode('utf-8')
		}
		WSHandler.sendWebHookPayload(data)
		self.write("OK")

app = tornado.web.Application([ ( r"/ws" , WSHandler  ) , ( r"/ipgw" , GitPushHandler   )   ])


if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(8888)
	tornado.ioloop.PeriodicCallback(WSHandler.heartbeat,30000).start()
	tornado.ioloop.IOLoop.instance().start()
