
import grpc
import time
from google.protobuf import empty_pb2
from concurrent import futures
from mizar.daemon.cni_service import CniServer
from mizar.daemon.droplet_service import DropletServer
import mizar.proto.cni_pb2_grpc as cni_pb2_grpc
import mizar.proto.cni_pb2 as cni_pb2
import mizar.proto.droplet_pb2_grpc as droplet_pb2_grpc
import mizar.proto.droplet_pb2 as droplet_pb2
import os
import logging
import sys
sys.path.append("/home/sherif/cloudfabric/dev/mizar")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    droplet_pb2_grpc.add_DropletServiceServicer_to_server(
        DropletServer(), server
    )

    cni_pb2_grpc.add_CniServiceServicer_to_server(
        CniServer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("server is running")
    try:
        while True:
            time.sleep(100000)
    except KeyboardInterrupt:
        server.stop(0)


serve()
