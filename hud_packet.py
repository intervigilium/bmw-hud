#!/usr/bin/env python3

import argparse
import contextlib
import math
import socket


HUD = ("192.168.10.1", 50007)

YARDS_PER_MILE = 1760

DATA_BEGIN_OFFSET = 0x2
UNK_OFFSET_2 = 0x02
SPEED_LIMIT_METRIC_OFFSET = 0x03
SPEED_CAMERA_OFFSET = 0x04
UNK_OFFSET_5 = 0x05
SPEED_LIMIT_OFFSET = 0x06
DIST_TO_TURN_0_OFFSET = 0x07
DIST_TO_TURN_1_OFFSET = 0x08
DIST_TO_TURN_2_OFFSET = 0x09
DIST_TO_TURN_DISABLE_OFFSET = 0x0a
ARROW_OFFSET = 0x0b
LANE_COUNT_OFFSET = 0x0c
LANE_INDEX_OFFSET = 0x0d
LANE_INDEX_DISABLE_OFFSET = 0x0e
ARRIVAL_TIME_HOURS_OFFSET = 0x0f
ARRIVAL_TIME_MINUTES_OFFSET = 0x10
ARRIVAL_TIME_AMPM_OFFSET = 0x11
REMAINING_DIST_0_OFFSET = 0x12
REMAINING_DIST_1_OFFSET = 0x13
REMAINING_DIST_2_OFFSET = 0x14
REMAINING_DIST_DISABLE_OFFSET = 0x15
TRAFFIC_DELAY_OFFSET = 0x16
NAV_MSG_DATA_END_OFFSET = 0x17
CHECKSUM_OFFSET = 0x18
CHECKSUM_OVERFLOW_OFFSET = 0x19

CONTROL_MSG_DATA_END_OFFSET = 0x08

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

CHECKSUM_OVERFLOW_TEST_MSG = [
    0x7a, 0x2, 0x0, 0x0,
    0x0, 0x0, 0x41, 0x0,
    0x0, 0xe1, 0x0, 0x5,
    0x6, 0x7, 0x0, 0x0,
    0x1, 0x2, 0x64, 0x64,
    0x0, 0x0, 0x0, 0x1,
    0x0, 0x2
]

CHECKSUM_UNDERFLOW_TEST_MSG = [
    0x7a, 0x2, 0x0, 0x0,
    0x0, 0x0, 0x41, 0x0,
    0x1, 0x0, 0x0, 0x5,
    0x6, 0x7, 0x0, 0x0,
    0x1, 0x2, 0x64, 0xa,
    0x0, 0x0, 0x0, 0x1,
    0xc6, 0x0
]

PARAMETER_CONTROL_MSG1 = [
    0x7b, 0x03, 0x0d, 0x64,
    0x00, 0x02, 0x01, 0x01,
    0x01, 0x76, 0x00
]

MESSAGES = [
    EMPTY_MSG,
    REPLAY_MSG1,
    REPLAY_MSG2,
    REPLAY_MSG3,
    REPLAY_MSG4,
    REPLAY_MSG5,
    TEST_MSG,
    CHECKSUM_OVERFLOW_TEST_MSG,
    CHECKSUM_UNDERFLOW_TEST_MSG,
    PARAMETER_CONTROL_MSG1,
]


def msg_to_string(msg):
    return ", ".join([hex(i) for i in msg])


def calculate_checksum(msg_data):
    if len(msg_data) != 21 and len(msg_data) != 6:
        raise Exception("calculate_checksum: Invalid data length {}"
                        .format(len(msg_data)))

    overflow = 0x01
    checksum = 0
    for i in msg_data:
        checksum += i
    checksum -= 0xff

    if checksum > 0xff:
        overflow = 0x02
    elif checksum < 0:
        overflow = 0x00

    checksum &= 0xff

    return (checksum, overflow)


def verify_checksum(args):
    print("calculating message checksums")

    msg = MESSAGES[args.msg]

    is_control_msg = len(msg) == 11

    end_offset = (CONTROL_MSG_DATA_END_OFFSET
                  if is_control_msg else NAV_MSG_DATA_END_OFFSET)

    (checksum, overflow) = calculate_checksum(
            msg[DATA_BEGIN_OFFSET:end_offset])

    print("checksum: {}, {}".format(hex(checksum), hex(overflow)))

    print("message[-2]: {}, message[-1]: {}".format(
        hex(msg[-2]), hex(msg[-1])))


def convert_yards(yards):
    if yards < 15:
        return 10
    elif yards < 25:
        return 20
    elif yards < 35:
        return 30
    elif yards < 45:
        return 40
    elif yards < 55:
        return 50
    elif yards < 65:
        # 55 makes it display 60 for some reason
        return 55
    elif yards < 75:
        # 60 makes it display 70 for some reason
        return 60
    elif yards < 85:
        # 70 makes it display 80 for some reason
        return 70
    elif yards < 95:
        # 80 makes it display 90 for some reason
        return 80
    elif yards < 150:
        return 100
    elif yards < 200:
        return 150
    elif yards < 250:
        return 200
    elif yards < 300:
        return 230
    else:
        return 255


def calculate_distance(miles):
    offset_2 = 0
    offset_1 = 0
    offset_0 = 0

    if miles > 41.0:
        scaling = (5660.0 - 41.0) / (139 - 1)
        offset_2 = math.floor(miles / scaling)
        remainder = (miles / scaling) - math.floor(miles / scaling)
        miles = remainder * scaling

    if miles > 0.17:
        scaling = (41.0 - (300.0 / YARDS_PER_MILE)) / (255 - 1)
        offset_1 = math.floor(miles / scaling)
        remainder = (miles / scaling) - math.floor(miles / scaling)
        miles = remainder * scaling

    if miles > 0.0:
        yards = miles * YARDS_PER_MILE
        offset_0 = convert_yards(yards)

    return (offset_2, offset_1, offset_0)


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

    if args.offset_2 is not None:
        msg[UNK_OFFSET_2] = args.offset_2

    if args.speed_limit_metric is not None:
        msg[SPEED_LIMIT_METRIC_OFFSET] = args.speed_limit_metric

    if args.speed_camera is not None:
        msg[SPEED_CAMERA_OFFSET] = args.speed_camera

    if args.offset_5 is not None:
        msg[UNK_OFFSET_5] = args.offset_5

    if args.speed_limit is not None:
        msg[SPEED_LIMIT_OFFSET] = args.speed_limit

    if args.dist_to_turn_0 is not None:
        msg[DIST_TO_TURN_0_OFFSET] = args.dist_to_turn_0

    if args.dist_to_turn_1 is not None:
        msg[DIST_TO_TURN_1_OFFSET] = args.dist_to_turn_1

    if args.dist_to_turn_2 is not None:
        msg[DIST_TO_TURN_2_OFFSET] = args.dist_to_turn_2

    if args.dist_to_turn_disable is not None:
        msg[DIST_TO_TURN_DISABLE_OFFSET] = args.dist_to_turn_disable

    if args.distance_to_turn is not None:
        (offset_2, offset_1, offset_0) = calculate_distance(
                args.distance_to_turn)
        msg[DIST_TO_TURN_2_OFFSET] = offset_2
        msg[DIST_TO_TURN_1_OFFSET] = offset_1
        msg[DIST_TO_TURN_0_OFFSET] = offset_0

    if args.arrow is not None:
        msg[ARROW_OFFSET] = args.arrow

    if args.lane_count is not None:
        msg[LANE_COUNT_OFFSET] = args.lane_count

    if args.lane_index is not None:
        msg[LANE_INDEX_OFFSET] = args.lane_index

    if args.lane_index_disable is not None:
        msg[LANE_INDEX_DISABLE_OFFSET] = args.lane_index_disable

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

    if args.remaining_dist_2 is not None:
        msg[REMAINING_DIST_2_OFFSET] = args.remaining_dist_2

    if args.remaining_dist_disable is not None:
        msg[REMAINING_DIST_DISABLE_OFFSET] = args.remaining_dist_disable

    if args.remaining_distance is not None:
        (offset_2, offset_1, offset_0) = calculate_distance(
                args.remaining_distance)
        msg[REMAINING_DIST_2_OFFSET] = offset_2
        msg[REMAINING_DIST_1_OFFSET] = offset_1
        msg[REMAINING_DIST_0_OFFSET] = offset_0

    if args.traffic_delay is not None:
        msg[TRAFFIC_DELAY_OFFSET] = args.traffic_delay

    (checksum, overflow) = calculate_checksum(
            msg[DATA_BEGIN_OFFSET:NAV_MSG_DATA_END_OFFSET])
    msg[CHECKSUM_OFFSET] = checksum
    msg[CHECKSUM_OVERFLOW_OFFSET] = overflow

    print("generated message: {}".format(msg_to_string(msg)))

    return msg


def send_msg(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("connecting to HUD")
        s.connect(HUD)

        raw_msg = bytearray(msg)
        print("sending message: {}".format(msg_to_string(msg)))
        s.sendall(raw_msg)

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

    parser.add_argument("--offset_2",
                        type=int,
                        help="unknown offset 2")

    parser.add_argument("--speed_limit_metric",
                        type=int,
                        help="speed limit is metric, 0 for mph, 1 for kmh")
    parser.add_argument("--speed_camera",
                        type=int,
                        help="enable speed camera icon")
    parser.add_argument("--offset_5",
                        type=int,
                        help="unknown offset 5")
    parser.add_argument("--speed_limit",
                        type=int,
                        help="set speed limit")

    parser.add_argument("--dist_to_turn_0",
                        type=int,
                        help="distance until next turn (1/3)")
    parser.add_argument("--dist_to_turn_1",
                        type=int,
                        help="distance until next turn (2/3)")
    parser.add_argument("--dist_to_turn_2",
                        type=int,
                        help="distance until next turn (3/3)")
    parser.add_argument("--dist_to_turn_disable",
                        type=int,
                        help="disable distance to turn indicator")
    parser.add_argument("--distance_to_turn",
                        type=float,
                        help="distance to turn in miles")

    parser.add_argument("--arrow",
                        type=int,
                        help="direction arrow 5: left 8: left")

    parser.add_argument("--lane_count",
                        type=int,
                        help="number of lanes")
    parser.add_argument("--lane_index",
                        type=int,
                        help="lane indicator index")
    parser.add_argument("--lane_index_disable",
                        type=int,
                        help="disable lane index indicator")

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
                        help="remaining distance 1/3")
    parser.add_argument("--remaining_dist_1",
                        type=int,
                        help="remaining distance 2/3")
    parser.add_argument("--remaining_dist_2",
                        type=int,
                        help="remaining distance 3/3")
    parser.add_argument("--remaining_dist_disable",
                        type=int,
                        help="disable remaining distance indicator")
    parser.add_argument("--remaining_distance",
                        type=float,
                        help="remaining distance in miles")

    parser.add_argument("--traffic_delay",
                        type=int,
                        help="minutes delay due to traffic")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.checksum:
        verify_checksum(args)
    elif args.msg is not None:
        send_msg(MESSAGES[args.msg])
    else:
        msg = generate_msg(args)
        send_msg(msg)


if __name__ == "__main__":
    main()
