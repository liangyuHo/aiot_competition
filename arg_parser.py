import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--IP', type=str, help='input ip ')
    parser.add_argument('--COM', type=str, help='input usb com')
    args = parser.parse_args()
    return args
