##############################################################################
# Developed by: Shobhit Agarwal and Udit Dixit
# Note: We use pyshark to capture live packets
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
import pyshark
import os
import pywav

# Create a raw folder with the agent id logged in
def create_raw_folder(agent):
    dirPath = os.path.dirname(__file__)
    rawfilesDirPath = os.path.join(dirPath, 'rawfiles', str(agent))
    if os.path.exists(rawfilesDirPath):
        pass
    else:
        os.makedirs(rawfilesDirPath)
    return rawfilesDirPath

# Creates wav files folder with the agent id logged in
def create_wav_folder(agent):
    dirPath = os.path.dirname(__file__)
    wavfilesDirPath = os.path.join(dirPath, 'wavfiles', str(agent))
    if os.path.exists(wavfilesDirPath):
        pass
    else:
        os.makedirs(wavfilesDirPath)
    return wavfilesDirPath

# Start in-house STT Engine
def capture_rtp_build_audio(agent, capture):

    # Placing this import here for reducing the time.
    from offline_asr_using_nemo import stt_engine

    rtp_list = []# Stores the RTP packets
    packetcount = 0# Counter to count the total packets
    rtp_count = 0# Counter to count only the RTP packets
    no_rtp_counter = 0# if no_rtp_counter value = 50, call is ended

    # Start Capturing the live packets
    for packet in capture.sniff_continuously():
        layer_names_list = []
        # Traverse each layer in a packet
        for layer in packet.layers:
            layer_names_list.append(layer.layer_name)
            try:
                # Check if the layer is rtp
                if layer.layer_name == 'rtp':
                    print("RTP Layer Found.")
                    # split the payload using ':' and append
                    # 56:f5:56:67-> 56 f5 56 67
                    rtp_list.append(layer.payload.split(":"))
            except Exception as err:
                print("Raised an Exception", err)

        packetcount += 1

        # Check if the rtp layer is present in packet or not?
        # if True: increase the no_rtp_counter by 1.
        # Else: Re-initiate the no_rtp_counter to 0.
        if 'rtp' not in layer_names_list:
            no_rtp_counter += 1
        else:
            no_rtp_counter = 0

        # If there are no RTP packets in continous 50 packets,
        # then it means call is disconnected.
        if no_rtp_counter >= 50:
            break

        # Create Raw files and Audio files for every 500 RTP packets.
        if len(rtp_list) != 0 and len(rtp_list) % 500 == 0:
            raw_agent_dir = create_raw_folder(agent)#function call
            raw_filename = 'rawfile' + str(rtp_count) + '.raw'
            rawfilepath = os.path.join(raw_agent_dir, raw_filename)
            # Create a rawfile and write the binary data to it.
            raw_audio = open(rawfilepath, "wb")
            for rtp_packet in rtp_list:
                payload = " ".join(rtp_packet)
                # convert hexadecimal values to bytearray
                audio = bytearray.fromhex(payload)
                # Create raw audio file.
                raw_audio.write(audio)

            # Read the raw audio files and extract the byte array data from it.
            with open(rawfilepath, "rb") as inp_f:
                data = inp_f.read()

            #### Create an audio file ####
            # function call for creating relevant agent id folder inside wavfiles folder
            wav_agent_dir = create_wav_folder(agent)
            wav_file_name = 'audio'+str(rtp_count)+'.wav'
            wavfilepath = os.path.join(wav_agent_dir, wav_file_name)
            wave_write = pywav.WavWrite(wavfilepath, 1, 8000, 8, 7)
            wave_write.write(data)
            wave_write.close()

            # Call In-house STT engine, Convert audio -> transcript
            stt_engine(agent, wavfilepath)
            rtp_list = []
            rtp_count += 1

    ############# REMAINING RTP PACKETS ##################
    raw_filename = 'rawfile' + str(rtp_count) + '.raw'
    rawfilepath = os.path.join(raw_agent_dir, raw_filename)
    raw_audio = open(rawfilepath, "wb")

    if len(rtp_list) != 0:
        for rtp_packet in rtp_list:
            payload = " ".join(rtp_packet)
            # Convert hexa code to byte array
            audio = bytearray.fromhex(payload)
            raw_audio.write(audio)
        with open(rawfilepath, "rb") as inp_f:
            data = inp_f.read()
        # Create an audio file using data
        wav_agent_dir = create_wav_folder(agent)  # function call
        wav_file_name = 'audio'+str(rtp_count)+'.wav'
        wavfilepath = os.path.join(wav_agent_dir, wav_file_name)
        # Create a audio wav file
        wave_write = pywav.WavWrite(wavfilepath, 1, 8000, 8, 7)
        wave_write.write(data)
        wave_write.close()
        # Convert audio -> transcript
        stt_engine(agent, wavfilepath)
        # return 'Done'
    else:
        print("No RTP packets left to transform into an Audio, End Call!")
    ############# REMAINING RTP PACKETS ENDS ##################

def create_live_capture_object(udp_port):
    try:
        capture = pyshark.LiveCapture(interface='Ethernet 2',
                                      output_file='final_packet_file.pcapng',
                                      decode_as={'udp.port=='+udp_port: 'rtp'})
    except Exception as err:
        print("Livecapture object couldn't be created due to {}".format(err))

    # Find the agent assigned to the particular port number, we may use mapping technique.
    agent = udp_port
    return_value = capture_rtp_build_audio(agent, capture)

    return return_value

if __name__ == '__main__':

    # d = {'5002': 4726, '5003': 4567}
    print("Start Capturing Live Packets...")
    # Represents a live capture on a network interface.
    agent = 5004
    udp_port = 4726
    # call functions.
    create_live_capture_object(agent, udp_port)
    print("100% success!")
