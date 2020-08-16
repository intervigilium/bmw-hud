#!/usr/bin/env python3

import argparse
import socket


HUD = ("192.168.10.1", 50007)

DATA_BEGIN_OFFSET = 0x2
SPEED_LIMIT_OFFSET = 0x06
DIST_TO_TURN_OFFSET = 0x07
ARROW_OFFSET = 0x0b
LANE_COUNT_OFFSET = 0x0c
LANE_INDEX_OFFSET = 0x0d
ARRIVAL_TIME_HOURS_OFFSET = 0x0f
ARRIVAL_TIME_MINUTES_OFFSET = 0x10
ARRIVAL_TIME_AMPM_OFFSET = 0x11
REMAINING_DIST_0_OFFSET = 0x12
REMAINING_DIST_1_OFFSET = 0x13
DATA_END_OFFSET = 0x17
CHECKSUM_OFFSET = 0x18

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


def calculate_checksum(msg_data):
    if len(msg_data) != 21:
        raise Exception("calculate_checksum: Invalid data length {}"
                        .format(len(msg_data)))

    checksum = 0
    for i in msg_data:
        checksum += i
    checksum -= 0xff
    checksum &= 0xff

    return checksum


def verify_checksum(args):
    print("calculating message checksums")

    msg = MESSAGES[args.msg]

    bmw_checksum = calculate_checksum(msg[DATA_BEGIN_OFFSET:DATA_END_OFFSET])

    print("bmw checksum: {}".format(hex(bmw_checksum)))

    print("message[25]: {}".format(hex(msg[24])))


def generate_msg(args):
    print("generating message")

    msg = [
        0x7a, 0x02, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x01,
    ]

    if args.speed_limit is not None:
        msg[SPEED_LIMIT_OFFSET] = args.speed_limit

    if args.dist_to_turn is not None:
        msg[DIST_TO_TURN_OFFSET] = args.dist_to_turn

    if args.arrow is not None:
        msg[ARROW_OFFSET] = args.arrow

    if args.lane_count is not None:
        msg[LANE_COUNT_OFFSET] = args.lane_count

    if args.lane_index is not None:
        msg[LANE_INDEX_OFFSET] = args.lane_index

    if args.arrival_hours is not None:
        msg[ARRIVAL_TIME_HOURS_OFFSET] = args.arrival_hours

    if args.arrival_minutes is not None:
        msg[ARRIVAL_TIME_MINUTES_OFFSET] = args.arrival_minutes

    if args.arrival_ampm is not None:
        msg[ARRIVAL_TIME_AMPM_OFFSET] = args.arrival_ampm

    if args.remaining_dist_0 is not None:
        msg[REMAINING_DIST_0_OFFSET] = args.remaining_dist_0

    if args.remaining_dist_1 is not None:
        msg[REMAINING_DIST_1_OFFSET] = args.remaining_dist_1

    msg[CHECKSUM_OFFSET] = calculate_checksum(
            msg[DATA_BEGIN_OFFSET:DATA_END_OFFSET])

    raw_msg = bytearray(msg)

    print("generated message: {}".format(raw_msg))

    return msg


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
                        help="message index to replay")
    parser.add_argument("--checksum",
                        action="store_true",
                        help="calculate checksums of messages")

    parser.add_argument("--speed_limit",
                        type=int,
                        help="set speed limit")
    parser.add_argument("--dist_to_turn",
                        type=int,
                        help="distance until next turn")
    parser.add_argument("--arrow",
                        type=int,
                        help="direction arrow 5: left 8: left")
    parser.add_argument("--lane_count",
                        type=int,
                        help="number of lanes")
    parser.add_argument("--lane_index",
                        type=int,
                        help="lane indicator index")
    parser.add_argument("--arrival_hours",
                        type=int,
                        help="arrival time hours")
    parser.add_argument("--arrival_minutes",
                        type=int,
                        help="arrival time minutes")
    parser.add_argument("--arrival_ampm",
                        type=int,
                        help="arrival time AM (0) PM (1)")
    parser.add_argument("--remaining_dist_0",
                        type=int,
                        help="remaining distance 1/2")
    parser.add_argument("--remaining_dist_1",
                        type=int,
                        help="remaining distance 2/2")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.checksum:
        verify_checksum(args)
    else:
        send_msg(args)


if __name__ == "__main__":
    main()
