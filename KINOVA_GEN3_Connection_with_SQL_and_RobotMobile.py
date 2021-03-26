import sys #import libraries and other tools/utils
import os
import time
import threading
import usb.core
import usb.util
import utilities
from kortex_api.TCPTransport import TCPTransport
from kortex_api.RouterClient import RouterClient
from kortex_api.SessionManager import SessionManager
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2
TIMEOUT_DURATION = 10 #max action wait time
  
def main():
    dev = usb.core.find(idVendor=0x256f, idProduct=0xc635) #look for 3DConnexion SpaceMouse Compact
    cfg = dev.get_active_configuration() #get configuration
    intf = cfg[(0,0)]
    ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    reattach = False
    if dev.is_kernel_driver_active(0): #attaches to device
        reattach = True
        dev.detach_kernel_driver(0)
    ep_in = dev[0][(0,0)][0] #data
    ep_out = dev[0][(0,0)][1]
    
    position = 0
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    args = utilities.parseConnectionArguments() # Parse arguments
    with utilities.DeviceConnection.createTcpConnection(args) as router: # Create connection and get router
        base = BaseClient(router) # Create required services
        while 1:
                data = dev.read(ep_in.bEndpointAddress, ep_in.bLength, 0) #reads SpaceMouse data
                    
                def check_for_end_or_abort(e):
                    def check(notification, e = e):
                        print("EVENT : " + \
                              Base_pb2.ActionEvent.Name(notification.action_event))
                        if notification.action_event == Base_pb2.ACTION_END \
                        or notification.action_event == Base_pb2.ACTION_ABORT:
                            e.set()
                    return check
                    
                if data[0] == 1: # checks the data (T) and seperates the values (XYZ)
                    tx = data[1] + (data[2]*256)
                    ty = data[3] + (data[4]*256)
                    tz = data[5] + (data[6]*256)
                    if data[2] > 127:tx -= 65536 # If data is abnormal
                    if data[4] > 127:ty -= 65536
                    if data[6] > 127:tz -= 65536
                    print ("T: ", tx, ty, tz) #prints values
                    
                if data[0] == 2: # checks the data (R) and seperates the values (XYZ)
                    rx = data[1] + (data[2]*256)
                    ry = data[3] + (data[4]*256)
                    rz = data[5] + (data[6]*256)
                    if data[2] > 127:rx -= 65536 # If data is abnormal
                    if data[4] > 127:ry -= 65536
                    if data[6] > 127:rz -= 65536
                    print ("R: ", rx, ry, rz)
                    

                if data[0] == 3 and data[1] == 0: #side button Left, goes to a sade position
                    
                    #end of main and loop
if __name__ == "__main__":
    main()