import select
import socket
import sys


def relay(isock, osock, mapdict):
    """ Custom IO Loop which relays data between two sockets.
        :param isock: The socket to read data from.
        :param osock: The socket to write the data to.
    """

    while True:
        r, w, e = select.select([isock], [osock], [])
        # Only write if writing socket is ready and reading socket has data
        if r and w:
            reader = mapdict[r[0]]
            writer = mapdict[w[0]]
            data = reader.pull_data()
            if not data:
                break
            try:
                writer.push_data(data)
            except socket.error as e:
                break


class Reader(object):
    """ Reads data from a socket. """

    def __init__(self, sock):
        """ Instantiates a Reader class object, which
            is used to handle the connection where the data has to be
            read from.

            :param sock: A readable socket object.
        """
        self.sock = sock

    def pull_data(self):
        data = self.sock.recv(1024)
        return data


class Writer(object):
    """ Writes data to a socket. """

    def __init__(self, sock):
        """ Instantiates a Writer class object, which
            is used to handle the connection where the data has to be
            forwarded.

            :param sock: A writable socket object.
        """
        self.sock = sock

    def push_data(self, data):
        """ Sends data over the socket object.

            :param data: The string to be sent.
        """
        self.sock.sendall(data)

if __name__ == '__main__':

    host = '127.0.0.1'

    if len(sys.argv) == 1:
        port = 8888
    elif len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except ValueError as e:
            print 'Invalid port number specified, using default.'
            port = 8888
    else:
        print 'Usage: %s [port number]' % sys.argv[0]
        sys.exit(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except Exception as e:
        print 'Bind failed, exiting'
        sys.exit(1)

    s.listen(2)

    try:
        conn_in, addr = s.accept()
        print 'Reading data from: ', addr
        conn_out, addr = s.accept()
        print 'Writing data to: ', addr
        reader = Reader(conn_in)
        writer = Writer(conn_out)
        map_ = {conn_in: reader, conn_out: writer}
        relay(conn_in, conn_out, map_)
    except KeyboardInterrupt as e:
        print 'TCP Relay stopped.'
