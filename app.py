import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket


class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('New Connection')
		self.write_message('New  WebSocket User is connected')

	def on_message(self,message):
		print('Got Message from User: ' + message)
		self.write_message("Message from Server: " + message)

	def on_close(self):
		print('Closing connection...')

	def check_origin(self,origin):
		return True


class GitPushHandler(tornado.web.RequestHandler):

	# @web.asynchronous
	def get(self,*args):
		print("Got GET request from user side...")
		self.write("OK-GET")

	# @web.asynchronous
	def post(self,*args):
		print("Got POST request from user side...")	
		# Handler Github POST payload webhook push data provided from every change on github repository...
		self.write("OK-POST")

app = tornado.web.Application([ ( r"/ws" , WSHandler  ) , ( r"/ipgw" , GitPushHandler   )   ])


if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
