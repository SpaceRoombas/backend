from queue import Queue, Empty
from twisted.internet.interfaces import IAddress
from twisted.internet import protocol, reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.task import LoopingCall
from data.messages import Handshake
import logging

from data import serialization

from data.messages import NewConnectionMessage

QUEUE_TIMEOUT = 0.3
QUEUE_FLUSH_RATE = 200

immediates = [
    'invalid',
    'handshake'
]


def is_immediate(carrier):
    return carrier.type in immediates


class ClientMessageWrapper():

    def __init__(self, clientid, message) -> None:
        self.client = clientid
        self.message = message


class SessionClient():
    def __init__(self, id, handler) -> None:
        self.recieve_queue = Queue()
        self.send_queue = Queue()
        self.id = id  # this may be the screen name, or a hash of the screen name
        self.username = id
        self.handler = handler

    def tick_flush_send_queue(self, flush_max=1):
        msg = None
        encoded = None
        try:
            while flush_max > 0:
                flush_max = flush_max - 1
                msg = self.send_queue.get(True, QUEUE_TIMEOUT)
                encoded = bytes(msg, 'utf-8')
                self.handler.send_data(encoded)
        except Empty:
            pass  # send queue empty

    def tick_send_message(self):
        try:
            msg = self.send_queue.get(True, QUEUE_TIMEOUT)
            encoded = bytes(msg, 'utf-8')
            self.handler.send_data(encoded)
        except Empty:
            pass  # send queue empty


class SessionHandler(protocol.Protocol):
    def __init__(self, factory) -> None:
        super().__init__()
        self.__factory = factory
        self.__session_id = None

    def dataReceived(self, data):
        # Data is sent and recieved as [buffersz + buffer]
        # buffersz is a 4 byte integer
        data_array = bytearray(data)
        buffersz = int.from_bytes(
            data_array[:4], byteorder='big')  # First four bytes
        buffer = data_array[4:]  # Remainder
        bufflen = len(buffer)

        if bufflen == buffersz:
            self.dispatch_carrier_deserialize(buffer)
        else:
            logging.error(
                "Packet head size mismatch: Told '%d' bytes, got '%d" % (buffersz, bufflen))
            return

    def session_queue(self):
        session_structure = self.__factory.session_clients[self.__session_id]

        if session_structure is not None:
            return session_structure.recieve_queue
        raise KeyError("Session object hasn't been created")

    def send_data(self, buffer):
        # The client likes two buffers sent: data size => data
        bufferSz = len(buffer)
        # Always send big endian
        bufferSzBytes = bufferSz.to_bytes(4, byteorder="big")
        # Send it
        self.transport.write(bufferSzBytes)
        self.transport.write(buffer)

    def handle_handshake(self, message):
        # Check handshake signature
        self.__session_id = message.username

        # TODO Verify handshake signature

        # Create session object or find existing
        if self.__session_id not in self.__factory.session_clients.keys():
            self.__factory.add_session(SessionClient(self.__session_id, self))
        else:
            # Re add self to handler object..
            # TODO This MUST be refactored - we will probably see race conditions here
            # But essentially, this case is for a reconnect, so we will probaby need smarter
            # logic here
            logging.info("Reconnecting orphaned client")
            self.__factory.session_clients[self.__session_id].handler = self

        # TODO verify handshake
        self.send_handshake_response(
            self.__session_id, message.signature, Handshake.STATUS_OK)

        # Let game state know that a player is joined into the game
        self.session_queue().put(ClientMessageWrapper(self.__session_id,
                                                      NewConnectionMessage(self.__session_id)), False)

    def send_handshake_response(self, username, signature, status):
        hnd = Handshake(username, signature, status)
        serialized = serialization.serialize("handshake", hnd)
        encoded = bytes(serialized, 'utf-8')
        self.send_data(encoded)

    def dispatch_carrier_deserialize(self, carrier_bytes):
        if not isinstance(carrier_bytes, bytearray):
            # TODO maybe throw some sort of error here?
            return
        carrier = serialization.unpackage_carrier(carrier_bytes)

        # Determine if message requies immediate service or 3-day shipping
        if is_immediate(carrier):
            # do stuff, return. For now, handle a handshake!
            if carrier.type == 'handshake':
                self.handle_handshake(carrier.payload)
            return  # immediate messages are not enqueued

        # Unpack message and enque
        try:
            message_wrapper = ClientMessageWrapper(
                self.__session_id, carrier.payload)
            self.session_queue().put(message_wrapper, True, QUEUE_TIMEOUT)
        except KeyError:
            logging.warning(
                "Session is not ready to accept messages (must complete handshake)")


class SessionHandlerFactory(protocol.Factory):

    session_clients = dict()

    def __init__(self) -> None:
        super().__init__()

    def add_session(self, session_structure):
        if session_structure.id is None:  # cheap null-check
            return
        self.session_clients[session_structure.id] = session_structure

    def buildProtocol(self, addr: IAddress):
        return SessionHandler(self)


class RoombaNetwork():

    def __init__(self, port=9001, update_delta=0.3) -> None:
        self.factory = None
        self.__port = port
        self.delta = update_delta
        pass

    def __dispatch_client_messages(self):
        if self.factory is None:
            return

        for k, v in self.factory.session_clients.items():
            v.tick_flush_send_queue(QUEUE_FLUSH_RATE)

    def fetch_messages(self):
        messages = list()

        if self.factory is not None:
            for k, v in self.factory.session_clients.items():
                queue = v.recieve_queue
                try:
                    # Head of each queue is inserted into messages list
                    messages.append(queue.get(True, QUEUE_TIMEOUT))
                except Empty:
                    continue  # Queue is empty, continue on silently
        return messages

    def enque_message(self, clientid, message):
        try:
            packed_message = serialization.package_for_shipping(message)
        except TypeError:
            logging.info(
                "Attempted to send message without an associated mapper.. ignoring..")
            return

        self.enque_serialized(clientid, packed_message)

    def enque_serialized(self, clientid, packed_message):
        if self.factory is not None:

            if packed_message is None:
                logging.error(
                    "Object couldn't be packaged and something really bad happened")
                return

            if clientid is None:  # This message gets put into *ALL* clients
                for k, v in self.factory.session_clients.items():
                    v.send_queue.put(packed_message, False)
            else:
                try:
                    client = self.factory.session_clients[clientid]
                    client.send_queue.put(packed_message, False)
                except KeyError:
                    logging.info("Client does not exist")
                    return

    def get_clients(self):
        return self.factory.session_clients

    def start(self):
        server = TCP4ServerEndpoint(reactor, self.__port)
        self.factory = SessionHandlerFactory()

        send_looper = LoopingCall(self.__dispatch_client_messages)

        logging.info("Starting server on %d" % (self.__port))

        send_looper.start(self.delta)
        server.listen(self.factory)
        reactor.run()
