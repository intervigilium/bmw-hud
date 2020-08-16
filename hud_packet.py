#!/usr/bin/env python3

import argparse
import socket


HUD = ("192.168.10.1", 50007)

HELLO_MSG = [
    0x7a, 0x01, 0x01, 0x15,
    0x13, 0x01,
]

SERVER_ACK_MSG = [
    0x7c, 0x04, 0x01, 0x00,
    0x00,
]

EMPTY_MSG = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0xff, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x01,
    0x00, 0x01,
]

REPLAY_MSG1 = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x23, 0x80,
    0x00, 0x00, 0x00, 0x05,
    0x03, 0x01, 0x00, 0x09,
    0x24, 0x01, 0xa5, 0x35,
    0x00, 0x00, 0x00, 0x01,
    0xb5, 0x01,
]

REPLAY_MSG2 = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x23, 0x73,
    0x00, 0x00, 0x00, 0x05,
    0x03, 0x01, 0x00, 0x09,
    0x24, 0x01, 0x98, 0x35,
    0x00, 0x00, 0x00, 0x01,
    0x9b, 0x01,
]

REPLAY_MSG3 = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x23, 0x00,
    0x00, 0x00, 0x00, 0x08,
    0x01, 0x01, 0x00, 0x09,
    0x22, 0x01, 0xc3, 0x31,
    0x00, 0x00, 0x00, 0x01,
    0x4e, 0x01,
]

REPLAY_MSG4 = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x19, 0xab,
    0x01, 0x00, 0x00, 0x05,
    0x00, 0x00, 0x00, 0x09,
    0x24, 0x01, 0xe3, 0x32,
    0x00, 0x00, 0x00, 0x01,
    0x0e, 0x02,
]

REPLAY_MSG5 = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x00, 0xf3,
    0x00, 0x00, 0x00, 0x08,
    0x00, 0x00, 0x00, 0x09,
    0x25, 0x01, 0x67, 0x32,
    0x00, 0x00, 0x00, 0x01,
    0xc4, 0x01,
]

TEST_MSG = [
    0x7a, 0x02, 0x00, 0x00,
    0x00, 0x00, 0x23, 0x80,
    0x00, 0x00, 0x00, 0x05,
    0x03, 0x01, 0x00, 0x09,
    0x24, 0x01, 0xa5, 0x35,
    0x00, 0x00, 0x00, 0x01,
    0xb5, 0x01,
]

MESSAGES = [
    EMPTY_MSG,
    REPLAY_MSG1,
    REPLAY_MSG2,
    REPLAY_MSG3,
    REPLAY_MSG4,
    REPLAY_MSG5,
    TEST_MSG,
]


def calculate_checksum(args):
    print("calculating message checksums")

    msg = MESSAGES[args.msg]

    bmw_checksum = 0
    for i in range(2, 23):
        bmw_checksum += msg[i]
    bmw_checksum -= 0xff
    bmw_checksum &= 0xff

    print("bmw checksum: {}".format(hex(bmw_checksum)))

    print("message[25]: {}".format(hex(msg[24])))


def send_msg(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("connecting to HUD")
    s.connect(HUD)

    msg = bytearray(MESSAGES[args.msg])
    print("sending message: {}".format(msg))
    s.sendall(msg)

    print("receiving response")
    data = s.recv(1024)

    print("received {}".format(data))
    # TODO: Check against server ACK message


def parse_args():
    parser = argparse.ArgumentParser(description='Send packets to BMW HUD.')
    parser.add_argument("--msg",
                        type=int,
                        required=True,
                        help="message index to replay")
    parser.add_argument("--checksum",
                        action="store_true",
                        help="calculate checksums of messages")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.checksum:
        calculate_checksum(args)
    else:
        send_msg(args)


if __name__ == "__main__":
    main()
