import serial
from time import sleep
import binascii

commands = {
    "header": "MJ",
    "status": "CS",
    "params": "PR",
    "timer": "TR",
    "params_list": {
        "01": ('model', None, None),
        "03": ('rotation_speed', 10, "rpm"),
        "04": ('motor_current', 0.1, "A"),
        "05": ('pump_temp', 1, "°C"),
        "08": ('present_rotation', 1, "%"),
        "11": ("rated_speed", 10, "rpm"),
        "21": ("axis1_unbal_MB", 1, "%"),
        "22": ("axis2_unbal_MB", 1, "%"),
        "26": ("X1_MB", 1, "%"),
        "27": ("Y1_MB", 1, "%"),
        "28": ("X2_MB", 1, "%"),
        "29": ("Y2_MB", 1, "%"),
        "30": ("Z_MB", 1, "%")
    },
    "timer_list": {"01": (None, None)},
    "status_answer": {
        "NS": "stop",
        "NA": "acceleration",
        "NN": "normal",
        "NB": "deceleration",
        "FS": "failed_stop",
        "FF": "failed_free_run",
        "FR": "failed_regen_brake",
        "FB": "failed_deceleration"
    }
}


def add_checksum(command_str: str) -> bytes:
    """Adds a checksum to the end of a string by summing the ASCII codes of its characters.

    Args:
        command_str: A string to add a checksum to.

    Returns:
        bytearray with a checksum appended to it, in uppercase hexadecimal format.
    """
    # Convert each character of the string to its ASCII code, then to its hexadecimal representation.
    hex_codes = [hex(ord(char))[2:].zfill(2) for char in command_str]
    # Sum the hexadecimal codes as integers.
    checksum = hex(sum(int(h,
                           16) for h in hex_codes) & 0xff)[2:].zfill(2).upper()
    checksum_byte = bytes(checksum, 'utf-8')
    checksum_hex = str(binascii.hexlify(checksum_byte), 'ascii')
    # Append the checksum and CR to the original string.
    CR = '0d'
    hex_codes.append(checksum_hex + CR)
    hex_code_str = ''.join(hex_codes)
    bytearray_obj = bytearray.fromhex(hex_code_str)
    return bytes(bytearray_obj)


def ser_obj():
    return serial.Serial('COM6',
                         baudrate=9600,
                         bytesize=8,
                         parity=serial.PARITY_NONE,
                         stopbits=1,
                         timeout=0.3)


def check_status(station: int) -> str:
    '''Check the status of the TMP

    [description]

    Args:
        station (int): [description]
    '''
    # send this "MJ01PR03"
    header = commands["header"]
    function = commands["status"]
    status_str = f"{header}{str(station).zfill(2)}{function}"
    ser = ser_obj()
    status_command = add_checksum(status_str)
    ser.write(status_command)
    sleep(0.3)
    output = ser.readline()
    decoded = output.decode('utf-8')
    reply = commands['status_answer'][decoded[4:-5]]
    # print(reply)
    ser.close()
    return reply


def get_params(station: int):
    header = commands["header"]
    function = commands["params"]
    params_list = commands["params_list"].items()
    result = []
    ser = ser_obj()
    listy = [val[0] for val in commands["params_list"].values()]
    # print(list(commands["params_list"].keys()))
    for params_no, values in params_list:
        # print(values)
        params_str = f"{header}{str(station).zfill(2)}{function}{params_no}"
        params_command = add_checksum(params_str)
        ser.write(params_command)
        sleep(0.3)
        output = ser.readline()
        decoded = output.decode('utf-8')
        reply = decoded[8:-3]
        if values[1]:
            decoded = values[1] * int(reply)
            result.append(decoded)
        else:
            result.append(reply)
        # print(reply)
    return result, listy


if __name__ == '__main__':

    # final_str = "MJ01PR03"
    # result = add_checksum(final_str)
    # print(result)
    # add_checksum(final_str)
    status = check_status(1)
    print("P27")
    print("Status: ", status)
    if status == "normal":
        params, desc = get_params(1)
        for i, j in zip(params, desc):
            print(f"{j}: {i}")

