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
from flask import Flask, request, jsonify
from pydub import AudioSegment
from scipy.signal import butter, lfilter, freqz

app = Flask(__name__)
recordPath = os.path.join('/', 'seongdalAudio', 'recorded')
originPath = os.path.join('/', 'seongdalAudio', 'original')

def butter_bandpass(lowcut, highcut, fs, order = 5):

	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low, high], btype='band')

	return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order = 5):

	b, a = butter_bandpass(lowcut, highcut, fs, order=order)
	y = lfilter(b, a, data)

	return y

def denoise(y, lowcut, highcut, sr):

	y = butter_bandpass_filter(y, lowcut, highcut, sr, order = 7)

	return y

def speed_change(sound, speed=1.0):
	# Manually override the frame_rate. This tells the computer how many
	# samples to play per second
	sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
		"frame_rate": int(sound.frame_rate * speed)
	})

	# convert the sound with altered frame rate to a standard frame rate
	# so that regular playback programs will work right. They often only
	# know how to play audio at standard frame rate (like 44.1k)
	return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def slowAudio(y):

	return librosa.effects.time_stretch(y, 0.1822)

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
		message = "low!"

	elif ratio < -threshold:

		code = 2
		message = "high!"

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


def printEnv(env):

	result = env
	threshold = 25

	code = 0
	message = "perfect!"

	if result >threshold:

		code = 1
		print ("You should care about Envelope!")

	else:
		print("Your Envelope is Good!")
	return code

def getAudioCutByOnset(file1, file2):

    pre_emphasis = 0.97
    y_t, sr_t = librosa.load(file1,offset= 0.025)
    y, sr = librosa.load(file2,offset= 0.025)

    print('target file : ', file1, ' samplingRate : ', sr_t)
    print('input file : ', file2, ' samplingRate : ', sr_t)

    y_t, index = librosa.effects.trim(y_t)
    y, index = librosa.effects.trim(y)

    emphasized_signal_t = np.append(y_t[0], y_t[1:] - pre_emphasis * y_t[:-1])
    emphasized_signal = np.append(y[0], y[1:] - pre_emphasis * y[:-1])

    y_t = librosa.util.normalize(emphasized_signal_t)
    y = librosa.util.normalize(emphasized_signal)
    y_t = denoise(y_t, 80, 3400, sr_t)
    y = denoise(y, 80, 3400, sr)

    onsetFrame_t = librosa.onset.onset_detect(y = y_t, sr = sr_t)
    onsetEnvelope_t = librosa.onset.onset_strength(y_t, sr = sr_t)
    onsetEnvelope_t = onsetEnvelope_t / onsetEnvelope_t.max()
    onsetTime_t = librosa.frames_to_time(np.arange(len(onsetEnvelope_t)), sr = sr_t)

    onsetFrame = librosa.onset.onset_detect(y = y, sr = sr)
    onsetEnvelope = librosa.onset.onset_strength(y, sr = sr)
    onsetEnvelope = onsetEnvelope / onsetEnvelope.max()
    onsetTime = librosa.frames_to_time(np.arange(len(onsetEnvelope)), sr = sr)

    #todo
    selected_t = [onsetTime_t[onsetFrame_t[idx]] for idx in range(len(onsetFrame_t)) if onsetEnvelope_t[onsetFrame_t[idx]] > 0.3]
    selected = [onsetTime[onsetFrame[idx]] for idx in range(len(onsetFrame)) if onsetEnvelope[onsetFrame[idx]] > 0.3]

    start_t = selected_t[0] -0.05
    end_t = selected_t[-1] + 0.3
    startIdx_t = int(start_t * sr_t)
    endIdx_t = int(end_t * sr_t)
    howlong_t = end_t - start_t

    if int(start_t * sr_t) < 0:

        startIdx_t = 0

    if int(end_t * sr_t) > len(y_t):

        endIdx_t = len(y_t)

    #these are onsets

    min1 = 0
    min2 = 0
    temp_mfcc_distance = 100
    #print("selected", selected)
    for idx1 in range(len(selected)):
        for idx2 in range(idx1+1,len(selected)):
            start = selected[idx1] - 0.05
            end = selected[idx2] + 0.3

            if end - start < howlong_t/2:
                continue

            startIdx = int(start * sr)
            endIdx = int(end * sr)

            if int(start * sr) < 0:
                startIdx = 0
            if int(end * sr) > len(y):
                endIdx = len(y)

            mfcc_t = showMFCC(y_t[startIdx_t:endIdx_t], sr_t)
            mfcc = showMFCC(y[startIdx:endIdx], sr)
            dis = compareMFCC(mfcc_t, mfcc)

            if temp_mfcc_distance > dis:
                min1 = idx1
                min2 = idx2
                temp_mfcc_distance = dis
                #print(start, end)
                #print("distance : ",dis)



    start = selected[min1] -0.05
    end = selected[min2] + 0.3
    startIdx = int(start * sr)
    endIdx = int(end * sr)

    if int(start * sr) < 0:

        startIdx = 0

    if int(end * sr) > len(y):

        endIdx = len(y)

    return start_t, end_t, y_t[startIdx_t:endIdx_t], sr_t, start, end, y[startIdx:endIdx], sr

def getOnset(wave, samplingRate):

	onsetFrame = librosa.onset.onset_detect(y = wave, sr = samplingRate)
	onsetEnvelope = librosa.onset.onset_strength(wave, sr = samplingRate)
	onsetEnvelope = onsetEnvelope / onsetEnvelope.max()
	onsetTime = librosa.frames_to_time(np.arange(len(onsetEnvelope)), sr = samplingRate)

	spectro =  librosa.stft(wave)
	selected = [onsetTime[onsetFrame[idx]] for idx in range(len(onsetFrame)) if onsetEnvelope[onsetFrame[idx]] > 0.4]
	print(selected)
'''
	plt.figure()
	ax = plt.subplot(2, 1, 1)
	librosa.display.specshow(librosa.amplitude_to_db(spectro, ref = np.max), x_axis = 'time', y_axis = 'log')
	plt.subplot(2, 1, 2, sharex = ax)
	plt.vlines(selected, 0, 1, color = 'blue', alpha = 0.9, linestyle = '--')
	plt.show()
'''
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

#	for idx in range(0, delta + 1):

#		distance.append(np.linalg.norm((short - long[:,idx:idx + short.shape[1]])/short.shape[1])) #short shape


	f = interp2d(x = np.arange(short.shape[1]), y = np.arange(short.shape[0]), z = short, kind = 'cubic')

	interp = np.array([[f(x * short.shape[1] / long.shape[1], y * short.shape[0] / long.shape[0])
			   for x in range(long.shape[1])] for y in range(long.shape[0])]).reshape(long.shape[0], long.shape[1])

	distance.append(np.linalg.norm((interp - long)/mfcc1.shape[1]))#interpolation shape. interpol shape

	return min(distance)

def testSync(target_audio_path, input_audio_path):

	result = dict()

	sound = AudioSegment.from_file(input_audio_path)
	slow_sound = speed_change(sound,0.184)
	new_path = input_audio_path[:-4]+"_slow.wav"

	slow_sound.export(new_path,format="wav")

	#Print
	#print("Target file: " + target_audio_path)
	#print("Input file : " + new_path)
	result['target'] = target_audio_path
	result['input'] = new_path

	# Cut By Onset
	start_t, end_t, y_t, sr_t, start, end, y, sr = getAudioCutByOnset(target_audio_path,new_path)


	# slow audio
#    y = slowAudio(y)
#    librosa.output.write_wav(input_audio_path[:-4] + '_slow.wav', y, sr)

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
	result_env /= (len(y_t)/sr_t)
	code_env = printEnv(result_env)
	print("env : ", result_env)
	result['env'] = result_env
	result['env_code'] = code_env

	#MFCC Analysis
	mfcc_t = showMFCC(y_t, sr_t)
	#mfcc_t -= (np.mean(mfcc_t, axis=0) + 1e-8)
	mfcc = showMFCC(y, sr)
	#mfcc -= (np.mean(mfcc, axis=0) + 1e-8)

	result_mfcc = compareMFCC(mfcc_t, mfcc)
	result['mfcc'] = result_mfcc
	print(result_mfcc)

	#regression
#	result['score'] = np.clip(-16 * np.log(result_mfcc) + 105, 0, 100)
	if result_mfcc < 15:
		result['score'] = np.clip((-2.5375 * result_mfcc + 110), 0, 100)
	else:
		result['score'] = np.clip((-4.7958 * result_mfcc + 143),0,100)

	if result['pitch_code'] != 0:
		result['score'] -= 8
	if result['length_code'] != 0:
		result['score'] -= 8
	if result['env_code'] != 0:
		result['score'] -= 8

	result['score'] = np.clip(result['score'],0,100)

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

			#resultDict = {'status' : 1,
			#			'pitch' : 0,
			#			'length' : 0,
			#			'envelope' : 0,
			#			'score' : 92}

		except Exception as e:

			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print('[error] ' + str(e))
			print('[error] line ' + str(exc_tb.tb_lineno))
			resultDict = {'status' : 0}

		return jsonify(resultDict)

"""
@app.route('/restore', methods = ['GET'])
def restoreAudio():

	if request.method == 'GET':

		try:

			recorded = request.args.get('fn')
			original = request.args.get('origin')

			# 성공하면 status 1, 실패 하면 status 0
			# 오디오 길이 늘여서 저장만

			resultDict = {'status' : 1}

	return jsonify(resultDict)
"""

if __name__ == '__main__':

	app.run(host = '0.0.0.0', port = 808)
