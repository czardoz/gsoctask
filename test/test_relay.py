import socket
import unittest
import threading
import random
import string

from tcprelay import Reader, Writer, relay


class Feeder(threading.Thread):

    def __init__(self, osock):
        threading.Thread.__init__(self)

        # Create random data of length between 1kB and 2kB
        data_length = random.randint(1024, 2048)
        self.sent_string = "".join([random.choice(string.letters) for i in xrange(data_length)])

        self.osock = osock

    def run(self):
        self.osock.sendall(self.sent_string)
        self.osock.close()


class Acceptor(threading.Thread):

    def __init__(self, osock):
        threading.Thread.__init__(self)
        self.osock = osock
        self.recvd_string = ''

    def run(self):
        while True:
            data = self.osock.recv(1024)
            self.recvd_string = self.recvd_string + data
            if not data:
                break


class Relay(threading.Thread):

    def __init__(self, isock, osock):
        threading.Thread.__init__(self)
        self.reader = Reader(isock)
        self.writer = Writer(osock)
        self.isock = isock
        self.osock = osock
        self.map = {self.isock: self.reader, self.osock: self.writer}

    def run(self):
        relay(self.isock, self.osock, self.map)


class TCPRelayTest(unittest.TestCase):

    def test_relay(self):
        """ Tests the relay.
        """
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.bind(('127.0.0.1', 12345))
        serv_sock.listen(2)

        in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        in_sock.connect(('127.0.0.1', 12345))
        out_sock.connect(('127.0.0.1', 12345))

        conn_in, addr = serv_sock.accept()
        conn_out, addr = serv_sock.accept()

        fdr = Feeder(in_sock)
        acc = Acceptor(out_sock)
        rel = Relay(conn_in, conn_out)

        rel.start()
        acc.start()
        fdr.start()

        fdr.join()
        acc.join()
        rel.join()
        serv_sock.close()

        # At the end, the string sent by the Feeder and the string received by the
        # Acceptor should be the same.
        self.assertEquals(fdr.sent_string, acc.recvd_string)

if __name__ == '__main__':
    unittest.main()
