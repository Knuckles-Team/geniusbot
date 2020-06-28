#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from client_server import Server

server = Server()
server.handle_client()
server.close()