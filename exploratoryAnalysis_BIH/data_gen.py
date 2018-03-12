import scipy as sci
import wfdb
import os
import json

class data_gen(object):

    def __init__(self, window_size):
        self.__doc__ = 
        """This class converts ECG signals from MIT-BIH Arrhythmia dataset and labels into structured, tabular data.
    
        """
        # Data Parameters
        self.data_dir = 'MIT-BIH/'
        
        self.record_numbers = set(map(lambda x: x.split('.')[0], os.listdir('MIT-BIH/')))
        self.all_patients_data = dict([(record_num, []) for record_num in self.record_numbers])

        # Model Parameters
        self.window_size = window_size

        self.alpha = 0.5

        self.read_all_records()

    def read_all_records(self):
        """Aggregates data from all records into a [m,n,2] pseudoimage"""
        for r in self.record_numbers:
            self.read_single_record(r)

    def read_single_record(self, record_num):
        """Updates the records dictionary with data from a given record number. 
        The data_dir should contain the .atr, .dat, and .hea files."""
        try:
            sample = wfdb.rdsamp(self.data_dir + record_num)
            annot = wfdb.rdann(self.data_dir + record_num, 'atr')
        except ValueError:
            raise ValueError('Record not found') 

        # validation_index = sci.random.choice(range(len(annot.sample)))
        self.all_patients_data[str(record_num)] = (sample, annot)

    def get_data_obj(self, record_num):
        """Returns the data object for the given record."""
        return self.all_patients_data[str(record_num)][0]

    def get_annot_obj(self, record_num):
        """Returns the data object for the given record."""
        return self.all_patients_data[str(record_num)][1]

        
    def to_json(self, record_num, n=100, channel=0):
        """Return a sample of windows in JSON"""
        return json.dumps(self.generate_data_batch(record_num, n, channel))
