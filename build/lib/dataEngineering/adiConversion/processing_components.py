# This module provides functions for preprocessing ECG signals
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample.html#scipy.signal.resample
import scipy as sci
import scipy.signal as sig

def resample_1d(signal, sampling_rate_from, sampling_rate_to):
    # signal in samples, rates in samples per second
    seconds = len(signal)/sampling_rate_from
    return sig.resample(signal, int(sci.floor(sampling_rate_to*seconds)))

def test():
    pass

if __name__ == '__main__':
    test()
