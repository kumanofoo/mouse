#! /usr/bin/python
import struct
import time
import sys

infile_path = "/dev/input/event0"

### mx is rotation angle (forward is pi/2)
##theta = pi/2 - mx/L
# mx is rotation angle (forward is 0)
# clockwise theta < 0, mx > 0
# counterclockwise theta > 0, mx < 0
#theta = - mx/L # [rad]
#
# dy is forward
# forward: forward > 0, my > 0
# backward: forward < 0, my < 0
#forward = my

# Motor R
#  GPIO7:INA1
#  GPIO8:INA2
# Motor L
#  GPIO25:INB1
#  GPIO24:INB2

# initialize device driver
# echo 7 > /sys/class/gpio/export
# echo 8 > /sys/class/gpio/export
# echo 18 > /sys/class/gpio/export
# echo 24 > /sys/class/gpio/export
# echo 25 > /sys/class/gpio/export
#
# echo out > /sys/class/gpio/gpio7/direction
# echo out > /sys/class/gpio/gpio8/direction
# echo out > /sys/class/gpio/gpio18/direction
# echo out > /sys/class/gpio/gpio24/direction
# echo out > /sys/class/gpio/gpio25/direction
#
# echo 0 > /sys/class/gpio/gpio7/value
# echo 0 > /sys/class/gpio/gpio8/value
# echo 1 > /sys/class/gpio/gpio18/value
# echo 0 > /sys/class/gpio/gpio24/value
# echo 0 > /sys/class/gpio/gpio25/value
#

# Command
# forward:
#  echo 1 > /sys/class/gpio/gpio7/value
#  echo 0 > /sys/class/gpio/gpio8/value
#  echo 0 > /sys/class/gpio/gpio24/value
#  echo 1 > /sys/class/gpio/gpio25/value
# stop:
#  echo 0 > /sys/class/gpio/gpio7/value
#  echo 0 > /sys/class/gpio/gpio8/value
#  echo 0 > /sys/class/gpio/gpio24/value
#  echo 0 > /sys/class/gpio/gpio25/value
# backward:
#  echo 0 > /sys/class/gpio/gpio7/value
#  echo 1 > /sys/class/gpio/gpio8/value
#  echo 1 > /sys/class/gpio/gpio24/value
#  echo 0 > /sys/class/gpio/gpio25/value

#
# /usr/include/linux/input.h
#
# struct input_event {
# 	struct timeval time;
# 	__u16 type;
# 	__u16 code;
# 	__s32 value;
# };
#
# type:
EV_REL = 0x02
# code:
REL_X     = 0x00
REL_Y     = 0x01
REL_WHEEL = 0x08
#
# mouse(made by HP)
# 45.534count/mm
C = 45.5 # [count/mm]
#long int, long int, unsigned short, unsigned short, int

#L = 4200.0
L = 55.0 # [mm]

class Mouse:
    def __init__(self):
        self.FORMAT = 'llHHi'
        self.EVENT_SIZE = struct.calcsize(self.FORMAT)
        try:
            self.in_file = open(infile_path, "rb")
        except:
            print 'cannot open ', infile_path
            exit()

    def __del__(self):
        self.in_file.close()

    def getDelta(self):
        event = self.in_file.read(self.EVENT_SIZE)
        (tv_sec, tv_usec, type, code, value) = struct.unpack(self.FORMAT, event)
        return (tv_sec, tv_usec, type, code, value)

    def getDX(self):
        while True:
            event = self.in_file.read(self.EVENT_SIZE)
            (tv_sec, tv_usec, type, code, value) = struct.unpack(self.FORMAT, event)
            if type == EV_REL and code == REL_X:
                return value/C # [mm]

    def getDY(self):
        while True:
            event = self.in_file.read(self.EVENT_SIZE)
            (tv_sec, tv_usec, type, code, value) = struct.unpack(self.FORMAT, event)
            if type == EV_REL and code == REL_Y:
                return value/C # [mm]

    def rotation(self, theta):
        if theta > 0:
            # rotate counterclockwise
            # Motor R is forward
            # Motor L is backward
            dt = -self.getDX()/L
            while theta > dt:
                dt = dt - self.getDX()/L
            # Moter stop
    
        if theta < 0:
            # rotate clockwise
            # Motor R is backward
            # Motor L is forward
            dt = -self.getDX()/L
            while theta < dt:
                dt = dt - self.getDX()/L
            # Moter stop
    

    def forward(self, l):
        if l > 0:
            # forward
            # Motor R is forward
            # Motor L is forward
            dl = -self.getDY()
            while l > dl:
                dl = dl - self.getDY()
            # Motor stop
                
        if l < 0:
            # backward
            # Motor R is backward
            # Motor L is forward
            dl = -self.getDY()
            while l < dl:
                dl = dl - self.getDY()
            # Motor stop

if __name__ == '__main__':
    a = Mouse()
    print 'start'
    #a.rotation(-3.1415/2.0);
    a.forward(-100);
    print 'stop'

    
