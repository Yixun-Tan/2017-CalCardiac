import struct

# param adibin_file: output of 'open' command in python3 (like _io.BufferedReader)
def parse_channels(adibin_file, dbg=False):
    FILE_HEADER_LENGTH = 68
    CHANNEL_HEADER_LENGTH = 96

    ADI_FILE_HEADER_FORMAT_STRING = "<4sldlllllddllll"
    ADI_CHANNEL_HEADER_FORMAT_STRING = "<32s32sdddd"

    # Start at the beginning of the buffer
    adibin_file.seek(0)
    
    # Read in overall file header
    file_header_bytes = adibin_file.read(FILE_HEADER_LENGTH)
    
    # Parse overall file header according to format string
    magic, version, secs_per_tick, year, month, day, hour, minute, second, \
     trigger, num_channels, samples_per_channel, time_czhannel, data_format \
    = struct.unpack(ADI_FILE_HEADER_FORMAT_STRING, file_header_bytes)
    
    if dbg == True:
        print("Magic:", magic.decode('utf-8'))
        print("Version:", version)
        print("secsPerTick:", secs_per_tick)
        print("Year:", year)
        print("Month:", month)
        print("Day:", day)
        print("Hour:", hour)
        print("Second:", second)
        print("Trigger:", trigger)
        print("NChannels:", num_channels)
        print("SamplesPerChannel:", samples_per_channel)
        print("DataFormat:", data_format)
        print('---')
    
    # Figure out length of rest of the file 
    if (data_format == 1): # 8 byte double
        bytes_per_sample = 8
        sample_format_string = 'd'
    elif (data_format == 2): # 4 byte float
        bytes_per_sample = 4
        sample_format_string = 'f'
    elif (data_format == 3): # 2 byte int
        bytes_per_sample = 2
        sample_format_string = 'h'
    else:
        return ValueError('DataFormat Not Coded to 1,2,or 3')
    
    # Order of entries in the array:
    data_names = ['ChannelIndex', 'ChannelTitle', 'Units', 'Scale', 
                            'Offset', 'RangeHigh', 'RangeLow', 'ChannelData']
    data_values_list = []

    # For every channel, read the header
    for channel_num in range(0, num_channels):
        channel_title_buffer = adibin_file.read(CHANNEL_HEADER_LENGTH)
        
        # Parse Channel Title Fields
        channel_title, units, scale, offset, range_high, range_low \
        = struct.unpack(ADI_CHANNEL_HEADER_FORMAT_STRING, channel_title_buffer)
        
        # Sanity Check
        if dbg == True:
            print("ChannelTitle:", channel_title.decode('utf-8'))
            print("Units:", units.decode('utf-8'))
            print("Scale:", scale)
            print("offset:", offset)
            print("RangeHigh:", range_high)
            print("RangeLow:", range_low)
            print('---')

        # Append channel title fields to list
        data_values_list.append([channel_num,
                                 channel_title.decode('utf-8').rstrip('\0'), 
                                 units.decode('utf-8').rstrip('\0'), 
                                 scale, 
                                 offset, 
                                 range_high, 
                                 range_low,
                                 []])

    # For every signal sample
    for sample in range(0, samples_per_channel):
        # For every channel
        for channel in range(0, num_channels):           
            data_values_list[channel][7].append(struct.unpack(sample_format_string,
                                                              adibin_file.read(bytes_per_sample))[0])
    
    # Return parsed list
    return list(map(lambda x: dict(zip(data_names, x)), data_values_list))


def test(filename):
    import matplotlib.pyplot as plt

    with open(filename, "rb") as adibin_file:
        ecg_channel_data = parse_channels(adibin_file, dbg=False)

    plt.plot(ecg_channel_data[0]['ChannelData'][0:300])
    plt.show()

if __name__ == '__main__':
    import sys
    
    try:
        cmd = sys.argv[1]        
    except:
        InputError('Usage: python3 adibin2csv.py <filename.adibin/test filename.adibin>')
        
    if cmd == 'test':
        try:
            filename = sys.argv[2]
        except:
            InputError('Usage: python3 adibin2csv.py <filename.adibin/test filename.adibin>')

        if filename.endswith('.adibin'):
            test(filename)
        else:
            print('File extension must be ".adibin"')
    elif cmd.endswith('.adibin'):
        with open(cmd, 'rb') as adibin_file:
            print(parse_channels(adibin_file))
    else:
        print('Usage: python3 adibin2csv.py <test/filename.adibin>')
        
