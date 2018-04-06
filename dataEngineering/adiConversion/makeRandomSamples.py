'''
********************************************************************************
Import Packages
********************************************************************************
'''

import os, random, glob


'''
********************************************************************************
*********************************Functions**************************************
********************************************************************************
'''


'''
********************************************************************************
makeRandomSamples Function
********************************************************************************
'''

def makeRandomSamples(sample_size, number_of_samples, csv_in_directory_path, dbg=False):
    
    file_name_array = glob.glob(csv_in_directory_path + '*.csv')
    
    random.shuffle(file_name_array)
    
    # Make directory path if it doesn't exist
    for j in range(number_of_samples):
        os.makedirs(os.path.dirname(csv_in_directory_path 
                      + '/' + 'batch' + str(j) + '/'), exist_ok=True)
    
    # Sort files into number_of_samples batches
    #  each of size sample_size
    if dbg == True:
        print(str(len(file_name_array)) + " files to sort")
    for j in range(number_of_samples):
        for i in range(sample_size):
            file_name_current = file_name_array.pop()
            file_name_basename = os.path.basename(file_name_current)
            os.rename(file_name_current
                      , csv_in_directory_path 
                      + 'batch' + str(j) + '/'  
                      + file_name_basename)
    
    if dbg == True:
        print(str(len(file_name_array)) + " files leftover")


'''
********************************************************************************
Do It To It
********************************************************************************
'''

csv_in_directory_path = './'
makeRandomSamples(1011,10,csv_in_directory_path, True)