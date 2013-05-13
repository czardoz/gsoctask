Python TCP Relay
------------------

This is a TCP socket relay written in python. Have a look at tcprelay.py
to see how it works! :-)

Usage
~~~~~~

You can run the tcprelay module like this:

.. code-block:: shell

    $ python tcprelay.py [PORT]

The ``PORT`` argument is optional, and it runs by default on port 8888
The data is relayed from the first client who connects to the server to the
second client which connects.
