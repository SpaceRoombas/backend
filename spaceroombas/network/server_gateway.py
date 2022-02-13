from asyncio import queues
from twisted.internet.interfaces import IAddress
from twisted.internet import protocol, reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.task import LoopingCall
import serialization
import flats.message_type as message_type
import util
from queue import LifoQueue

class SessionClient():
    def __init__(self, id, handler) -> None:
        self.recieve_queue = LifoQueue()
        self.send_queue = LifoQueue()
        self.id = id # this may be the screen name, or a hash of the screen name
        self.username = id
        self.handler = handler

class SessionHandler(protocol.Protocol):
    def __init__(self, factory) -> None:
        super().__init__()
        self.__factory = factory
        self.__session_id = None

    def dataReceived(self, data):
        # Data is sent and recieved as [buffersz + buffer]
        # buffersz is a 4 byte integer
        data_array = bytearray(data)
        buffersz = int.from_bytes(data_array[:4], byteorder='big') # First four bytes
        buffer = data_array[4:] # Remainder

        if len(buffer) == buffersz:
            self.dispatch_carrier_deserialize(buffer)
        else:
            raise RuntimeError("Recieved object of mismatched size")

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
        # TODO Check if session object exists already (reconnect)

        # Create session object
        self.__factory.add_session(SessionClient(self.__session_id, self))

    def dispatch_carrier_deserialize(self, carrier_bytes):
        carrier = serialization.deserialize_carrier(carrier_bytes)
        message = None

        # Determine if message requies immediate service or 3-day shipping
        if util.is_immediate(carrier):
            # do stuff, return. For now, handle a handshake!
            if carrier.type == message_type.message_type.Handshake:
                self.handle_handshake(carrier.payload)
            return # immediate messages are not enqueued

        # Unpack message and enque
        try:
            self.session_queue().put(message)
        except KeyError:
            print("Session is not ready to accept messages (must complete handshake)")

    def send_message(self, message):
        pass # Message handing handled here


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


class ServerGateway():

    def __init__(self) -> None:
        self.factory = None
        pass

    def handle_messages(self):
        if self.factory is None:
            return

        for k, v in self.factory.session_clients.items():
            handler = v.handler
            queue = v.recieve_queue

            for msg in queue:
                handler.send_message(msg)
 
    def messages(self):
        messages = list()

        if self.factory is not None:
            for k, v in self.factory.session_clients.items():
                queue = v.recieve_queue
                messages.append(queue.get())  # Head of each queue is inserted into messages list

        return messages

    def start(self, port: int):
        server = TCP4ServerEndpoint(reactor, port)
        self.factory = SessionHandlerFactory()

        send_looper = LoopingCall(self.handle_messages)

        print("Starting server on %d" % (port))
        server.listen(self.factory)

        send_looper.start(0.5)
        reactor.run()

