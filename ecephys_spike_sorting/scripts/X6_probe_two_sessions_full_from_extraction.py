
from helpers.batch_processing_common import processing_session
from helpers.batch_processing_config import get_from_config, get_from_kwargs
import sys
from collections import namedtuple, OrderedDict
import os

import argparse



session_name = '2053709239_532246_20200930'#test_2019-07-25_18-16-48' #Fill in with appropriate session name
session_names = [session_name]
probes_in = ['A', 'B', 'C', 'D', 'E', 'F']#get_from_config('processable_probes')#['D', 'E', 'F']
cortex_only = False

start_module = 'extract_from_npx'
end_module = 'cleanup'

#default_backup1 = os.path.join(get_from_config('network_backup', kwargs), session_name)
#default_backup2 = get_from_config('disk_backup')

modules = [
   #'copy_back_primary_raw_data',
   #'copy_back_secondary_raw_data',
   #'primary_backup_raw_data1',
   'extract_from_npx',
   'restructure_directories',
   'depth_estimation',
   'median_subtraction',
   'extend_short_data',
   'kilosort_helper',
   'noise_templates',
   'mean_waveforms',
   'quality_metrics',
   'add_noise_class_to_metrics',
   'copy_logs', 
   'final_copy_parallel',
   #'primary_backup_raw_data1',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'primary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'secondary_backup_processed_data',#combine these into one module - or allow it to kick off multiple processes without waiting?
   #'secondary_backup_raw_data',#combine these into one module - or allow it to kick off multiple processes without waiting? is it really that simple?
   'cleanup'
   #'primary_processed_lims_only',
   #'move_processed_for_phy',
]


copy_while_waiting_modules = [
    'cww_primary_backup_raw_data',
    #'cww_primary_backup_processed', # need to name these differently because both may be run
    'cww_secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
    #'cww_secondary_backup_processed'
]

final_copy_all_parallel = [
    'final_primary_backup_raw_data',
    'final_primary_backup_processed', # need to name these differently because both may be run
    'final_secondary_backup_raw_data', #these can be the same as the main modules because only needs to run once - slot module prevents from running again
    #'final_secondary_backup_processed'
]
#slot_config:{
#       2:{
#           'acq_drive':os.path.join(get_from_kwargs('network_backup', kwargs), session_name, session_name+'probeABC'),
#           'suffix': 'probeABC',
#       },
#       3:{
#           'acq_drive':os.path.join(get_from_kwargs('network_backup', kwargs), session_name, session_name+'probeDEF'),
#           'suffix': 'probeDEF',
#       },
#    }
        
sharing_backup = True
        

def make_slots(session_names):
    pxi_slots = OrderedDict()
    slot_config = get_from_config('slot_config')
    slot_params = get_from_config('slot_params')
    processing_drive = get_from_config('processing_drive')
    
    default_backup2 = get_from_config('disk_backup')
    for session_name in session_names:
        default_backup1 = os.path.join(get_from_config('network_backup'), session_name)
        for slot, params in slot_config.items():
            pxi_slots[session_name+'_'+str(slot)] = slot_params(int(slot), os.path.join(params['acq_drive'], session_name+'_'+params['suffix']), processing_drive, default_backup1, default_backup2)#S
    print(pxi_slots)
        #print(self.pxi_slots)
        #print(self.pxi_slots['3'])
    return pxi_slots


def make_probes(session_names, probes_to_process):
    probe_params = get_from_config('probe_params')
    probe_config = get_from_config('probe_config')
    probes = OrderedDict()
    default_backup2 = get_from_config('disk_backup')
    for session_name in session_names:
        default_backup1 = os.path.join(get_from_config('network_backup'), session_name)
        for probe in probes_to_process:
            probe_key = session_name+'_probe'+probe
            probe_slot_params = probe_config[probe]
            probes[probe_key]=probe_params(probe, session_name+'_'+probe_slot_params['pxi_slot'], probe_slot_params['num_in_slot'], session_name, start_module, end_module, default_backup1, default_backup2)
            print(probes[probe_key]) 
    return probes

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("session",
                  help="full path to session directory")

  parser.add_argument("session2",
                  help="full path to session directory")
  
  parser.add_argument("-p", "--probes", 
                  help= "list of probes to run (default from config)")

  parser.add_argument("-ctx", "--cortex", 
                  help= "flag to sort only cortex", action="store_true")

  parser.add_argument("-start", "--start_module", 
                  help= "which module to start from")

  parser.add_argument("-f", "--force", 
                  help= "ignore errors when checking if there is enough space to complete processing", action="store_true")

  parser.add_argument("-l", "--lower", 
                  help= "don't sort the first 15 minutes", action="store_true")

  args = parser.parse_args()

  session_names = []
  try:
    session_name = args.session
    session_names.append(session_name)
    print(session_name)
  except exception as E:
    raise(ValueError)
    print('No arguments found in sys call, using session name from py file instead')

  try:
    session_name2 = args.session2
    session_names.append(session_name2)
    print(session_name)
  except exception as E:
    raise(ValueError)
    print('No arguments found in sys call, using session name from py file instead')


  try:
    if not(args.probes is None):
      probes_in = list(args.probes)
    print(probes_in)
  except exception as E:
    raise(ValueError)
    print('No probes found in sys call, using probes from py file instead')

  cortex_only = args.cortex
  print("cortex only", cortex_only)

  force = args.force
  print("Force? ignore errors when checking if there is enough space: ", force)

  lower = args.lower
  print("Data during lowering?: don't sort the first 15 minutes ", lower)

  try:
    if not(args.start_module is None):
      start_module = args.start_module
    print("starting with module", start_module)
  except exception as E:
    raise(ValueError)
    print('No start module found in sys call, using from py file instead')




  slots = make_slots(session_names)
  probes = make_probes(session_names, probes_in)


  processor = processing_session(
    session_name, 
    probes_in, 
        cortex_only=cortex_only,
        modules=modules,
        probes= probes,
        pxi_slots= slots,
        copy_while_waiting_modules=copy_while_waiting_modules,
        final_copy_all_parallel=final_copy_all_parallel,
    start_module = start_module,
    end_module = end_module,
    processable_probes = probes_in,
    force = force,
    lower = lower
    )
  processor.start_processing()

