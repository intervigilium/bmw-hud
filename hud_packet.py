#!/usr/bin/env python3

import socket


def send_msg():
    hud = ("192.168.10.1", 50007)

    hello_msg = [
        0x7a, 0x01, 0x01, 0x15,
        0x13, 0x01
    ]

    server_ack_msg = [
        0x7c, 0x04, 0x01, 0x00,
        0x00
    ]

    msg = [
        0x7a, 0x02, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0xff, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x01
    ]
    raw_msg = bytearray(msg)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("connecting to HUD")
    s.connect(hud)

    print("sending message")
    s.sendall(raw_msg)

    print("receiving response")
    data = s.recv(1024)

    print("received {}".format(data))


def main():
    send_msg()


if __name__ == "__main__":
    main()
