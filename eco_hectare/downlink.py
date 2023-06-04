import time
import os
import sys

import grpc
from chirpstack_api.as_pb.external import api

def send_downlink(dev_eui, data=[0x01], f_port=2):
    # Configuration.

    # This must point to the API interface.
    server = "localhost:8080"

    # The DevEUI for which you want to enqueue the downlink.
    #"3d c3 95 24 1c 7f 85 01"
    #dev_eui = bytes([0xe1, 0x8a, 0xef, 0x6f, 0x96, 0x1c, 0xf6, 0x7a])
    #dev_eui = 'e18aef6f961cf67a'

    # The API token (retrieved using the web-interface).
    api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiYmVmMTMwMzctODZkNC00YmJmLWJhOWEtZjIyNjAwYTJhYmNmIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY4MDQyOTQ4OCwic3ViIjoiYXBpX2tleSJ9.UZizFCS3xVk6SbC7XJkLxURB8FF_UEF4fhoFsABOB3k"

    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.DeviceQueueServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.EnqueueDeviceQueueItemRequest()
    req.device_queue_item.confirmed = True
    req.device_queue_item.data = bytes(data)
    req.device_queue_item.dev_eui = dev_eui
    #req.device_queue_item.dev_eui = dev_eui.hex()
    req.device_queue_item.f_port = f_port

    resp = client.Enqueue(req, metadata=auth_token)
