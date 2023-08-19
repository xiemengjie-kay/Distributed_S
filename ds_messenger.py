import socket
import json
from collections import namedtuple
import ds_protocol
import time


class FailToJoin(Exception):
    """
    FailToJoin is a custom exception that is raised when attempting to join the official
    ICS 32 Distributed Social Server.
    """
    pass


class RetrieveProtocol:
    """
    RetrieveProtocol class is responsible for formatting a JSON request that can be used to retrieve
    new messages or retireve all messages from the DS server.
    """
    def __init__(self, token:str, status:str):
        """
        Initializer for RetrieveProtocol.

        :param token: The user token you get after successivefully joining the DS server.  
        :param status: Specify requests, 'all' for retireve all messages, 'new' for retireve new messages.  
        
        """
        self.token = token
        self.status = status

    def new_message(self):
        """
        Formats a request in which unread new messages are requested from the DS server.
        """
        return '{"token":"' + self.token + '", "directmessage": "' + self.status + '"}'


    def all_message(self):
        """
        Format a request in which all messages are requested from the DS server.
        """
        return '{"token":"' + self.token + '", "directmessage": "' + self.status + '"}'


class DirectMessage:
    """
    The DirectMessage class stores message data in each response from a "retrieve_new" or "retrieve_all" request
    and makes DirectMessage objects.
    """
    def __init__(self):
        """
        Initializer for DirectMessage.

        """
        self.recipient = None
        self.message = None
        self.timestamp = None 


class DirectMessenger:
    """
    The DirectMessenger class is responsible for communicating with the DS server. This class can be implemented to
    send direct messages to other users and retrieve unread messages or all messages from the DS server.
    """
    def __init__(self, dsuserver=None, username=None, password=None):
        """
        Initializer for DirectMessenger.

        :param dsuserver: The IP address of the official ICS 32 Distributed Social Server.  
        :param username: Initialize with your username.  
        :param password: Initialize with your password.  
        
        """
        self.token = None
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        
		
    def send(self, message:str, recipient:str) -> bool:
        """ 
        Make connection with the DS server and send direct messages to other users.

        :param message: The message you want to send.  
        :param recipient: The user you want to send messages to.

        :return: bool
        """
        port = 3021
        # connect to the DS server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((self.dsuserver, port))
            except:
                print("fail to connect to the server, change a server.")
                return False

            # create send and receive files in the socket
            send = client.makefile('w')
            recv = client.makefile('r')
            # get a JSON string of joining message
            joined_msg = ds_protocol.join(self.dsuserver, self.username, self.password)
            
            # send the JSON string to join the server and get a response: r_join
            r_join = self.write_and_receive(joined_msg, send, recv, join_=True)

            if 'error' in r_join:
                # fail to join
                return False
            if 'ok' in r_join:
                t = self.extract_json(r_join)
                self.token = t.token

            post_msg = ds_protocol.post(self.token, message, recipient, str(time.time()))
            # send the formatted post to the recipient and receive a response
            response = self.write_and_receive(post_msg, send, recv)
            
            if response:
                # successfully send the information
                return True
            else:
                # fail to send the information
                print("There is something wrong. You cannot put \' in your post.")
                return False
            
        	
    def retrieve_new(self) -> list:
        """
        Retrieve unread messages from the DS server and convert the responses into a list of DirectMessage objects.

        :return: list
        """
        dm_new_list = []      
        port = 3021
        # connect to the DS server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((self.dsuserver, port))
            except:
                print("fail to connect to the server, change a server.")
                return False

            # create send and receive files in the socket
            send = client.makefile('w')
            recv = client.makefile('r')

            # get a JSON string of joining message
            joined_msg = ds_protocol.join(self.dsuserver, self.username, self.password)
            
            # send the JSON string to join the server and get a response: r_join
            r_join = self.write_and_receive(joined_msg, send, recv, join_=True)

            if 'error' in r_join:
                raise FailToJoin("Failed to join the server. The password is incorrect.")
            if 'ok' in r_join:
                t = self.extract_json(r_join)
                self.token = t.token

            # format a retireve-all-new-messages request
            retrieve_msg = RetrieveProtocol(self.token, 'new').new_message()
            try:
                send.write(retrieve_msg + '\n')
                send.flush()
            except:
                print("Fail to send the request to the server.")
            else:
                srv_msg = recv.readline()
                json_obj = json.loads(srv_msg)
                for i in json_obj['response']['messages']:
                    dm_new = DirectMessage()
                    dm_new.recipient = i["from"]
                    dm_new.message = i["message"]
                    dm_new.timestamp = i["timestamp"]
                    dm_new_list.append(dm_new.__dict__)

                # returns a list of DirectMessage objects containing all new messages
                return dm_new_list
                
            
    def retrieve_all(self) -> list:
        """
        Retrieve all messages from the DS server and convert the responses into a list of DirectMessage objects.

        :return: list
        """
        dm_all_list = []
        port = 3021
        # connect to the DS server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((self.dsuserver, port))
            except:
                print("fail to connect to the server, change a server.")
                return False

            # create send and receive files in the socket
            send = client.makefile('w')
            recv = client.makefile('r')

            # get a JSON string of joining message
            joined_msg = ds_protocol.join(self.dsuserver, self.username, self.password)
            
            # send the JSON string to join the server and get a response: r_join
            r_join = self.write_and_receive(joined_msg, send, recv, join_=True)

            if 'error' in r_join:
                raise FailToJoin("Failed to join the server. The password is incorrect.")
            if 'ok' in r_join:
                t = self.extract_json(r_join)
                self.token = t.token

            # format a retireve-all-messages request
            retrieve_msg = RetrieveProtocol(self.token, 'all').all_message()
            try:
                send.write(retrieve_msg + '\n')
                send.flush()
            except:
                print("Fail to send the request to the server.")
            else:
                srv_msg = recv.readline()
                json_obj = json.loads(srv_msg)
                for i in json_obj['response']['messages']:
                    dm_new = DirectMessage()
                    dm_new.recipient = i["from"]
                    dm_new.message = i["message"]
                    dm_new.timestamp = i["timestamp"]
                    dm_all_list.append(dm_new.__dict__)

                # returns a list of DirectMessage objects containing all messages
                return dm_all_list
            

    def extract_json(self, json_msg:str) -> "DataTuple":
        '''
        Call json.loads function on a json string and then convert the json object into a DataTuple object.

        :param json_msg: A JSON formatted string.

        :return: DataTuple
        '''
        # Create a namedtuple to hold the values we expect to retrieve from json messages.
        DataTuple = namedtuple('DataTuple', ['type','message','token'])
        try:
            json_obj = json.loads(json_msg)
            mtype = json_obj['response']['type']
            message = json_obj['response']['message']
            token = json_obj['response']['token']
        except json.JSONDecodeError:
             print("Json cannot be decoded.")

        return DataTuple(mtype, message, token)

    
    def write_and_receive(self, msg:str, send, recv, join_=False) -> bool:
        """
        Abstract functions that are used to join the server and write formatted messages into the socket file.

        :param msg: A JSON string that has requests to the DS server.  
        :param send: Send file created in the socket.  
        :param recv: Receive file created in the socket.  
        :param join_: True if you want to join the server.

        :return: bool
        """
        try:
            send.write(msg + '\n')
            send.flush()
        except:
            return False

        srv_msg = recv.readline()
        if join_:
            return srv_msg
        else:
            if 'ok' in srv_msg:
                return True
            if 'error' in srv_msg:
                return False
        
