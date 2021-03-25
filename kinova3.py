import sys
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
TIMEOUT_DURATION = 10
  
def main():
    dev = usb.core.find(idVendor=0x256f, idProduct=0xc635)
    if dev is None: raise ValueError('SpaceNavigator not found');
    else: print ('SpaceNavigator found')
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    reattach = False
    if dev.is_kernel_driver_active(0):
        reattach = True
        dev.detach_kernel_driver(0)
    ep_in = dev[0][(0,0)][0]
    ep_out = dev[0][(0,0)][1]
    
    # Import the utilities helper module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    args = utilities.parseConnectionArguments() # Parse arguments
    with utilities.DeviceConnection.createTcpConnection(args) as router: # Create connection and get router
        base = BaseClient(router) # Create required services
        while 1:
            try:
                data = dev.read(ep_in.bEndpointAddress, ep_in.bLength, 0)
                def CreateCommand(vel, axys, mode):
                    command = Base_pb2.TwistCommand()
                    command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                    command.duration = 0
                    twist = command.twist
                    if mode == "linear":
                        if axys == "x":twist.linear_x = vel
                        elif axys == "y":twist.linear_y = vel
                        elif axys == "z":twist.linear_z = vel
                    elif mode == "angular":
                        if axys == "x":twist.angular_x = vel
                        elif axys == "y":twist.angular_y = vel
                        elif axys == "z":twist.angular_z = vel
                    base.SendTwistCommand(command)
                    base.Stop()
                    
                def check_for_end_or_abort(e):
                    def check(notification, e = e):
                        print("EVENT : " + \
                              Base_pb2.ActionEvent.Name(notification.action_event))
                        if notification.action_event == Base_pb2.ACTION_END \
                        or notification.action_event == Base_pb2.ACTION_ABORT:
                            e.set()
                    return check
                    
                if data[0] == 1:
                    tx = data[1] + (data[2]*256)
                    ty = data[3] + (data[4]*256)
                    tz = data[5] + (data[6]*256)
                    if data[2] > 127:tx -= 65536
                    if data[4] > 127:ty -= 65536
                    if data[6] > 127:tz -= 65536
                    print ("T: ", tx, ty, tz)
                    if tx >= 100: CreateCommand(1,"x","linear")
                    if tx <= -100: CreateCommand(-1,"x","linear")
                    if ty >= 100: CreateCommand(1,"y","linear")
                    if ty <= -100: CreateCommand(-1,"y","linear")
                    if tz >= 100: CreateCommand(1,"z","linear")
                    if tz <= -100: CreateCommand(-1,"z","linear")
                if data[0] == 2:
                    rx = data[1] + (data[2]*256)
                    ry = data[3] + (data[4]*256)
                    rz = data[5] + (data[6]*256)
                    if data[2] > 127:rx -= 65536
                    if data[4] > 127:ry -= 65536
                    if data[6] > 127:rz -= 65536
                    print ("R: ", rx, ry, rz)
                    if rx >= 100: CreateCommand(70,"x","angular")
                    if rx <= -100: CreateCommand(-70,"x","angular") 
                    if ry >= 100: CreateCommand(70,"y","angular")
                    if ry <= -100: CreateCommand(-70,"y","angular")
                    if rz >= 100: CreateCommand(100,"z","angular")
                    if rz <=  -100: CreateCommand(-100,"z","angular")

                if data[0] == 3 and data[1] == 0:
                    # Make sure the arm is in Single Level Servoing mode
                    base_servo_mode = Base_pb2.ServoingModeInformation()
                    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
                    base.SetServoingMode(base_servo_mode)
                    # Move arm to ready position
                    action_type = Base_pb2.RequestedActionType()
                    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
                    action_list = base.ReadAllActions(action_type)
                    action_handle = None
                    for action in action_list.action_list:
                        if action.name == "Home":
                            action_handle = action.handle
                    
                    e = threading.Event()
                    notification_handle = base.OnNotificationActionTopic(
                        check_for_end_or_abort(e),
                        Base_pb2.NotificationOptions())
                    base.ExecuteActionFromReference(action_handle)
                 
            except usb.core.USBError:
                print("USB error")            

if __name__ == "__main__":
    main()