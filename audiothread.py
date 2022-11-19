from pickle import NONE
import threading
import time
import queue
from time import sleep
from tkinter import Canvas
from turtle import textinput

from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
from constants import Constants
import sounddevice as sd
from numpy.fft import fft, ifft
from scipy.signal import find_peaks

exitFlag = 0
frequency = 0
cPitch = 0
cNote = None
dataQueue = queue.Queue()
samplesInQueue = 0 #signifies the amount of samples that are in the processing queue
FFTResultQueue = queue.Queue()

b_startRec = False #to determine if we are recording or not

def callBack(indata, frames, time, status):
   global samplesInQueue, b_startRec
   if status:
      print(status)
   maxValue = max(indata)
   if maxValue < 0.1 and maxValue > -0.1 and b_startRec == False:
      return
   b_startRec = True
   if samplesInQueue < 2*Constants.RATE:
      dataQueue.put(indata)
      samplesInQueue += frames
   else:
      b_startRec = False



class audioThread (threading.Thread):


   def __init__(self, plotWin, canvas, plotFreq, window):
      threading.Thread.__init__(self)
      self.running = False
      self.recording = False
      self.plotWin = plotWin
      self.canvas = canvas
      self.plotFreq = plotFreq
      self.count = 0 
      self.cNote = None
      self.cPitch = None
      self.window = window
      # self.autoDetect = True
      self.chordName = ""

   def showdata(self):
      soundData = None
      global samplesInQueue
      if samplesInQueue <Constants.RATE:
         return
      soundData = None
      
      while True:
         try:
            # data = dataQueue.get_nowait()
            if dataQueue.empty():
               break
            else:
               data = dataQueue.get(False)
         except queue.Empty:
            break
         if soundData is None:
            soundData = data
         else:
            soundData = np.append(soundData, data)
      if soundData is None:
         return 
      sLength = len(soundData)
      if sLength == 0:
         return
      if self.recording == False or self.running == False:
         return
      x = range(0, sLength, 1)
      self.plotWin.clear()
      self.plotWin.plot(x, soundData)
      self.plotWin.grid()
      # self.plotWin.xlim(0, sLength)
      # self.plotWin.ylim(-1, 1)
      # self.canvas.draw()
      # self.canvas.flush_events()
      self.fftanalysis(soundData, samplesInQueue)
      samplesInQueue = 0
   
   def find_closest_note(self, pitch):
      # i = int(np.round(np.log2(pitch/Constants.CONCERT_PITCH)*12))

      # closest_note = Constants.ALL_NOTES[i%12] + str(4 + (i + 9) // 12)
      # standardFreq = Constants.STANDARDFREQ[i%12]
      # closest_pitch = Constants.CONCERT_PITCH*2**(i/12)
      if self.chordName == "":
         if pitch < 92:
            standardFreq = 82.41
            closest_note = 'E2'
         elif pitch < 128:
            standardFreq = 110
            closest_note = 'A3'
         elif pitch < 171:
            standardFreq = 146.83
            closest_note = 'D3'
         elif pitch < 221:
            standardFreq = 196
            closest_note = 'G3'
         elif pitch < 287:
            standardFreq = 246.94
            closest_note = 'B3'
         else:
            standardFreq = 329.63
            closest_note = 'E4'
      else: #elf.chordName == "E1" or self.chordName == "A" or self.chordName == "D" or self.chordName == "G" or self.chordName == "B" or self.chordName == "E2":
         if self.chordName == "E1":
            standardFreq = 82.41
            closest_note = 'E2'
         elif self.chordName == "A":
            standardFreq = 110
            closest_note = 'A3'
         elif self.chordName == "D":
            standardFreq = 146.83
            closest_note = 'D3'
         elif self.chordName == "G":
            standardFreq = 196
            closest_note = 'G3'
         elif self.chordName == "B":
            standardFreq = 246.94
            closest_note = 'B3'
         elif self.chordName == "E2":
            standardFreq = 246.94
            closest_note = 'E4'
      return closest_note, pitch, standardFreq
   
   def fftanalysis(self, x1, framerate):
      global frequency, cPitch, cNote
      X = fft(x1)
      N = len(X)
      n = np.arange(N)
      T = N/framerate
      freq = n/T
      y =np.abs(X)

      e,_= find_peaks(y, height = np.max(y)*0.2)
      idx = e[0]
      frequency = idx*framerate/N
      # print(frequency)
      # self.plotFreq.stem(freq, y, 'b', \
      #    markerfmt=" ", basefmt="-b")
      self.plotFreq.clear()
      self.plotFreq.plot(int(frequency), y[idx], 'ro', label='Fundamental Frequency - ' + "{:.2f}".format(frequency) + 'Hz')
      self.plotFreq.legend(loc='upper right')
      cNote, cPitch, standardFreq = self.find_closest_note(frequency)
      diff = (cPitch - standardFreq)/standardFreq
      
      cnp = cNote + "  " + str(round(diff*100, 2)) + '%'
      FFTResultQueue.put(cnp)
      self.window.event_generate('<<FFT_Result_Event>>')
      # self.plotFreq.xlim(0, 1000)
      # self.plotFreq.xlabel('Freq (Hz)')
      # self.plotFreq.ylabel('Amplitude')

   
   
   

   def run(self):
      self.running = True
      while self.running:
         if self.recording:
            try:
               with sd.InputStream(channels=1, callback=callBack,
                  blocksize=Constants.CHUNK,
                  samplerate=Constants.RATE):
                  while self.recording:
                     self.showdata()
                     
                     sleep(0.00005)
            except Exception as e:
               print(str(e))
         sleep(0.1)
      



