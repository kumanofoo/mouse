#! /usr/bin/python
import struct
import time
import sys
import RPi.GPIO as GPIO

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
# ENABLE
#  PWM:ENABLE
INA1 = 7
INA2 = 8
INB1 = 25
INB2 = 24
ENABLE = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(INA1, GPIO.OUT)
GPIO.setup(INA2, GPIO.OUT)
GPIO.setup(INB1, GPIO.OUT)
GPIO.setup(INB2, GPIO.OUT)
GPIO.setup(ENABLE, GPIO.OUT)
GPIO.output(ENABLE, True)

def stp():
    GPIO.output(INA1, False)
    GPIO.output(INA2, False)
    GPIO.output(INB1, False)
    GPIO.output(INB2, False)

def fwd():
    GPIO.output(INA1, True)
    GPIO.output(INA2, False)
    GPIO.output(INB1, True)
    GPIO.output(INB2, False)

def bwd():
    GPIO.output(INA1, True)
    GPIO.output(INA2, False)
    GPIO.output(INB1, True)
    GPIO.output(INB2, False)

def ccw():
    GPIO.output(INA1, True)
    GPIO.output(INA2, False)
    GPIO.output(INB1, False)
    GPIO.output(INB2, True)

def cw():
    GPIO.output(INA1, False)
    GPIO.output(INA2, True)
    GPIO.output(INB1, True)
    GPIO.output(INB2, False)
    
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
                print 'X:', value/C
                return value/C # [mm]

    def getDY(self):
        while True:
            event = self.in_file.read(self.EVENT_SIZE)
            (tv_sec, tv_usec, type, code, value) = struct.unpack(self.FORMAT, event)
            if type == EV_REL and code == REL_Y:
                print 'Y:', value/C
                return value/C # [mm]

    def rotation(self, theta):
        if theta > 0:
            # rotate counterclockwise
            ccw()
            dt = -self.getDX()/L
            while theta > dt:
                dt = dt - self.getDX()/L
            # Moter stop
            stp()
    
        if theta < 0:
            # rotate clockwise
            cw()
            dt = -self.getDX()/L
            while theta < dt:
                dt = dt - self.getDX()/L
            # Moter stop
            stp()

    def forward(self, l):
        if l > 0:
            # forward
            fwd()
            dl = -self.getDY()
            while l > dl:
                dl = dl - self.getDY()
                print 'dl:', dl
            # Motor stop
            stp()
            
        if l < 0:
            # backward
            bwd()
            dl = -self.getDY()
            while l < dl:
                dl = dl - self.getDY()
                print 'dl:', dl
            # Motor stop
            stp()

if __name__ == '__main__':
    a = Mouse()
    print 'start'
    a.rotation(-3.1415/2.0);
    print 'stop'
    print 'start'
    a.forward(-100);
    print 'stop'



    
