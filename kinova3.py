import sys
import os
import time
import threading
import usb.core
import usb.util

from time import gmtime, strftime
from kortex_api.TCPTransport import TCPTransport
from kortex_api.RouterClient import RouterClient
from kortex_api.SessionManager import SessionManager
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2
TIMEOUT_DURATION = 10

def check_for_end_or_abort(e):
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check
  
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
    import utilities
    # Parse arguments
    args = utilities.parseConnectionArguments()
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        # Create required services
        base = BaseClient(router)
        # Example core
        success = True
        while 1:
            try:
                data = dev.read(ep_in.bEndpointAddress, ep_in.bLength, 0)
                if data[0] == 1:
                    tx = data[1] + (data[2]*256)
                    ty = data[3] + (data[4]*256)
                    tz = data[5] + (data[6]*256)
                    if data[2] > 127:
                        tx -= 65536
                    if data[4] > 127:
                        ty -= 65536
                    if data[6] > 127:
                        tz -= 65536
                    print ("T: ", tx, ty, tz)
                    if tx >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_x = 1
                        base.SendTwistCommand(command)
                        base.Stop()
                    if tx <= -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_x = -1
                        base.SendTwistCommand(command)
                        base.Stop()
                    if ty >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_y = 1
                        base.SendTwistCommand(command)
                        base.Stop()
                    if ty <= -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_y = -1
                        base.SendTwistCommand(command)
                        base.Stop()
                    if tz >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_z = 1
                        base.SendTwistCommand(command)
                        base.Stop()
                    if tz <= -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.linear_z = -1
                        base.SendTwistCommand(command)
                        base.Stop()
          
                if data[0] == 2:
                    rx = data[1] + (data[2]*256)
                    ry = data[3] + (data[4]*256)
                    rz = data[5] + (data[6]*256)
                    if data[2] > 127:
                        rx -= 65536
                    if data[4] > 127:
                        ry -= 65536
                    if data[6] > 127:
                        rz -= 65536
                    print ("R: ", rx, ry, rz)
                    if rx >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_x = 70
                        base.SendTwistCommand(command)
                        base.Stop()
                    if rx <= -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_x = -70
                        base.SendTwistCommand(command)
                        base.Stop() 
                    if ry >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_y = 70
                        base.SendTwistCommand(command)
                        base.Stop()
                    if ry <= -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_y = -70
                        base.SendTwistCommand(command)
                        base.Stop()
                    if rz >= 100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_z = 100
                        base.SendTwistCommand(command)
                        base.Stop()
                    if rz <=  -100:
                        command = Base_pb2.TwistCommand()
                        command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
                        command.duration = 0
                        twist = command.twist
                        twist.angular_z = -100
                        base.SendTwistCommand(command)
                        base.Stop()

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

                    if action_handle == None:
                        print("Can't reach safe position.")

                    e = threading.Event()
                    notification_handle = base.OnNotificationActionTopic(
                        check_for_end_or_abort(e),
                        Base_pb2.NotificationOptions()
                    )
                    base.ExecuteActionFromReference(action_handle)
                        
            except usb.core.USBError:
                print("USB error")
        return 0 if success else 1
            

if __name__ == "__main__":
    main()