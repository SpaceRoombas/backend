# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class session_handshake(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = session_handshake()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAssession_handshake(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # session_handshake
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # session_handshake
    def CreationTime(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
        return 0

    # session_handshake
    def Username(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # session_handshake
    def Signature(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def Start(builder): builder.StartObject(3)
def session_handshakeStart(builder):
    """This method is deprecated. Please switch to Start."""
    return Start(builder)
def AddCreationTime(builder, creationTime): builder.PrependUint32Slot(0, creationTime, 0)
def session_handshakeAddCreationTime(builder, creationTime):
    """This method is deprecated. Please switch to AddCreationTime."""
    return AddCreationTime(builder, creationTime)
def AddUsername(builder, username): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(username), 0)
def session_handshakeAddUsername(builder, username):
    """This method is deprecated. Please switch to AddUsername."""
    return AddUsername(builder, username)
def AddSignature(builder, signature): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(signature), 0)
def session_handshakeAddSignature(builder, signature):
    """This method is deprecated. Please switch to AddSignature."""
    return AddSignature(builder, signature)
def End(builder): return builder.EndObject()
def session_handshakeEnd(builder):
    """This method is deprecated. Please switch to End."""
    return End(builder)