import pyb
from pyb import Pin, ADC
from time import sleep
ser = pyb.USB_VCP()
led = pyb.LED(1)
led.on()
adc_light = ADC(Pin('X12'))
adc_temp = ADC(Pin('Y12'))
while 1:
    sleep(5)
    val_light = adc_light.read()
    val_temp = adc_temp.read()
    val_sens = 'light: '+str(val_light) +',temp: '+str(val_temp)
    ser.write(val_sens +'\n')
