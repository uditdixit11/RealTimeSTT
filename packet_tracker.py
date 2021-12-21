##############################################################################
# Developed by: Shobhit Agarwal and Udit Dixit
# Note: We use pyshark, Download and Install wireshark
# Algorithm:
# 1.) We'll create a capture object using pyshark
# 2.) Next, We'll check each packets during the runtime
# 3.) Inside each packet, check the layers
# if layer is udp, extract the active port.
# 4.) Once, we have the active port, map it to the agent number
# 5.) create a blank text file, in Agent_login_checker folder with the agent id.
# Process is created and create_live_capture_object is called.
# 6.) If new agent is logged in, then new text file with the agent id is created and new process is created.
# New process is created for create_live_capture_object from live_stream module.
# Please Note: The main purpose of using multiprocess is for the multiple calls at once,
# since we'll getting multiple calls at once and their packets needs to be isolated from another call
# Also, each call's packet will be captured on multiple cores.
##############################################################################

# Import Packages
import pyshark
import Global_var
from packet_capture import create_live_capture_object
import os, glob
import multiprocessing

if __name__ == '__main__':

    #Create a pyshark Live Capture object to work on Real time packets.
    maincapture = pyshark.LiveCapture(interface='Ethernet 2')
    print("Start tracking the Network Packets")
    agent_checker = "Agent_login_checker"# Checks the agent is logged in or not
    processes_list = [] # Stores the object of process and calls it using multiprocessing

    # sniff continously returns generator object
    for packet in maincapture.sniff_continuously():
        layers_name = []# Stores the layer name
        layers_object = []# Stores the layer object
        # Traverse each layer in a packet
        for layer in packet.layers:
            layers_name.append(layer.layer_name)
            layers_object.append(layer)

        # Zip layer_name and layer_object e.g. [1,2,3] and [100, 200, 300] => [[1,100], [2, 200], [3, 300]]
        for name, layer in zip(layers_name, layers_object):
            # Check if the layer name is 'udp'
            if name == 'udp':
                # Find the active destination port
                active_port = layer.dstport
                # Check from the database if the agent port number is present
                # Right now the database is a simple list.
                if active_port in Global_var.agents_ports:
                    # Extract the list of Files present inside Agent_login_checker folder
                    file_list = glob.glob(os.path.join(agent_checker, "*.*"))
                    agents_logged_in = [os.path.basename(filename).split('.')[0] for filename in file_list]
                    # If the active port is already activated, do nothing
                    if active_port in agents_logged_in:
                        # Do nothing
                        pass
                    # Else, if the port is activated first time, do the following
                    else:
                        # Create a text file name inside Agent_login_checker folder
                        # To track which agent is logged in and which agent is not.
                        file_name = active_port + ".txt"
                        full_file_path = os.path.join(agent_checker, file_name)
                        with open(full_file_path, "w") as fp:
                            print("File Created")
                        # Initiate the multiprocess Process for create_live_capture_object
                        process_i = multiprocessing.Process(target=create_live_capture_object,args=(active_port,))
                        # Append each process object in a list for each different call.
                        processes_list.append(process_i)
                        # Start the process run.
                        process_i.start()
            else:
                # Do nothing
                pass

    # run multiple calls in parallel using below for loop.
    for proc in processes_list:
        proc.join()
