import socket
import select
from thread import *
import sys
import MySQLdb as mdb
import time
from desalgo import des
from flask import Flask, render_template, Response
from camera import VideoCamera

sql_host = "localhost"
sql_username = "varun"
sql_password = "python"
sql_database = "NetMon"
key = "vv_narad"
d = des()

sql_connection = mdb.connect(sql_host,sql_username,sql_password,sql_database)
print sql_connection
cursor = sql_connection.cursor()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.bind((IP_address, Port)) 
server.listen(100)
list_of_clients=[]

def clientthread(conn, addr):
	conn.send(d.encrypt(key,"1 for Chatroom\n2 for Downloading Media\n3 for live streaming",padding = True))
	choice = conn.recv(2048)
	choice = d.decrypt(key,choice,padding = True)
	choice = choice.strip()
	choice = int(choice)

	if(choice == 1):
		conn.send(d.encrypt(key,"Welcome to the chat room!",padding = True))
		while True:
			try:
				message = conn.recv(2048)
				msg = d.decrypt(key,message,padding = True)
				if msg:
					print "<" + addr[0] + "> " + msg
					print message
					message_to_send = "<" + addr[0] + "> " + msg
					broadcast(message_to_send,conn)
				else:
					remove(conn)
			except:
				continue
	elif(choice == 2):
		file_name = open('img.jpeg','rb')
   		while True:
   			data = file_name.readline()
   			if not data:
   				break
   			conn.send(data)
   		file_name.close()
		conn.close()
	elif(choice == 3):
		conn.send(d.encrypt(key,"http://"+IP_address+":5000/",padding = True))
		app = Flask(__name__)
		@app.route('/')
		def index():
			return render_template('index.html')
		def gen(camera):
			while True:
				frame = camera.get_frame()
				yield (b'--frame\r\n'
					   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		@app.route('/video_feed')
		def video_feed():
			return Response(gen(VideoCamera()),
            	        mimetype='multipart/x-mixed-replace; boundary=frame')
		if __name__ == '__main__':
			app.run(host='0.0.0.0', debug=False)
			



def broadcast(message,connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(d.decrypt(key,message,padding = True))
            except:
                clients.close()
                remove(clients)
                
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print addr[0] + " connected"
    cursor = sql_connection.cursor()
    cursor.execute("use NetMon")
    conn.send(d.encrypt(key,"Username:",padding = True))
    user = conn.recv(2048)
    user = d.decrypt(key,user,padding = True)
    print user
    user = user.strip()
    conn.send(d.encrypt(key,"Password:",padding = True))
    password = conn.recv(2048)
    password = d.decrypt(key,password,padding = True)
    print password
    password = password.strip()
    cursor.execute("select * from login where name = '" + user +"' and password ='" + password + "'")
    data = cursor.fetchone()
    sql_connection.commit()
    print data[2]
    start_new_thread(clientthread,(conn,addr))
    
sql_connection.close()
conn.close()
server.close()