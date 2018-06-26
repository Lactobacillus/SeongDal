import os
import sys
from os import listdir
from os.path import isfile, join
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from PIL import Image
import librosa
import librosa.display
import IPython.display as ipd
from fastdtw import fastdtw
from scipy.interpolate import interp2d
from flask import Flask, request

app = Flask(__name__)
recordPath = os.path.join('/', 'seongdalAudio', 'recorded')
originPath = os.path.join('/', 'seongdalAudio', 'original')

#input : y_target, sr_target, y_input, sr_input
def analyzePitch(y_t, sr_t, y_i, sr_i):

    pitches_t, magnitudes_t = librosa.piptrack(y=y_t, sr=sr_t)
    pitches_i, magnitudes_i = librosa.piptrack(y=y_i, sr=sr_i)

#    print(magnitudes_i[magnitudes_i>0])
#    print(np.mean(magnitudes_i[magnitudes_i>0]))
    mean_t = np.mean(pitches_t.T[magnitudes_t.T>0.1])
    mean_i = np.mean(pitches_i.T[magnitudes_i.T>0.1])

    ratio = (mean_t - mean_i) / mean_t * 100

    print("Mean of pitches(t,i) : ", mean_t, mean_i)
    print("Ratio : ", ratio)

    return ratio

#prefix : "of front part" , "of middle part", "of back part"
def printPitch(ratio,prefix = "of entire speech"):

    threshold = 5

    code = 0
    message = "perfect!"

    if ratio > threshold:

        code = 1
        message = "high!"

    elif ratio < -threshold:

        code = 2
        message = "low!"

#    elif ratio > threshold1:

#        code = 3
#        message = "little high!"

#    elif ratio < -threshold1:

#        code = 4
#        message = "little low!"

    print ("The pitch " + prefix + " is " + message)

    return code

def analyzeLength(y_t, sr_t, y, sr):

    print("target : ", len(y_t)/sr_t,"sec")
    print("input : ", len(y)/sr,"sec")

    diff = len(y_t)/sr_t - len(y)/sr
    ratio = diff / (len(y_t)/sr_t) * 100

    return ratio

def printLength(ratio):

#    threshold1 = 3
    threshold2 = 10

    code = 0
    message = "perfect!"

    if ratio > threshold2:

        code = 1
        message = "fast!"

    elif ratio < -threshold2:

        code = 2
        message = " slow!"

#    elif ratio > threshold1:

#        code = 3
#        message = "little fast!"

#    elif ratio < -threshold1:

#        code = 4
#        message = "little slow!"

    print ("The speed is " + message)

    return code


def printEnv(env, y, sr):

    result = env / (len(y)/sr)
    threshold = 35

    code = 0
    message = "perfect!"

    if result <threshold:

        code = 1
        print ("You should care about Envelope!")

    else:
        print("Your Envelope is Good!")
    return code

def getAudioCutByOnset(file):

    pre_emphasis = 0.97
    wave, samplingRate = librosa.load(file,offset= 0.025)
    emphasized_signal = np.append(wave[0], wave[1:] - pre_emphasis * wave[:-1])
    wave = librosa.util.normalize(emphasized_signal)

    onsetFrame = librosa.onset.onset_detect(y = wave, sr = samplingRate)
    onsetEnvelope = librosa.onset.onset_strength(wave, sr = samplingRate)
    onsetEnvelope = onsetEnvelope / onsetEnvelope.max()
    onsetTime = librosa.frames_to_time(np.arange(len(onsetEnvelope)), sr = samplingRate)

    selected = [onsetTime[onsetFrame[idx]] for idx in range(len(onsetFrame)) if onsetEnvelope[onsetFrame[idx]] > 0.3]
    start = selected[0] -0.05
    end = selected[-1] + 0.5
    startIdx = int(start * samplingRate)
    endIdx = int(end * samplingRate)

    if int(start * samplingRate) < 0:

        startIdx = 0

    if int(end * samplingRate) > len(wave):

        endIdx = len(wave)

    return start, end, wave[startIdx:endIdx], samplingRate

def getOnset(wave, samplingRate):

    onsetFrame = librosa.onset.onset_detect(y = wave, sr = samplingRate)
    onsetEnvelope = librosa.onset.onset_strength(wave, sr = samplingRate)
    onsetEnvelope = onsetEnvelope / onsetEnvelope.max()
    onsetTime = librosa.frames_to_time(np.arange(len(onsetEnvelope)), sr = samplingRate)

    spectro =  librosa.stft(wave)
    selected = [onsetTime[onsetFrame[idx]] for idx in range(len(onsetFrame)) if onsetEnvelope[onsetFrame[idx]] > 0.4]
    print(selected)

    plt.figure()
    ax = plt.subplot(2, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(spectro, ref = np.max), x_axis = 'time', y_axis = 'log')
    plt.subplot(2, 1, 2, sharex = ax)
    plt.vlines(selected, 0, 1, color = 'blue', alpha = 0.9, linestyle = '--')
    plt.show()

def showWave(wave, samplingRate):

    plt.figure(figsize = (10, 4))
    librosa.display.waveplot(wave, sr = samplingRate)
    plt.show()

def showSTFT(wave, samplingRate):

    plt.figure(figsize = (6, 4))
    spectro =  librosa.stft(wave)
    #print(spectro.shape)

    librosa.display.specshow(librosa.amplitude_to_db(spectro, ref = np.max), x_axis = 'time', y_axis = 'log')
    plt.show()

    return spectro, samplingRate

def showEnvelope(wave, samplingRate):

    envelope = librosa.onset.onset_strength(wave, sr = samplingRate)
    time = librosa.frames_to_time(np.arange(len(envelope)), sr = samplingRate)
    spectro =  librosa.stft(wave)
    #print(envelope.shape)
    '''
    plt.figure()
    ax = plt.subplot(2, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(spectro, ref = np.max), x_axis = 'time', y_axis = 'log')
    plt.subplot(2, 1, 2, sharex = ax)
    plt.plot(time, envelope, c = 'b')
    plt.show()
        '''
    return envelope, time

def showMFCC(wave, samplingRate):

    mfcc = librosa.feature.mfcc(y = wave, sr = samplingRate, n_mfcc = 13)
    #print(mfcc.shape)
    '''
    plt.figure(figsize = (10, 4))
    librosa.display.specshow(mfcc, x_axis = 'time')
    plt.colorbar()
    plt.tight_layout()
    plt.show()
    '''
    return mfcc

def compareMFCC(mfcc1, mfcc2):

    distance = list()

    if mfcc1.shape[1] > mfcc2.shape[1]:

        long = mfcc1
        short = mfcc2

    else:

        long = mfcc2
        short = mfcc1

    delta = long.shape[1] - short.shape[1]

    for idx in range(0, delta + 1):

        distance.append(np.linalg.norm((short - long[:,idx:idx + short.shape[1]])/short.shape[1])) #short shape


    f = interp2d(x = np.arange(short.shape[1]), y = np.arange(short.shape[0]), z = short, kind = 'cubic')

    interp = np.array([[f(x * short.shape[1] / long.shape[1], y * short.shape[0] / long.shape[0])
               for x in range(long.shape[1])] for y in range(long.shape[0])]).reshape(long.shape[0], long.shape[1])

    distance.append(np.linalg.norm((interp - long)/interp.shape[1]))#interpolation shape. interpol shape

    return min(distance) #TO

def testSync(target_audio_path, input_audio_path):

    result = dict()

    #Print
    print("Target file: " + target_audio_path)
    print("Input file : " + input_audio_path)
    result['target'] = target_audio_path
    result['input'] = input_audio_path

    # Cut By Onset
    start_t, end_t, y_t, sr_t = getAudioCutByOnset(target_audio_path)
    start, end, y, sr = getAudioCutByOnset(input_audio_path)
    result['start_t'] = start_t
    result['end_t'] = end_t
    result['y_t'] = y_t
    result['sr_t'] = sr_t
    result['start'] = start
    result['end'] = end
    result['sr'] = sr
    result['y'] = y

    #Pitch Analysis
    result_pitch = analyzePitch(y_t, sr_t, y, sr)
    code_pitch = printPitch(result_pitch)
    result['pitch'] = result_pitch
    result['pitch_code'] = code_pitch

    #Speed Analysis
    result_length = analyzeLength(y_t,sr_t, y, sr)
    code_length = printLength(result_length)
    print(result_length)
    result['length'] = result_length
    result['length_code'] = code_length

    #Power Analysis
    env_t, time_t = showEnvelope(y_t, sr_t)
    env, time = showEnvelope(y, sr)


    result_env, _  = fastdtw(env_t, env, dist = sp.spatial.distance.euclidean)
    code_env = printEnv(result_env, y, sr)
    print("env : ", result_env)
    result['env'] = result_env
    result['env_code'] = code_env

    #MFCC Analysis
    mfcc_t = showMFCC(y_t, sr_t)
    mfcc_t -= (np.mean(mfcc_t, axis=0) + 1e-8)
    mfcc = showMFCC(y, sr)
    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)

    result_mfcc = compareMFCC(mfcc_t, mfcc)
    result['mfcc'] = result_mfcc
    print(result_mfcc)

    #regression
    result['score'] = np.clip(-16 * np.log(result_mfcc) + 120, 0, 100)

    return result
    
@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
def index():

	return 'server is working!!'

@app.route('/score', methods = ['GET'])
def getScore():

	if request.method == 'GET':

		try:

			recorded = request.args.get('fn')
			original = request.args.get('origin')

			rPath = os.path.join(recordPath, recorded + '.wav')
			oPath = os.path.join(originPath, original + '.wav')

			result = testSync(oPath, rPath)
			resultDict = {'status' : 1,
						'pitch' : int(result['pitch_code']),
						'length' : int(result['length_code']),
						'envelope' : int(result['env_code']),
						'score' : int(result['score'])}

		except:

			resultDict = {'status' : 0}

		return resultDict

if __name__ == '__main__':

	app.run(host = '127.0.0.1', port = 808)
