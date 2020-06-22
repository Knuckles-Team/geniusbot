from client_server import Client
DISCONNECT_MESSAGE = "!DISCONNECT"

client = Client()
client.send("Hello World!")
client.send("Hello Everyone!")
client.send(DISCONNECT_MESSAGE)