##############################################################################
# Developed by: Shobhit Agarwal and Udit Dixit
# Note: We use In-house STT Engine based on Nvidia's nemo model
# Algorithm:
# 1.) We create a LiveCapture object and traverse each packet continuously using a for loop.
# 2.) For each packet traverse each layer i.e. 'eth', 'tcp','rtp'.
# 3.) Check if 'rtp' layer is present in a packet,
# if yes then append the RTP payload by splitting on ':' to rtp_list.
# 4.) Also, we increment the no_rtp_counter by 1 if there is no RTP layer in a packet,
# else re-initialize the no_rtp_counter to 0.
# 5.) if no_rtp_counter >=50, stop capturing the packets(call is ended),
# else, for every 1000 Extras, create a raw file and decode the payload hexadecimal string to binary,
# and create the raw files at location "/rawfiles" for those payloads,
# also create a corresponding audio file at location "/wavfiles".
# 6.) Suppose, there are 1600 packets, so audio for first 1000 packets are created,
# for remaining 600, the raw file and the audio will be created once the call is ended.
##############################################################################

# Import packages
import numpy as np
import librosa
import nemo.collections.asr as nemo_asr
import os
import Global_var

# Load the pre-trained in-house STT Engine model.
asr_model = nemo_asr.models.EncDecCTCModel.restore_from('models\\QuartzNet15x5Base-En.nemo')

# Convert Audio to Transcript
def transcribe(asr_model, AUDIO_FILENAME):
    signal, sample_rate = librosa.load(AUDIO_FILENAME, sr=None)

    # calculate amplitude spectrum
    time_stride = 0.01
    hop_length = int(sample_rate * time_stride)
    n_fft = 512
    # linear scale spectrogram
    s = librosa.stft(y=signal,
                     n_fft=n_fft,
                     hop_length=hop_length)
    s_db = librosa.power_to_db(np.abs(s) ** 2, ref=np.max, top_db=100)

    # Convert our audio sample to text
    files = [AUDIO_FILENAME]
    transcript = asr_model.transcribe(paths2audio_files=files)[0]

# Create a transcription folder with the agent id logged in
def create_transcript_folder(agent):
    dirPath = os.path.dirname(__file__)
    transfilesDirPath = os.path.join(dirPath, 'transcripts', str(agent))
    if os.path.exists(transfilesDirPath):
        pass
    else:
        os.makedirs(transfilesDirPath)
    return transfilesDirPath

def stt_engine(agent, AUDIO_FILENAME):
    try:
        signal, sample_rate = librosa.load(AUDIO_FILENAME, sr=None)

        # calculate amplitude spectrum
        time_stride = 0.01
        hop_length = int(sample_rate*time_stride)
        n_fft = 512
        # linear scale spectrogram
        s = librosa.stft(y=signal,
                         n_fft=n_fft,
                         hop_length=hop_length)
        s_db = librosa.power_to_db(np.abs(s)**2, ref=np.max, top_db=100)

        # Convert our audio sample to text
        files = [AUDIO_FILENAME]
        transcript = asr_model.transcribe(paths2audio_files=files)[0]

        # TO_DO Put down any action.
        # if 'cvv' or 'c v v' or 'C V V' in transcript:
        #     print("Action to be taken")
        #     # create a file in action folder.
        #     agent_action_file = os.path.join('actions', str(agent), 'cvv.txt')
        #     os.mkdir(os.path.join('actions', str(agent)))
        #     f = open(agent_action_file, "a")
        #     f.write("CVV is found in the conversation!")
        #     f.close()
        # elif 'phone' or 'mobile' or 'phone number' or 'mobile number' in transcript:
        #     print("Action to be taken")
        #     # create a file in action folder.
        #     agent_action_file = os.path.join('actions', str(agent), 'mobilenumber.txt')
        #     os.mkdir(os.path.join('actions', str(agent)))
        #     f = open(agent_action_file, "a")
        #     f.write("Mobile number is asked in the conversation!")
        #     f.close()

        # Append the transcripts
        Global_var.transcripts.append(transcript)
        #### Create a folder with agent id name inside transcripts folder ####
        audio_file_name = os.path.split(AUDIO_FILENAME)[1]
        transcript_file_name = audio_file_name.split(".")[0]
        full_file_name = transcript_file_name + '.txt'
        trans_agent_dir = create_transcript_folder(agent)
        complete_file_path = os.path.join(trans_agent_dir, full_file_name)
        #### Create a text file containing transcripts ####
        file = open(complete_file_path, "w")
        file.write(transcript)

    except Exception as err:
        print("Error is: ", err)

if __name__ == '__main__':

    AUDIO_FILENAME = "audios/20210805165336_5007.wav"

    # process1 = multiprocessing.Process(target=load_model)
    # process2 = multiprocessing.Process(target=transcribe, args=(asr_model, AUDIO_FILENAME))
    #
    # process1.start()
    # process2.start()
    #
    # process1.join()
    # process2.join()
