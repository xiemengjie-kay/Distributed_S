import time


"""
join will format user information and return a JSON string.
the JSON string will be used to join the server.

"""
def join(server:str, username:str, password:str) -> str:

    join_msg = '{"join": {"username": "' + username + '","password": "' + password + '","token":""}}'
        
    return join_msg


"""
post will format a journal post for the current user and return a JSON string.

"""
def post(token:str, entry:str, reci:str, time:str) -> str:

    post_msg = '{"token":"' + token + '", "directmessage": {"entry": "' + entry + '","recipient":"' + reci + '", "timestamp": "' + time + '"}}'

    return post_msg

"""
bio will format a bio and return a JSON string.

"""
def bio(token:str, bio:str) ->str:

    # create a timestamp for a bio
    bio_time = str(time.time())
    
    bio_msg = '{"token":"' + token + '", "bio": {"entry": "' + bio + '","timestamp": "' + bio_time + '"}}'

    return bio_msg

    
    

