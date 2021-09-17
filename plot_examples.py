#!/usr/bin/env python3

from collections import namedtuple
from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np


class Signal(namedtuple('_Signal', 'data rate')):
    def seconds(self) -> float:
        return len(self.data) / self.rate


def read_wav(path) -> Signal:
    rate, data = wavfile.read(path)
    return Signal(data, rate)


def shift_frequency(sig, fshift, fs):
    '''Shift signal in frequency domain by fshift (can be negative), given sampling fs.'''
    txx = np.arange(0, len(sig))
    sig_shift = np.exp(1.0j*2*np.pi*fshift*txx/fs)
    return sig * sig_shift


def chop(sig, samples_per_chunk):
    k1 = np.arange(0, len(sig), samples_per_chunk)
    k2 = np.arange(0, len(sig), samples_per_chunk)
    return [sig[s:e] for s, e in zip(k1[0:-1], k2[1:])]


def plot_spectro(data, rate, fpath=None, tshift=0):
    f, t, sxx = signal.spectrogram(data, rate)
    t = t + tshift
    #sxx = np.log(sxx)
    fig = plt.figure()
    plt.pcolormesh(t, f, sxx, shading='nearest', cmap='binary')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    if fpath == None:
        plt.show()
    else:
        plt.savefig(fpath)
        plt.close()


def plot_fft(data, rate, fpath=None):
    yf = fft(data)
    t = 1. / rate
    xf = fftfreq(data.size, t)
    yplot = np.abs(yf)/data.size
    h = int(len(xf)/2)
    fig = plt.figure()
    plt.grid()
    plt.xlabel('Frequency [Hz]')
    plt.plot(xf, yplot)
    if fpath != None:
        plt.savefig(fpath)
        plt.close()


def main():
    fname = 'zoom_RASMXJ_20khz_2share.wav'
    s = read_wav(fname)
    print("file {} has {} seconds".format(fname, s.seconds()))

    sig, rate = s.data, s.rate
    sos = signal.butter(4, 15_000, 'hp', fs=rate, output='sos')
    sig =  signal.sosfilt(sos, sig)
    sig = signal.hilbert(sig)
    plot_fft(sig, rate, 'figs/fft_original.png')
    sig = shift_frequency(sig, -19_000, fs=rate)
    dk = 15
    sig, rate = signal.decimate(sig, dk), int(rate/dk)

    plot_fft(sig, rate, 'figs/fft_decimated.png')
    chunk_size = rate*5
    for i, subsig in enumerate(chop(sig, chunk_size)):
        fpath='figs/spectro_{}.png'.format(i+1)
        print(fpath)
        plot_spectro(np.real(subsig), rate, fpath=fpath, tshift=(i*chunk_size)/rate)

main()
