from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement


def get_model():
    """Return a parser for HDFS sorted.log"""
    model = SequenceModelElement("hdfs", [
        DateTimeModelElement("time", b"%y%m%d %H%M%S "),
        DecimalIntegerValueModelElement("id"),
        FixedDataModelElement("space", b" "),
        FixedWordlistDataModelElement("status", [b"INFO", b"WARN", b"ERROR"]),
        DelimitedDataModelElement("dfs", b":"),
        FixedDataModelElement("colon", b": "),
        FirstMatchModelElement("type", [
            SequenceModelElement("adding", [
                FixedDataModelElement("adding", b"Adding an already existing block "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("verification", [
                FixedDataModelElement("adding", b"Verification succeeded for "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("serving", [
                DelimitedDataModelElement("ip1", b" Served block"),
                FixedDataModelElement("served", b" Served block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("to", b" to "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("exception", [
                DelimitedDataModelElement("ip1", b":Got exception while serving"),
                FixedDataModelElement("exception", b":Got exception while serving "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("to", b" to "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("receiving", [
                FixedDataModelElement("receiving", b"Receiving block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("src_str", b" src: "),
                DelimitedDataModelElement("src", b" "),
                FixedDataModelElement("dest_str", b" dest: "),
                AnyByteDataModelElement("dest")
                ]),
            SequenceModelElement("received", [
                FixedDataModelElement("received", b"Received block "),
                DelimitedDataModelElement("blk", b" "),
                FirstMatchModelElement("type", [
                    SequenceModelElement("src", [
                        FixedDataModelElement("src_str", b" src: "),
                        DelimitedDataModelElement("src", b" "),
                        FixedDataModelElement("dest_str", b" dest: "),
                        DelimitedDataModelElement("dest", b" "),
                        FixedDataModelElement("size_str", b" of size "),
                        AnyByteDataModelElement("size")
                        ]),
                    SequenceModelElement("size", [
                        FixedDataModelElement("size_str", b" of size "),
                        DecimalIntegerValueModelElement("size"),
                        FixedDataModelElement("size_str", b" from "),
                        AnyByteDataModelElement("ip")
                        ])
                    ])
                ]),
            SequenceModelElement("writeblock", [
                FixedDataModelElement("writeblock", b"writeBlock "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("exception", b" received exception"),
                AnyByteDataModelElement("exception")
                ]),
            SequenceModelElement("packetresponder", [
                FixedDataModelElement("packetresponder", b"PacketResponder "),
                FirstMatchModelElement("type", [
                    SequenceModelElement("nonex", [
                        DecimalIntegerValueModelElement("resp"),
                        FixedDataModelElement("for", b" for block "),
                        DelimitedDataModelElement("blk", b" "),
                        FirstMatchModelElement("resp_type", [
                            FixedDataModelElement("interrupted", b" Interrupted."),
                            FixedDataModelElement("terminating", b" terminating"),
                            ])
                        ]),
                    SequenceModelElement("ex", [
                        DelimitedDataModelElement("blk", b" "),
                        FixedDataModelElement("space", b" "),
                        DecimalIntegerValueModelElement("resp"),
                        AnyByteDataModelElement("exception")
                        ])
                    ])
                ]),
            SequenceModelElement("ex_wr", [
                DelimitedDataModelElement("ip1", b":Exception writing"),
                FixedDataModelElement("wr", b":Exception writing block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("mirr", b" to mirror "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("empty", [
                FixedDataModelElement("empty", b"Receiving empty packet for block "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("ex_r", [
                FixedDataModelElement("ex_r", b"Exception in receiveBlock for block "),
                DelimitedDataModelElement("blk", b" "),
                AnyByteDataModelElement("exception")
                ]),
            SequenceModelElement("changing", [
                FixedDataModelElement("changing", b"Changing block file offset of block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("from", b" from "),
                DecimalIntegerValueModelElement("offset1"),
                FixedDataModelElement("to", b" to "),
                DecimalIntegerValueModelElement("offset2"),
                FixedDataModelElement("meta", b" meta file offset to "),
                DecimalIntegerValueModelElement("offset3")
                ]),
            SequenceModelElement("trans", [
                DelimitedDataModelElement("ip1", b":Transmitted"),
                FixedDataModelElement("wr", b":Transmitted block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("to", b" to "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("failed", [
                DelimitedDataModelElement("ip1", b":Failed"),
                FixedDataModelElement("failed", b":Failed to transfer "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("to", b" to "),
                DelimitedDataModelElement("ip2", b" "),
                AnyByteDataModelElement("exception")
                ]),
            SequenceModelElement("thread", [
                DelimitedDataModelElement("ip1", b" Starting thread"),
                FixedDataModelElement("thread", b" Starting thread to transfer block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("to", b" to "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("reopen", [
                FixedDataModelElement("failed", b"Reopen Block "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("vmap", [
                FixedDataModelElement("err", b"Unexpected error trying to delete block "),
                DelimitedDataModelElement("blk", b" "),
                AnyByteDataModelElement("vmap")
                ]),
            SequenceModelElement("deleting", [
                FixedDataModelElement("deleting", b"Deleting block "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("file_str", b" file "),
                AnyByteDataModelElement("file")
                ]),
            SequenceModelElement("deleting", [
                FixedDataModelElement("allocateBlock", b"BLOCK* NameSystem.allocateBlock: "),
                DelimitedDataModelElement("file", b". "),
                FixedDataModelElement("dot", b". "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("invalidset", [
                FixedDataModelElement("invalidset", b"BLOCK* NameSystem.delete: "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("added", b" is added to invalidSet of "),
                AnyByteDataModelElement("ip")
                ]),
            SequenceModelElement("neededrep", [
                FixedDataModelElement("neededrep", b"BLOCK* Removing block "),
                DelimitedDataModelElement("blk", b" "),
                AnyByteDataModelElement("from")
                ]),
            SequenceModelElement("repl", [
                FixedDataModelElement("repl", b"BLOCK* ask "),
                DelimitedDataModelElement("ip1", b" "),
                FixedDataModelElement("to", b" to replicate "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("datanodes", b" to datanode(s) "),
                AnyByteDataModelElement("ip2")
                ]),
            SequenceModelElement("upd", [
                FixedDataModelElement("updated", b"BLOCK* NameSystem.addStoredBlock: blockMap updated: "),
                DelimitedDataModelElement("ip", b" "),
                FixedDataModelElement("to", b" is added to "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("size_str", b" size "),
                DecimalIntegerValueModelElement("size")
                ]),
            SequenceModelElement("redun", [
                FixedDataModelElement("redun", b"BLOCK* NameSystem.addStoredBlock: Redundant addStoredBlock request received for "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("on_str", b" on "),
                DelimitedDataModelElement("ip", b" "),
                FixedDataModelElement("size_str", b" size "),
                DecimalIntegerValueModelElement("size")
                ]),
            SequenceModelElement("no_file", [
                FixedDataModelElement("add", b"BLOCK* NameSystem.addStoredBlock: addStoredBlock request received for "),
                DelimitedDataModelElement("blk", b" "),
                FixedDataModelElement("on_str", b" on "),
                DelimitedDataModelElement("ip", b" "),
                FixedDataModelElement("size_str", b" size "),
                DecimalIntegerValueModelElement("size"),
                FixedDataModelElement("no_file", b" But it does not belong to any file.")
                ]),
            SequenceModelElement("pending", [
                FixedDataModelElement("pending", b"PendingReplicationMonitor timed out block "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("del", [
                FixedDataModelElement("del", b"BLOCK* ask "),
                DelimitedDataModelElement("ip1", b" "),
                FixedDataModelElement("to", b" to delete "),
                AnyByteDataModelElement("blk")
                ]),
            SequenceModelElement("cannot", [
                DelimitedDataModelElement("ip1", b":DataXceiver:"),
                FixedDataModelElement("xceiver", b":DataXceiver: java.io.IOException: Block "),
                DelimitedDataModelElement("blk", b" "),
                FirstMatchModelElement("valid", [
                    FixedDataModelElement("valid", b" is valid, and cannot be written to."),
                    FixedDataModelElement("notvalid", b" is not valid."),
                    ]),
                ]),
            SequenceModelElement("access", [
                FixedDataModelElement("access", b"org.apache.hadoop.util.Shell$ExitCodeException: du: cannot access `/mnt/hadoop/dfs/data/tmp/"),
                DelimitedDataModelElement("blk", b"':"),
                FixedDataModelElement("no_file", b"': No such file or directory"),
                ])
            ])
        #AnyByteDataModelElement("remainder")
        ])
    return model
