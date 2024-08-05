import zmq
import zmq.asyncio
import asyncio
import time

IPC_SOCK = "/tmp/aminer"
ZMQ = "/tmp/zmq"
topic = "test_topic"
context = zmq.asyncio.Context()

async def client():
    socket = context.socket(zmq.SUB)
    socket.connect(f"ipc://{IPC_SOCK}")
    socket.subscribe(topic)

    with open(ZMQ, "w") as f:
        while True:
            value = await socket.recv_string()
            value = value.replace(topic, "")
            if value != "":
                f.write(value)
                f.flush()


async def main():
    await asyncio.gather(client())


if __name__ == "__main__":
    asyncio.run(main())
