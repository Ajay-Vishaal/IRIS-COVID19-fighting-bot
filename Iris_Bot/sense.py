#library for converting the hex and binary values of data into human readable format
from __future__ import division
import struct
import _thread

# converts VOC data to units in ppb
def VOC(VOC_char):        
    VOC_data = VOC_char.read()
    VOC_data_value = struct.unpack('<h', VOC_data)
    VOC_data_value = VOC_data_value[0]
    return VOC_data_value

#converts co2 data into units in ppm
def CO2(CO2_char): 
    CO2_data = CO2_char.read()
    CO2_data_value = struct.unpack('<h', CO2_data)
    CO2_data_value = CO2_data_value[0]
    return CO2_data_value

# pressure data to 0.1Pa
def Pressure(Pressure_char): 
    Pressure_data = Pressure_char.read()
    Pressure_data_value = struct.unpack('<L', Pressure_data)
    Pressure_data_value = Pressure_data_value[0] / 1000
    return Pressure_data_value   
        
#sound into units of 0.01dB
def Sound(Sound_char): 
    Sound_data = Sound_char.read()
    Sound_data_value = struct.unpack('<h', Sound_data)
    Sound_data_value = Sound_data_value[0] / 100
    return Sound_data_value

#convert from farenheit
def Temperature(temperature_char): 
    temperature_data = temperature_char.read()
    temperature_data_value = struct.unpack('<H', temperature_data)
    temperature_data_value = temperature_data_value[0] / 100
    return temperature_data_value

#converts humidity data 
def Humidity(humidity_char): 
    humidity_data = humidity_char.read()
    humidity_data_value = struct.unpack('<H', humidity_data)
    humidity_data_value = humidity_data_value[0] / 100
    return humidity_data_value

#converts light data
def Light(light_char): 
    light_data = light_char.read()
    light_data_value = struct.unpack('<L', light_data)
    light_data_value = light_data_value[0] / 100
    return light_data_value
