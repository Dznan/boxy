import sys
import argparse

from relay import udp
from relay import tcp
from relay import status


def quit():
    print("Quitting...")

    if protocol == "UDP":
        udp.stop()
    else:
        tcp.stop()

    sys.exit(0)


def check_port_range(port):
    port = int(port)
    if not (0 < port <= 65535):
        raise argparse.ArgumentTypeError('{} is an invalid port!'.format(port))
    return port


# process args
parser = argparse.ArgumentParser(description='boxy tcp/udp relay')
parser.add_argument('--relay_port', '-i', type=check_port_range, required=True, help='local listen port')
parser.add_argument('--remote_port', '-p', type=check_port_range, required=True, help='remote listen port')
parser.add_argument('--remote_address', '-a', type=str, required=True, help='remote ip address')
parser.add_argument('--TCP', '-t', action='store_true', default=False, help='enable TCP relay')
args = parser.parse_args()

relay_port = args.relay_port
remote_port = args.remote_port
remote_address = args.remote_address
protocol = 'TCP' if args.TCP else 'UDP'

print("Relay starting on port {0}, relaying {1} to {2}:{3}".format(relay_port, protocol, remote_address, remote_port))

if protocol == "UDP":
    udp.start(relay_port, remote_address, remote_port)
else:
    tcp.start(relay_port, remote_address, remote_port)
status.start(relay_port, remote_address, remote_port)

try:
    while input() != "quit":
        continue
    quit()
except KeyboardInterrupt:
    quit()
except EOFError:
    # this exception is raised when ctrl-c is used to close the application on Windows, appears to be thrown twice?
    try:
        quit()
    except KeyboardInterrupt:
        sys.exit(0)
