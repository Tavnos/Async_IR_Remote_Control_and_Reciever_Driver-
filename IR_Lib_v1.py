import time
import machine as mc
import random as rd
import uasyncio as ao


class irGetCMD:
    dictKeyNum = 0
    logList = []
    irDict = {}
    index = 0
    start = 0
    def __init__(self, gpioNum):
        self.irRecv = mc.Pin(gpioNum, mc.Pin.IN, mc.Pin.PULL_UP)
        self.irRecv.irq(trigger=mc.Pin.IRQ_RISING | mc.Pin.IRQ_FALLING, handler=self.logHandler)
    def logHandler(self, source):
        thisComeInTime = time.ticks_us()  # Synchronisation
        if self.start == 0:
            self.start = thisComeInTime
            self.index = 0
            return
        self.logList.append(time.ticks_diff(thisComeInTime, self.start))
        self.start = thisComeInTime
        self.index += 1
    def ir_read(self):
        time.sleep_ms(500) 
        if time.ticks_diff(time.ticks_us(),self.start) > 800000 and self.index > 0:
            ir_buffer=[]
            for i in range(3,66,2):
                if self.logList[i]>800:
                    ir_buffer.append(1)
                else:
                    ir_buffer.append(0)
            irValue=0x00000000
            for i in range(0,4):
                for j in range(0,8):
                    if ir_buffer[i*8+j]==1:
                        irValue=irValue<<1
                        irValue |= 0x01
                    else:
                        irValue=irValue<<1
                        irValue &= 0xfffffffe                    
            self.logList = []
            self.index = 0
            self.start = 0
            return hex(irValue)
        
class Ir_Translate:
    d_btn={'0xffa25d':'Power',   '0xffb04f':'C', 
           '0xffe21d':'Menu',    '0xff30cf':'1', 
           '0xff22dd':'Test',    '0xff18e7':'2',
           '0xff02fd':'Plus',    '0xff7a85':'3', 
           '0xffc23d':'Return',  '0xff10ef':'4', 
           '0xffe01f':'Back',    '0xff38c7':'5', 
           '0xffa857':'Play',    '0xff5aa5':'6', 
           '0xff906f':'Forward', '0xff42bd':'7', 
           '0xff6897':'0',       '0xff4ab5':'8', 
           '0xff9867':'Minus',   '0xff52ad':'9'}
    recvPin = irGetCMD(15)
    async def read_ir(self):
        for i in range(2):
            self.irValue = self.recvPin.ir_read()
            if self.irValue not in self.d_btn:
                time.sleep_ms(250)
                self.irValue = self.recvPin.ir_read()
                time.sleep_ms(250)
            if self.irValue in self.d_btn:
                time.sleep_ms(500)
                return self.irValue
