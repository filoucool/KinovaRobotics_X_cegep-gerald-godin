"""
BSD 3-Clause License

Copyright (c) 2021, Félix Chenette-Stewart
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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
