# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class GameMap(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = GameMap()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsGameMap(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # GameMap
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # GameMap
    def Chunk(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # GameMap
    def LandMap(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Int8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # GameMap
    def LandMapAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Int8Flags, o)
        return 0

    # GameMap
    def LandMapLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # GameMap
    def LandMapIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

def Start(builder): builder.StartObject(2)
def GameMapStart(builder):
    """This method is deprecated. Please switch to Start."""
    return Start(builder)
def AddChunk(builder, chunk): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(chunk), 0)
def GameMapAddChunk(builder, chunk):
    """This method is deprecated. Please switch to AddChunk."""
    return AddChunk(builder, chunk)
def AddLandMap(builder, landMap): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(landMap), 0)
def GameMapAddLandMap(builder, landMap):
    """This method is deprecated. Please switch to AddLandMap."""
    return AddLandMap(builder, landMap)
def StartLandMapVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def GameMapStartLandMapVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartLandMapVector(builder, numElems)
def End(builder): return builder.EndObject()
def GameMapEnd(builder):
    """This method is deprecated. Please switch to End."""
    return End(builder)