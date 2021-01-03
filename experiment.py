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


# set interpreter
INTERPRETER=sys.executable
print("##### python interpreter: " + INTERPRETER)

BASE_DIR = os.getcwd()
print('current working directory:  ' + BASE_DIR)

if platform.system() != "Darwin":
    import torch
    print('CUDA available: ' + str(torch.cuda.is_available()))

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
    'dataset': 'miniimagenet',
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
    'num-batches': 2,
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

def execute_experiment(command_list):
    try:
        process = subprocess.Popen(
            command_list,
            shell=False,
            encoding='utf-8',
            stdout=subprocess.PIPE,
            # bufsize=0,
            # stdin=subprocess.DEVNULL,
            # universal_newlines=True,
            # stderr=subprocess.PIPE
        )
        # Poll process for new output until finished
        # Source: https://stackoverflow.com/q/37401654/7769076
        while process.poll() is None:
            nextline = process.stdout.readline()
            sys.stdout.write(nextline)
            # sys.stdout.flush()

    except CalledProcessError as err:
        print("CalledProcessError: {0}".format(err))
        sys.exit(1)

    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

# MAIN
# user input: parameter to configure
parameter_index, parameter_list = print_indexed_parameters(PARAMETERS)

while True:
    # skim parameter input by ENTER
    PARAM_INPUT = input(parameter_index)
    if PARAM_INPUT == "":
      break
    # check if number
    try:
      PARAM_INPUT = int(PARAM_INPUT)
    except ValueError: # for int conversion, replaces not SyntaxError, NameError (python2)
        print("No number entered. Please select from the following list:")
        continue
    else:
        break

if (PARAM_INPUT is ""):
    CONFIG_SELECT_LIST = [1]
    PARAM_SELECT = 'num-epochs'
else:
  PARAM_SELECT = parameter_list[PARAM_INPUT-1]
  print(PARAM_SELECT)

  # user input: parameter configuration
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


for CONFIG_SELECT in CONFIG_SELECT_LIST:
    if (PARAM_INPUT is ""):
        print("Training default configuration")
    else:
        print(CONFIG_SELECT)

    tic = time.time()
    command1 = create_command_list(PARAMETERS, PARAM_SELECT, CONFIG_SELECT)
    print(' '.join(command1[1:]))
    execute_experiment(command1)
    toc = time.time()
    time1 = round(toc - tic)
    print("Total time elapsed: " + str(time1) + " seconds")
