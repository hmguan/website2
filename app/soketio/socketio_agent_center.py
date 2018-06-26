

def post_msg_to_room(data,room_identify):
    from app.soketio.sockio_api import send_messge_to_room
    send_messge_to_room(data,room_identify)