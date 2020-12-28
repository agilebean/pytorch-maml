#!/usr/bin/python3
###########################################################################
# Conduct experiments with MAML algorithm
###########################################################################
# import libraries
import os
import sys
import platform
import subprocess
from subprocess import DEVNULL
from subprocess import CalledProcessError
import glob
import time
import shlex
import json
import pathlib

# set interpreter
INTERPRETER=sys.executable
print("##### python interpreter: " + INTERPRETER)

BASE_DIR = os.getcwd()
print('current working directory:  ' + BASE_DIR)

DATA_FOLDER = 'data'

######################################################
# function to create sync folder for Cloud
def create_sync_folder(base_dir):

    if platform.system() == "Darwin":  # Mac
        # set MAC_SYNC_DIR
        sync_dir = os.path.expanduser(BASE_DIR + '/sync')
        if (not os.path.exists(sync_dir)):
            os.mkdir(sync_dir)
    else:
        # set CLOUD_SYNC_DIR
        sync_dir = os.path.expanduser('~/sync')

    return sync_dir

# # create sync folder for Cloud
# SYNC_DIR = create_sync_folder(BASE_DIR)
# print('SYNC_DIR: ' + SYNC_DIR)
#
######################################################

# create dictionary of parameters
PARAMETERS = {

    ## General parameters
    # dataset
    'dataset': 'omniglot',
    # output folder
    'output-folder': 'output/',
    # Number of classes per task (N in "N-way", default: 5)
    'num-ways': 5,
    # Number of training example per class (k in "k-shot", default: 5)
    'num-shots': 1,
    # Number of test example per class. If negative, same as the number of training examples
    'num-shots-test': 15,

    ## Optimization parameters
    # Number of tasks in a batch of tasks
    'batch-size': 1,
    # Number of batch of tasks per epoch
    'num-batches': 1,
    # Number of epochs of meta-training
    'num-epochs': 1,
    # Number of fast adaptation steps, ie. gradient descent updates.
    'num-steps': 1,
    # Size of the fast adaptation step, ie. learning rate in the gradient descent update
    'step-size': 0.1,
    # Learning rate for the meta-optimizer (optimization of the outer loss
    'meta-lr': 0.001,

    ## Technical parameters
    # Number of workers to use for data-loading
    'num-workers': 1,
}

def print_indexed_parameters(parameter_dict):

    index = 1
    output = ""
    param_list = list()

    for param_label in parameter_dict:
        param_list.append(param_label)
        output += ("[" + str(index) + "] " + param_label + "\n")
        index += 1
        # print(output)

    # return output
    return output, param_list



def execute_experiment(command_list):
    try:

        print(' '.join(command_list[1:]))

        tic = time.time()

        process = subprocess.Popen(command_list, shell=False, encoding='utf-8',
                                   stdin=DEVNULL, stdout=subprocess.PIPE)

        if platform.system() == "Darwin":
            while True:
                output = process.stdout.readline().strip()

                if output == '' and process.poll() is not None:  # end of output
                    break
                if output:  # print output in realtime
                    print(output)
        else:
            (output, error) = process.communicate()

        toc = time.time()
        time1 = str(round(toc - tic))

    except CalledProcessError as err:
        print("CalledProcessError: {0}".format(err))
        sys.exit(1)

    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    return time1

# MAIN
# user input: parameter to configure
parameter_index, parameter_list = print_indexed_parameters(PARAMETERS)

while True:
    try:
        PARAM_INPUT = int(input(parameter_index))

    except ValueError: # for int conversion, replaces not SyntaxError, NameError (python2)
        print("No number entered. Please select from the following list:")
        continue
    else:
        break

PARAM_SELECT = parameter_list[PARAM_INPUT-1]
print(PARAM_SELECT)


# user input: erosion kernel size
while True:
    try:
        CONFIG_INPUT = input("Which parameter configurations? (separate with spaces)> ")
        if (PARAM_SELECT == 'step-size' or PARAM_SELECT == 'meta-lr'):
            datatype = float
        else:
            datatype = int

        CONFIG_SELECT_LIST = list(map(datatype, CONFIG_INPUT.split()))

    except ValueError: # for int conversion, replaces not SyntaxError, NameError (python2)
        print("No number entered. Please select from the following list:")
        continue
    else:
        break

print('*********************************************************************')
print('You want to experiment the parameter ' + PARAM_SELECT)
print(' with configurations ' + str(CONFIG_SELECT_LIST))
print('*********************************************************************')

def create_command_list(parameter_dict, param_select, config_select):
    output = list()
    output.append(INTERPRETER)
    output.append('train.py')
    output.append(DATA_FOLDER)

    # replace parameter default value in dict by config_select value
    parameter_dict[param_select] = config_select

    for param, default_value in parameter_dict.items():
        output.append( ('--') + param )
        output.append(str(default_value))

    return output

for CONFIG_SELECT in CONFIG_SELECT_LIST:
    print(CONFIG_SELECT)
    command1 = create_command_list(PARAMETERS, PARAM_SELECT, CONFIG_SELECT)
    print(command1)
    execute_experiment(command1)

