'''
*******************************************************************************
Import Packages
*******************************************************************************
'''

import struct
import csv
import json
import base64
import zlib
import pprint
import numpy
import ctypes
import glob
import os
import sys
import time
import pickle


'''
*******************************************************************************
Relevant Docs
*******************************************************************************



# #### [Relevant Python Documentation for Reading C Structs into Python]\
# (https://docs.python.org/3.5/library/struct.html \
# "Python Docs for C Structs")
# 
# #### [Excellent code snippets for working with Binary data in Python]\
# (https://www.devdungeon.com/content/working-binary-data-python \
# "DevDungeon")
# 
# |doc | url |
# |-----|-----|
# | adiBin docs| http://cdn.adinstruments.com/adi-web/manuals/translatebinary/LabChartBinaryFormat.pdf |
# | adiBin header|  http://cdn.adinstruments.com/adi-web/manuals/translatebinary/ADIBinaryFormat.h |
# | adiBin example|http://cdn.adinstruments.com/adi-web/manuals/translatebinary/TranslateBinary.c |
# |source | https://forum.adinstruments.com/viewtopic.php?t=395 |

'''


'''
*******************************************************************************
*********************************Functions*************************************
*******************************************************************************
'''


'''
*******************************************************************************
Base64 to JSON Function
*******************************************************************************
'''

def base64ToJson(zippedString):
    json_str = zlib.decompress(base64.b64decode(zippedString)).decode()
    json_json = json.loads(json_str)
    return json_json


'''
*******************************************************************************
Parse CSV Function
*******************************************************************************
'''

def parseCsv(csv_row, dbg=False):
    
    ###########################################################################
    # Parse CSV Data
    ###########################################################################
    
    # Record Identifiers 
    alarm_id = csv_row[0]
    time_since_admission = csv_row[1]
    
    # Decompress channel data
    channel_json = base64ToJson(csv_row[2])
    
    
    ###########################################################################
    # Parse file header and channel header data
    ###########################################################################
    
    # Number of channels
    num_channels = len(channel_json)
    
    # Channel titles
    channel_titles = []
    for i in range(num_channels):
        channel_titles.append(channel_json[i]['Label'].upper())
        
    

    ###########################################################################
    # Parse channel data
    ###########################################################################
    
    # Convert channel data to list
    channel_data = []
    for i in range(num_channels):
        channel_data.append([int(j) for j in channel_json[i]['Text'].split(',')])
        
    
    # Check to see if all channels have the same length
    # If channels are the same length, samples_per_channel set to len element 0
    # If theres a mismatch, pad other channels with mean and
    #   set samples_per_channel to max length
    
    if all(len(i) == len(channel_data[0]) for i in channel_data):
        samples_per_channel = len(channel_data[0])
        if dbg == True:
            print("all channel_data sublists equal length")
    else:
        max_sublist_len = len(max(channel_data, key=len))
        for i in range (num_channels):
            len_dif_tuple = (0, max_sublist_len - len(channel_data[i]))
            channel_data[i] = numpy.pad(channel_data[i]
                                        , pad_width = len_dif_tuple
                                       )
        samples_per_channel = max_sublist_len
        if dbg == True:
            print("all channel_data sublists NOT equal length\
                  - padded w/ trailing means")


    ###########################################################################
    # Create dictionary of all parsed data from csv file
    ###########################################################################
    
    csv_data = {'alarm_id' : alarm_id
                , 'time_since_admission' : time_since_admission
                , 'num_channels' : num_channels
                , 'channel_titles' : channel_titles
                , 'channel_data' : channel_data
                , 'samples_per_channel' : samples_per_channel
                }
    
    
    ###########################################################################
    # Debug: Check values
    ###########################################################################
    if dbg == True:
        print("alarm_id:", alarm_id)
        print("time_since_admission:", time_since_admission)
        print("num_channels:", num_channels)
        print("channel_titles:", channel_titles)
        print("samples_per_channel:", samples_per_channel)
        print("\n")
        
    
    ###########################################################################
    # Return
    ###########################################################################
    return csv_data


'''
*******************************************************************************
Create ADIBIN Function
*******************************************************************************
'''

def createAdibin(data_dict, dbg=False):
       
    ###########################################################################
    # Define default adibin file header variables
    ###########################################################################
    
    # Define default file size variables for writing adibin file
    FILE_HEADER_LENGTH = 68
    CHANNEL_HEADER_LENGTH = 96
    # CHANNEL_TITLE_LENGTH = 32
    # UNITS_LENGTH = 32
    
    # Define format strings for struct
    ADI_FILE_HEADER_FORMAT_STRING = "<4sldlllllddllll"
    ADI_CHANNEL_HEADER_FORMAT_STRING = "<32s32sdddd"
    ADI_CHANNEL_DATA_FORMAT_STRING = "<h"
    
    # Define default file header variables
    magic = b'CFWB'
    version = 1
    secs_per_tick = 1/240
    year = 1776
    month = 7
    day = 4
    hour = 0
    minute = 0
    second = 0
    trigger = 0
    # num_channels passed in dict
    # samples_per_channel passed in dict
    time_channel = 0
    data_format = 3
    
    # Define default channel header variables
    # channel_title passed in dict
    units = {'I':b'mV'\
             , 'II':b'mV'\
             , 'III':b'mV'\
             , 'V':b'mV'\
             , 'AVR':b'mV'\
             , 'AVL':b'mV'\
             , 'AVF':b'mV'\
             , 'SPO2':b'%'\
             , 'RR':b'Imp'\
             , 'RESP':b'Imp'\
             , 'AR1':b'mmHg'\
             , 'AR2':b'mmHg'\
             , 'AR3':b'mmHg'\
             , 'AR4':b'mmHg'\
             , 'AR5':b'mmHg'\
             , 'AR6':b'mmHg'\
             , 'AR7':b'mmHg'\
             , 'AR8':b'mmHg'\
             , 'CVP1':b'mmHg'\
             , 'CVP2':b'mmHg'\
             , 'CVP3':b'mmHg'\
             , 'CVP4':b'mmHg'\
             , 'CVP5':b'mmHg'\
             , 'CVP6':b'mmHg'\
             , 'CVP7':b'mmHg'\
             , 'CVP8':b'mmHg'\
             , 'FE1':b'mmHg'\
             , 'FE2':b'mmHg'\
             , 'FE3':b'mmHg'\
             , 'FE4':b'mmHg'\
             , 'FE5':b'mmHg'\
             , 'FE6':b'mmHg'\
             , 'FE7':b'mmHg'\
             , 'FE8':b'mmHg'\
             , 'FEM1':b'mmHg'\
             , 'FEM2':b'mmHg'\
             , 'FEM3':b'mmHg'\
             , 'FEM4':b'mmHg'\
             , 'FEM5':b'mmHg'\
             , 'FEM6':b'mmHg'\
             , 'FEM7':b'mmHg'\
             , 'FEM8':b'mmHg'\
             , 'ICP1':b'mmHg'\
             , 'ICP2':b'mmHg'\
             , 'ICP3':b'mmHg'\
             , 'ICP4':b'mmHg'\
             , 'ICP5':b'mmHg'\
             , 'ICP6':b'mmHg'\
             , 'ICP7':b'mmHg'\
             , 'ICP8':b'mmHg'\
             , 'ICT1':b'mmHg'\
             , 'ICT2':b'mmHg'\
             , 'ICT3':b'mmHg'\
             , 'ICT4':b'mmHg'\
             , 'ICT5':b'mmHg'\
             , 'ICT6':b'mmHg'\
             , 'ICT7':b'mmHg'\
             , 'ICT8':b'mmHg'\
             , 'IRV':b'-'\
             , 'LA1':b'mmHg'\
             , 'LA2':b'mmHg'\
             , 'LA3':b'mmHg'\
             , 'LA4':b'mmHg'\
             , 'LA5':b'mmHg'\
             , 'LA6':b'mmHg'\
             , 'LA7':b'mmHg'\
             , 'LA8':b'mmHg'\
             , 'PA1':b'mmHg'\
             , 'PA2':b'mmHg'\
             , 'PA3':b'mmHg'\
             , 'PA4':b'mmHg'\
             , 'PA5':b'mmHg'\
             , 'PA6':b'mmHg'\
             , 'PA7':b'mmHg'\
             , 'PA8':b'mmHg'\
             , 'RA1':b'mmHg'\
             , 'RA2':b'mmHg'\
             , 'RA3':b'mmHg'\
             , 'RA4':b'mmHg'\
             , 'RA5':b'mmHg'\
             , 'RA6':b'mmHg'\
             , 'RA7':b'mmHg'\
             , 'RA8':b'mmHg'\
             , 'SP1':b'-'\
             , 'SP2':b'-'\
             , 'SP3':b'-'\
             , 'SP4':b'-'\
             , 'SP5':b'-'\
             , 'SP6':b'-'\
             , 'SP7':b'-'\
             , 'SP8':b'-'\
             , 'V1':b'mV'\
             , 'V2':b'mV'\
             , 'V3':b'mV'\
             , 'V4':b'mV'\
             , 'V5':b'mV'\
             , 'V6':b'mV'\
             , 'V7':b'mV'\
             , 'V8':b'mV'\
             , '':b'blank'\
             }
    scale = {'I': 2.44\
             , 'II': 2.44\
             , 'III': 2.44\
             , 'V': 2.44\
             , 'AVR': 2.44\
             , 'AVL': 2.44\
             , 'AVF': 2.44\
             , 'SPO2': 1.0\
             , 'RR': 0.1\
             , 'RESP': 0.1\
             , 'AR1': 0.2\
             , 'AR2': 0.2\
             , 'AR3': 0.2\
             , 'AR4': 0.2\
             , 'AR5': 0.2\
             , 'AR6': 0.2\
             , 'AR7': 0.2\
             , 'AR8': 0.2\
             , 'CVP1': 0.2\
             , 'CVP2': 0.2\
             , 'CVP3': 0.2\
             , 'CVP4': 0.2\
             , 'CVP5': 0.2\
             , 'CVP6': 0.2\
             , 'CVP7': 0.2\
             , 'CVP8': 0.2\
             , 'FE1': 0.2\
             , 'FE2': 0.2\
             , 'FE3': 0.2\
             , 'FE4': 0.2\
             , 'FE5': 0.2\
             , 'FE6': 0.2\
             , 'FE7': 0.2\
             , 'FE8': 0.2\
             , 'FEM1': 0.2\
             , 'FEM2': 0.2\
             , 'FEM3': 0.2\
             , 'FEM4': 0.2\
             , 'FEM5': 0.2\
             , 'FEM6': 0.2\
             , 'FEM7': 0.2\
             , 'FEM8': 0.2\
             , 'IRV': 1.0\
             , 'ICP1': 0.2\
             , 'ICP2': 0.2\
             , 'ICP3': 0.2\
             , 'ICP4': 0.2\
             , 'ICP5': 0.2\
             , 'ICP6': 0.2\
             , 'ICP7': 0.2\
             , 'ICP8': 0.2\
             , 'ICT1': 0.2\
             , 'ICT2': 0.2\
             , 'ICT3': 0.2\
             , 'ICT4': 0.2\
             , 'ICT5': 0.2\
             , 'ICT6': 0.2\
             , 'ICT7': 0.2\
             , 'ICT8': 0.2\
             , 'LA1':0.2\
             , 'LA2':0.2\
             , 'LA3':0.2\
             , 'LA4':0.2\
             , 'LA5':0.2\
             , 'LA6':0.2\
             , 'LA7':0.2\
             , 'LA8':0.2\
             , 'PA1': 0.2\
             , 'PA2': 0.2\
             , 'PA3': 0.2\
             , 'PA4': 0.2\
             , 'PA5': 0.2\
             , 'PA6': 0.2\
             , 'PA7': 0.2\
             , 'PA8': 0.2\
             , 'RA1': 0.2\
             , 'RA2': 0.2\
             , 'RA3': 0.2\
             , 'RA4': 0.2\
             , 'RA5': 0.2\
             , 'RA6': 0.2\
             , 'RA7': 0.2\
             , 'RA8': 0.2\
             , 'SP1': 1.0\
             , 'SP2': 1.0\
             , 'SP3': 1.0\
             , 'SP4': 1.0\
             , 'SP5': 1.0\
             , 'SP6': 1.0\
             , 'SP7': 1.0\
             , 'SP8': 1.0\
             , 'V1': 2.44\
             , 'V2': 2.44\
             , 'V3': 2.44\
             , 'V4': 2.44\
             , 'V5': 2.44\
             , 'V6': 2.44\
             , 'V7': 2.44\
             , 'V8': 2.44\
             , '': 1.0\
             }
    offset = 0
    range_high = 1
    range_low = 0
    # channel_data passed in dict
    
    
    ###########################################################################
    # Create units and scales fields from channel titles  passed in dict
    ###########################################################################
    
    # If the channel title being passed is not present in the units or scale
    #  dictionaries, these statements will fail
    
    # Channel units
    channel_units = []
    for i in range(data_dict['num_channels']):
        channel_units.append(units[data_dict['channel_titles'][i]])
        
    # Channel scales
    channel_scales = []
    for i in range(data_dict['num_channels']):
        channel_scales.append(scale[data_dict['channel_titles'][i]])
            
   
    ###########################################################################
    # Convert channel titles passed in dict to binary strings
    ###########################################################################
    
    # New list for binary channel titles
    bin_channel_titles = []
    for i in range(data_dict['num_channels']):
        bin_channel_titles.append(\
                                data_dict['channel_titles'][i].encode('utf-8'))
    
    ###########################################################################
    # Append all adibin fields to list of lists
    ###########################################################################
    
    # Append file header    
    adibin_header = []
    
    adibin_header.append(magic)
    adibin_header.append(version)
    adibin_header.append(secs_per_tick)
    adibin_header.append(year)
    adibin_header.append(month)
    adibin_header.append(day)
    adibin_header.append(hour)
    adibin_header.append(minute)
    adibin_header.append(second)
    adibin_header.append(trigger)
    adibin_header.append(data_dict['num_channels'])
    adibin_header.append(data_dict['samples_per_channel'])
    adibin_header.append(time_channel)
    adibin_header.append(data_format)
 
    # Append channel headers
    adibin_channel_headers = []

    for i in range(data_dict['num_channels']):
        adibin_channel_headers.append(bin_channel_titles[i])
        adibin_channel_headers.append(channel_units[i])
        adibin_channel_headers.append(channel_scales[i])
        adibin_channel_headers.append(offset)
        adibin_channel_headers.append(range_high)
        adibin_channel_headers.append(range_low)
        
    # Append interleaved channel data
    adibin_channel_data = []
    
    for j in range(data_dict['samples_per_channel']):
        for i in range(data_dict['num_channels']):
            adibin_channel_data.append(data_dict['channel_data'][i][j])
        
    
    
    ###########################################################################
    # Pack adibin data into writable struct buffers
    ###########################################################################

    ###########################################################################
    # Pack file header
    # Create placeholder buffer of the right size
    file_header_buffer = bytearray(FILE_HEADER_LENGTH)
    
    # Pack file header
    struct.pack_into(ADI_FILE_HEADER_FORMAT_STRING
                     , file_header_buffer
                     , 0
                     , *adibin_header
                     )

    ###########################################################################
    # Pack channel headers
    # Create format string of right length for num_channels
    channel_headers_format_string = ADI_CHANNEL_HEADER_FORMAT_STRING
    for i in range(data_dict['num_channels'] - 1):
        channel_headers_format_string += ADI_CHANNEL_HEADER_FORMAT_STRING[1:]
    
    # Create placeholder buffer of the right size
    channel_headers_buffer = bytearray((data_dict['num_channels']) \
                                       * CHANNEL_HEADER_LENGTH)
    
    # Pack channel headers
    struct.pack_into(channel_headers_format_string
                     , channel_headers_buffer
                     , 0
                     , *adibin_channel_headers
                     )

    ###########################################################################
    # Pack channel data
    # Create format string to write all the interwoven channel data
    channel_data_format_string = ADI_CHANNEL_DATA_FORMAT_STRING
    for i in range(\
        ((data_dict['num_channels'])*(data_dict['samples_per_channel']))- 1):
        channel_data_format_string += ADI_CHANNEL_DATA_FORMAT_STRING[1:]
    
    # Create placeholder buffer of the right size
    channel_data_buffer = bytearray(struct.calcsize(channel_data_format_string))
    
    # Pack channel data
    struct.pack_into(channel_data_format_string
                     , channel_data_buffer
                     , 0
                     , *adibin_channel_data
                     )

    
    ###########################################################################
    # Debug: Check values
    ###########################################################################
    if dbg == True:
        print("channel_units:", channel_units)
        print("channel_scales:", channel_scales)
        print("adibin_data[0]:", adibin_data[0])
        print('\n')
        
        
    ###########################################################################
    # Return packed adibin buffers
    ###########################################################################
    
    # Create dictionary of packed buffers for return
    adibin_data = {'alarm_id': data_dict['alarm_id']
                  , 'time_since_admission': data_dict['time_since_admission']
                  , 'file_header': file_header_buffer
                  , 'channel_headers': channel_headers_buffer
                  , 'channel_data': channel_data_buffer
                  }
    
    return adibin_data


'''
*******************************************************************************
Write ADIBIN Function
*******************************************************************************
'''

def writeAdibin(adibin_data, csv_filename, output_directory, dbg=False):
    
    # Create output filename
    filename = output_directory \
                + csv_filename \
                + "_" \
                + adibin_data['alarm_id'] \
                + "_" \
                + adibin_data['time_since_admission'] \
                + ".adibin"
    
    # If directory does not exist, create it
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write the returned content to a file in the output directory
    # overwrite previous file without warning
    with open(filename, 'wb') as adibin_file:
        adibin_file.write(adibin_data['file_header'])
        adibin_file.write(adibin_data['channel_headers'])
        adibin_file.write(adibin_data['channel_data'])

    if dbg == True:
        print("Writing:", filename)


'''
*******************************************************************************
Write CSV Row to Pickle
*******************************************************************************
'''

def pickleMe(csv_data, csv_filename, output_directory, dbg=False):
    
    # Create output filename
    filename = output_directory \
                + csv_filename \
                + "_" \
                + csv_data['alarm_id'] \
                + "_" \
                + csv_data['time_since_admission'] \
                + ".pickle"

    # If directory does not exist, create it
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write the returned content to a file in the output directory
    # overwrite previous file without warning
    with open(filename, 'wb') as pickle_file:
        pickle.dump(csv_data, pickle_file)
        
    if dbg == True:
        print("Writing:", filename)


'''
*******************************************************************************
Progress Bar Function
*******************************************************************************
'''

def printProgress(current_iteration, total_iterations, fill = '█'):
    
    # Default variables
    bar_length = 70
    
    # Calculate percent complete
    percent_complete = current_iteration / float(total_iterations)
    
    # Calculate filled length
    filled_length = int(round(bar_length * percent_complete))
    
    # Create bar and message
    percent_complete_msg = round(100.0 * percent_complete, 1)
    progress_bar = fill * filled_length \
                 + '-' * (bar_length - filled_length)
    
    sys.stdout.write('\r%s |%s| %s%% %s' % \
                     ('progress:'
                      , progress_bar
                      , percent_complete_msg
                      , 'complete'
                      )
                    )
    sys.stdout.flush()


'''
*******************************************************************************
Nicely Wrapped CSV to ADIBIN Function
*******************************************************************************
'''

def csvToAdibin(csv_in_directory_path, adibin_out_directory_path, dbg=False):
    
    # Size of job for dbg progress bar
    if dbg == True:
        num_files_to_convert = \
            len([name for name in os.listdir(csv_in_directory_path)\
            if os.path.isfile(os.path.join(csv_in_directory_path, name))])
        
        current_iteration = 0
        
        printProgress(current_iteration, num_files_to_convert)
        
    
    # For every csv file in the csv_in_directory_path
    for csv_filename in glob.glob(csv_in_directory_path + '*.csv'):
        
        # Parse admission_id from csv_filename
        csv_basename = os.path.basename(csv_filename)
        admission_id = csv_basename[:-4]
        
        # Open CSV File
        with open(csv_filename) as csv_file:
            
            # Parse and write out ADIBIN for every row in the CSV
            try:
                csv_file_reader = csv.reader(csv_file)
                for row in csv_file_reader:
                    try: 
                        writeAdibin(createAdibin(parseCsv(row, dbg=False), dbg=False)
                                    , admission_id
                                    , adibin_out_directory_path
                                    , dbg = False
                                    )
                    except:
                        # Create problemFile directory to catch problem files
                        os.makedirs(os.path.dirname("./problemPickles/"), exist_ok=True)
                        # Write csv row to pickle
                        pickleMe(parseCsv(row, dbg=False)
                                 , admission_id
                                 , "./problemPickles/"
                                 , dbg=False
                                 )
            except:
                # Create problemFile directory to catch problem files
                os.makedirs(os.path.dirname("./problemFiles/"), exist_ok=True)
                # Move problem csv file to the problemFiles directory
                os.rename(csv_filename
                         , "./problemFiles/" + csv_basename)


            if dbg == True:
                current_iteration += 1
                if current_iteration <= num_files_to_convert:
                    printProgress(current_iteration, num_files_to_convert)
                else:
                    printProgress(1,1)


'''
*******************************************************************************
Do It To It
*******************************************************************************
'''

csv_directory_path = "./csvFiles/"
adibin_directory_path = "./generatedAdibins/"

start_time = time.time()
csvToAdibin(csv_directory_path, adibin_directory_path, dbg=True)
end_time = time.time()
printProgress(1,1)
print("\nran in %s seconds" % (end_time - start_time))


'''
*******************************************************************************
Sanity Check
*******************************************************************************
'''
'''
#csv_file_name = "./sampleFiles/4b80ff2eb1112815299d7a4e9a4a1957.csv"
csv_directory_path = "./sampleFiles/"
adibin_directory_path = "./testOutsAdibin/"

start_time = time.time()
csvToAdibin(csv_directory_path, adibin_directory_path, dbg=True)
end_time = time.time()
printProgress(1,1)
print("\nran in %s seconds" % (end_time - start_time))
'''