import json
import socket
import time
import cProfile
import timeit

# List of ESP32 IP addresses
ESP32_IPS = [
    "192.168.4.1", # AP
    "192.168.4.2", # Head
    "192.168.4.3", # Body
    "192.168.4.4"  # Tail
]

# PC IP address
PC_IP = "192.168.4.10"

ID_IP_table = {
    1: '192.168.4.2',
    2: '192.168.4.2',
    3: '192.168.4.2',
    4: '192.168.4.3',
    5: '192.168.4.3',
    6: '192.168.4.3',
    7: '192.168.4.4',
    8: '192.168.4.4',
    9: '192.168.4.4'
}

IP_IDList_table = {
    '192.168.4.2': [1, 2, 3],
    '192.168.4.3': [4, 5, 6],
    '192.168.4.4': [7, 8, 9]
}


UDP_PORT = 12345

def send_udp_message(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))
    sock.close()

def query_ip_by_id(ID):
    return ID_IP_table.get(ID, "ID not found")

def query_id_list_by_ip(IP):
    return IP_IDList_table.get(IP, "IP not found")

def set_rgb_color(ID, r, g, b):
    ip = query_ip_by_id(ID)
    message = {
        'Cmd': "RGB",
        'ID': ID,
        'R': r,
        'G': g,
        'B': b
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def position_up(ID):
    ip = query_ip_by_id(ID)
    message = {
        'Cmd': "Position+",
        'ID': ID
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def position_down(ID):
    ip = query_ip_by_id(ID)
    message = {
        'Cmd': "Position-",
        'ID': ID
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def write_pos_ex(ID, pos, vel, acc):
    ip = query_ip_by_id(ID)
    message = {
        'Cmd': "WritePosEx",
        'ID': ID,
        'pos': pos,
        'vel': vel,
        'acc': acc
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def reg_write_pos_ex(ID, pos, vel, acc):
    ip = query_ip_by_id(ID)
    message = {
        'Cmd': "RegWritePosEx",
        'ID': ID,
        'pos': pos,
        'vel': vel,
        'acc': acc
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def sync_write_pos_ex(ip, pos_list, vel_list, acc_list):
    message = {
        'Cmd': "SyncWritePosEx",
        'ID_list': query_id_list_by_ip(ip),
        'IDNum': len(query_id_list_by_ip(ip)),
        'pos_list': pos_list,
        'vel_list': vel_list,
        'acc_list': acc_list
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def get_state(ID):
    message = {
        'Cmd': "State",
        'ID': ID
    }
    ip = query_ip_by_id(ID)
    json_message = json.dumps(message)
    # send_udp_message(ip, UDP_PORT, json_message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("192.168.4.10", 12345))
    sock.sendto(json_message.encode(), (ip, UDP_PORT))

    # print("Cmd sent")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            ip_address, port = addr 
            # print(f"Received message: {data.decode()} from IP: {ip_address}, Port: {port}")
            return int(data.decode())
        except KeyboardInterrupt:
            print("Exiting...")
            break
    sock.close()

def enable_torque(ip, Enable):
    message = {
        'Cmd': "EnableTorque",
        'ID_list': query_id_list_by_ip(ip),
        'Enable': Enable
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def set_torque(ip, newTorque_list):

    message = {
        'Cmd': "SetTorque",
        'ID_list': query_id_list_by_ip(ip),
        'NewTorque_list': newTorque_list
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def set_mode(ip, Mode):
    message = {
        'Cmd': "SetMode",
        'ID_list': query_id_list_by_ip(ip),
        'Mode': Mode
    }
    json_message = json.dumps(message)
    send_udp_message(ip, UDP_PORT, json_message)

def set_time(ip, time_list, direction_list):
    message = {
        'Cmd': "SetTime",
        'ID_list': query_id_list_by_ip(ip),
        'Time_list': time_list,
        'Direction_list': direction_list
    }
    json_message = json.dumps(message)
    # send_udp_message(ip, UDP_PORT, json_message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("192.168.4.10", 12345))
    sock.sendto(json_message.encode(), (ip, UDP_PORT))

    # print("Cmd sent")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            decoded_data = data.decode('utf-8')
            print(f"Received data: {decoded_data}")
            json_data = json.loads(decoded_data)
            pos_list = json_data["Pos_list"]
            speed_list = json_data["Speed_list"]
            current_list = json_data["Current_list"]

            return pos_list, speed_list, current_list
        except KeyboardInterrupt:
            print("Exiting...")
            break
    sock.close()



# def execute_function():
#     for _ in range(100):
#         get_state(1)
#
# total_time = timeit.timeit(execute_function, number=1)
# average_time = total_time / 100
#
# print(f"获取舵机位置函数执行100次的平均执行时间: {average_time:.8f} 秒")



# Example usage
# write_pos_ex(1, 0, 4000, 100)
# sync_write_pos_ex("192.168.4.2", [1000, 1000, 1000], [4000, 4000, 4000], [100, 100, 100])
# control_all_boards(0, 255, 0)  # Set RGB LED to green on all boards
# position_up(1)
# position_down("192.168.4.2", 2)
# set_rgb_color("192.168.4.2",0, 255, 0)
# print(get_state(1))
# enable_torque("192.168.4.5", 1)
# set_torque("192.168.4.5",[100,100,100])
# set_mode("192.168.4.5", 0)
# pos_list, speed_list, current_list = set_time("192.168.4.5", [200, 200, 200], [0, 0, 0])
# print("Pos_list: ", pos_list)
# print("Speed_list: ", speed_list)
# print("Current_list: ", current_list)
# cProfile.run("get_state(1)")


def tail_lock():
    sync_write_pos_ex("192.168.4.4", [1380, 1380, 1380], [1000, 1000, 1000], [50, 50, 50])

def head_lock():
    sync_write_pos_ex("192.168.4.2", [1380, 1380, 1380], [1000, 1000, 1000], [50, 50, 50])

def body_expend():
    sync_write_pos_ex("192.168.4.2", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.3", [1000, 1000, 1000], [1000, 1000, 1000], [50, 50, 50])

def body_contract():
    sync_write_pos_ex("192.168.4.4", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.3", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])

def free():
    sync_write_pos_ex("192.168.4.2", [1000, 1000, 1000], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.3", [1000, 1000, 1000], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.4", [1000, 1000, 1000], [1000, 1000, 1000], [50, 50, 50])


def move_forward():
    tail_lock()
    time.sleep(0.2)
    body_expend()
    time.sleep(0.2)
    head_lock()
    time.sleep(0.2)
    body_contract()
    time.sleep(0.2)





if __name__ == "__main__":
    # free()
    sync_write_pos_ex("192.168.4.2", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.3", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])
    sync_write_pos_ex("192.168.4.4", [1300, 1300, 1300], [1000, 1000, 1000], [50, 50, 50])

    for i in range(50):
        time.sleep(0.2)
        move_forward()

























