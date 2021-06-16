#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

from qtmodern import styles, windows
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import *

import subprocess
import shutil
import os
import time
#import psutil
from collections import namedtuple, OrderedDict
#from pprint import pprint
#from recordclass import recordclass
import datetime
import logging
from qtpy import QtGui, QtCore
#import multiprocessing

logging.basicConfig(level = logging.DEBUG)


#from cleanup.check_data_processing import postprocessing, check_data_processing
#from create_input_json import createInputJson
from zro import RemoteObject, Proxy

class RemoteInterface(RemoteObject):
	def __init__(self, rep_port, parent):
		super(RemoteInterface, self).__init__(rep_port=rep_port)
		print('Opening Remote Interface on port: '+ str(rep_port))
		self.parent = parent

	def set_session_name(self, session_name):
		print('Recieved new session from remote command')
		session_name = self.parent.session_entry.text()
		print('Cleaning up phy from old session name: ' +session_name+ ' first')
		self.parent.cleanup_phy(session_name)
		print('Setting session name')
		self.parent.set_session( session_name)
		return True

	def cleanup_daqs(self):
		print('Attempting to cleanup daqs from remote command')
		self.parent.cleanup_daqs()
		return

	def create_bat_files(self, session_name):
		print('Attempting to cleanup daqs from remote command')
		self.parent.open_phy( session_name)
		return

	def test_matlab(self, session_name):
		print('Attempting to test matlab from remote command')
		self.parent.test_matlab(session_name)
		return True

	def check_matlab_test(self, session_name):
		print('Attempting to check matlab test from remote command')
		return self.parent.matlab_check

	def ping(self):
		print("its alive")       


class Processing_Agent(QWidget):
	def __init__(self):
		super(Processing_Agent, self).__init__()

		#logging.basicConfig(level=logging.DEBUG,
		#        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		#self.config = mpeconfig.source_configuration('neuropixels')

		self.matlab_check = False
		self.session_name = None

		self.interface = RemoteInterface(rep_port=1212, parent=self)
		print('Starting Remote Interface')

		self.interfaceTimer = QtCore.QTimer()
		self.interfaceTimer.timeout.connect(self._check_sock)
		self.interfaceTimer.start(100)

		self.smallFont = QtGui.QFont()
		self.smallFont.setPointSize(8)
		self.smallFont.setBold(False)

		self.bigFont = QtGui.QFont()
		self.bigFont.setPointSize(12)
		self.bigFont.setBold(False)

		self.vLayout = QVBoxLayout()

		self.header = QLabel()
		self.header.setFont(self.bigFont)
		self.header.setText('NPX Processing Assistant')
		self.header.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.vLayout.addWidget(self.header)

		self.processing_layout = QGridLayout()

		self.sessoin_label = QLabel()
		self.sessoin_label = QLabel()
		self.sessoin_label.setFont(self.smallFont)
		self.sessoin_label.setText('Full session name:')
		self.sessoin_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.session_entry = QLineEdit()
		self.session_entry.setFont(self.smallFont)
		self.processing_layout.addWidget(self.sessoin_label, 1, 0)
		self.processing_layout.addWidget(self.session_entry, 1, 1)

		self.vLayout.addLayout(self.processing_layout)

		self.processButton = QPushButton("Open Phy")
		self.processButton.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.processButton.clicked.connect(self.process_button_press)
		self.vLayout.addWidget(self.processButton)

		self.testMatlabButton = QPushButton("Test Matlab")
		self.testMatlabButton.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.testMatlabButton.clicked.connect(self.test_matlab_buttonpress)
		self.vLayout.addWidget(self.testMatlabButton)

		self.cleanupButton = QPushButton("Cleanup acquisition drives")
		self.cleanupButton.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.cleanupButton.clicked.connect(self.cleanup_buttonpress)
		self.vLayout.addWidget(self.cleanupButton)

		self.cleanupButton2 = QPushButton("Cleanup phy")
		self.cleanupButton2.setStyleSheet("color: #333; border: 2px solid #555; border-radius: 11px; padding: 5px;background: qradialgradient(cx: 0.3, cy: -0.4,fx: 0.3, fy: -0.4,radius: 1.35, stop: 0 #fff, stop: 1 #388E3C);min-width: 80px;font-size:15px;")
		self.cleanupButton2.clicked.connect(self.cleanup_phy_buttonpress)
		self.vLayout.addWidget(self.cleanupButton2)

		###############################################################

		self.setLayout(self.vLayout)

	def set_session(self, session_name):
		self.session_entry.setText(session_name)

	def process_button_press(self):
		try:
			self.cleanup_phy(self.session_name)
		except Exception as E:
			logging.warning('Failed to cleanup last session')
		self.session_name = self.session_entry.text()
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to open phy with session name: "+self.session_name+"?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.open_phy(self.session_name)
		else:
			pass


	def test_matlab_buttonpress(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to test MATLAB?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.test_matlab(session_name)
		else:
			pass
		
	def cleanup_buttonpress(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want cleanup the acquisition drives?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.cleanup_daqs(session_name)
		else:
			pass

	def cleanup_phy_buttonpress(self):
		session_name = self.session_entry.text()
		reply = QMessageBox.question(self, 'Message', "Are you sure you want cleanup phy: "+session_name+"?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.cleanup_phy(session_name)
		else:
			pass

	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def _check_sock(self):
		self.interface._check_rep()

	def cleanup_phy(self, session_name):
		npx_directories = make_constants(session_name)
		bat_path, cleanup_path = self.make_batch_files(npx_directories,session_name)
		try:
			subprocess.check_call(cleanup_path)
		except Exception as E:
			logging.warning('Cleanup Batch file failed', exc_info = True)

	def open_phy(self, session_name):
		npx_directories = make_constants(session_name)
		bat_path, cleanup_path = self.make_batch_files(npx_directories,session_name)
		try:
			subprocess.check_call(bat_path)
		except Exception as E:
			logging.warning('Open phy Batch file failed', exc_info = True)


	def make_phy_paths(self, session):
		now = datetime.datetime.now()
		bat_path = os.path.join(r"C:\Users\svc_neuropix\Desktop", 'start_phy'+session+".bat")
		cleanup_path = os.path.join(r"C:\Users\svc_neuropix\Desktop", 'cleanup_phy'+session+".bat")
		return bat_path, cleanup_path

	def make_batch_files(self, npx_directories, session):
		relpaths, data_files = make_files()
		bat_path, cleanup_path = self.make_phy_paths(session)
		bat_string = ""#"call activate phy\n"
		#bat_string_2 = "pause"
		tsv_list = ['metrics.csv', 'waveform_metrics.csv', 'cluster_Amplitude.tsv', 'cluster_ContamPct.tsv', 'cluster_KSLabel.tsv']
		cleanup_phy_string = ""
		for npx_directory, params in npx_directories.items():
			basepath,session = os.path.split(npx_directory)
			probe_letter = session.split('_')[3][-1]
			sorted_dir = os.path.join(basepath,session, relpaths['spikes'])
			metrics_dir = os.path.join(sorted_dir, 'tsv_files')
			#params.backup1
			probe_depth_path = os.path.join(basepath, session, 'probe_depth_'+probe_letter+'.png')
			move_list = []
			move_back_list = []
			for filename in tsv_list:
					metrics_file_1 = os.path.join(sorted_dir, filename)
					metrics_file_2 = os.path.join(metrics_dir, filename)
					move_list.extend(['move ',metrics_file_1," ",metrics_file_2,'\n'])
					move_back_list.extend(['move ',metrics_file_2," ",metrics_file_1,'\n'])
			add_phy = [
				probe_depth_path,'\n',
				'if not exist ',metrics_dir,' mkdir ', metrics_dir, '\n'
			]
			add_phy.extend(move_list)
			add_phy.extend([
				'start cmd /c ^\n',
				'cd /d ',sorted_dir,' ^& ^\n',
				"call activate phy ^& ^\n",
				'phy template-gui params.py ^& ^\n',
				'echo start pings\n',
				'PING localhost -n 6 >NUL \n',#Wait until phy has time to open
				'echo pings complete\n'
			])
			add_phy.extend(move_list)
			add_phy.append('echo moved complete\n')

			cleanup_phy = []
			cleanup_phy.extend(move_back_list)
			cleanup_phy.extend([
				'move ',metrics_file_2," ",metrics_file_1,'\n',
				'rmdir /s /q ',metrics_dir,' \n',
				'rmdir /s /q ',os.path.join(sorted_dir, ".phy"),' \n',
				'del ',os.path.join(sorted_dir,'phy.log'),' \n'
			])

			add_phy_string = "".join(add_phy)
			add_cleanup_phy_string = "".join(cleanup_phy)
			
			bat_string = bat_string+add_phy_string
			cleanup_phy_string = cleanup_phy_string + add_cleanup_phy_string
		
		#bat_string = bat_string_1+bat_string_2
		cleanup_final = [
				'del ',bat_path,' \n',
				'del "%~f0"'
				]
		cleanup_final_string = "".join(cleanup_final)
		cleanup_string = cleanup_phy_string + cleanup_final_string

		with open(bat_path,"w+") as f:
			f.write(bat_string)
		with open(cleanup_path,"w+") as f:
			f.write(cleanup_string)

		with open(bat_path,"w+") as f:
			f.write(bat_string)
		with open(cleanup_path,"w+") as f:
			f.write(cleanup_string)

		return bat_path, cleanup_path

	def cleanup_daqs(self):
		session_name = self.session_entry.text()
		npx_directories = make_constants(session_name)
		for npx_dir in npx_directories:
			drive, tail = os.path.splitdrive(npx_dir)
			for data_dir in os.listdir(drive):
				try:
					pass
					#query ecephys lims page for the dir
					#if local dir matches lims dir:
					#once we we have a working example try using filecmp.dircmp to check if they are actually the same
						#^can test this now
					#otherwise do something with os.walk
					#for root, dirs, files in os.walk(data_dir)
						#shutil.rmtree(local_dir)
				except Exception as E:
					logging.info('Error checking directory:'+data_dir, exc_info = True)

	def test_matlab(self):
		self.matlab_check = False
		#eng = matlab.engine.start_matlab()

		#try:
		#	eng.createChannelMapFile(nargout=0)
		#	eng.kilosort_config_file(nargout=0)
		#	eng.kilosort_master_file(nargout=0)
		#except Exception as E:
	#		print(E)
	#		print("Kilosort Error")
		#eng.quit()
		self.matlab_check = True #return True:
		#what if we actually start kilosort from this prompt? and keep pinging it until it is done?
		#then if it crashes, we know. could even reopen this from a bat file if it isn't open?
		# want to get more information about where and when it happens before we add this int
		# will make more complicated since we will have to signal back when it passes, and matlab could still crash it in the middle
		#in which case its of little use to check boforehand, unless we can catch the error and keep the prompt open
		#maybe try running in a different prompt?
		#leave folders with small mock data on them and attempt to run kilosort - could even put it on the C drive
		#maybe a paired down version where it only goes one step beyond loading the data
   
def make_constants(session_name):
	npx_params = namedtuple('npx_params',['start_module','end_module','backup1','backup2'])
	print(session_name)
	default_backup1 = r'N:'
	default_backup2 = os.path.join(r'\\sd5\sd5', session_name)
	default_start = 'secondary_backup_processed_data'
	default_end = 'secondary_backup_processed_data'
	json_directory = r'C:\Users\svc_neuropix\Documents\json_files'

	npx_directories = OrderedDict()
	probe_list = ['A','B','C','D','E','F']
	drive_list = ['D:','E:','F:','G']
	for probe in probe_list:
		for drive in drive_list:
			probe_dir = os.path.join(drive, session_name+'_probe'+probe+'_sorted')
			print(probe_dir)
			if os.path.exists(probe_dir):
				npx_directories[probe_dir]=npx_params(default_start,default_end,default_backup1,default_backup2)
				break
	print(npx_directories)
	return npx_directories

def make_files():
	data_file_params = namedtuple('data_file_params',['relpath','upload','sorting_step'])

	relpaths = {
	                'lfp':r"continuous\Neuropix-PXI-100.1",
	                'spikes':r"continuous\Neuropix-PXI-100.0",
	                'events':r"events\Neuropix-PXI-100.0\TTL_1",
	                'empty':""
	                    }
	        
	data_files = {
	      "probe_info.json":data_file_params('empty',True,'depth_estimation'),
	      "channel_states.npy":data_file_params('events',True,'extraction'),
	      "event_timestamps.npy":data_file_params('events',True,'extraction'),
	      r"continuous\Neuropix-PXi-100.1\continuous.dat":data_file_params('empty',True,'extraction'),
	      "lfp_timestamps.npy":data_file_params('lfp',True,'sorting'),
	      "amplitudes.npy":data_file_params('spikes',True,'sorting'),
	      "spike_times.npy":data_file_params('spikes',True,'sorting'),
	          "mean_waveforms.npy":data_file_params('spikes',True,'mean waveforms'),
	          "spike_clusters.npy":data_file_params('spikes',True,'sorting'),
	          "spike_templates.npy":data_file_params('spikes',True,'sorting'),
	          "templates.npy":data_file_params('spikes',True,'sorting'),
	          "whitening_mat.npy":data_file_params('spikes',True,'sorting'),
	          "whitening_mat_inv.npy":data_file_params('spikes',True,'sorting'),
	          "templates_ind.npy":data_file_params('spikes',True,'sorting'),
	          "similar_templates.npy":data_file_params('spikes',True,'sorting'),
	          "metrics.csv":data_file_params('spikes',True,'metrics'),
	          "channel_positions.npy":data_file_params('spikes',True,'sorting'),
	          "cluster_group.tsv":data_file_params('spikes',True,'sorting'),
	          "channel_map.npy":data_file_params('spikes',True,'sorting'),
	          "params.py":data_file_params('spikes',True,'sorting'),
	      "probe_depth.png":data_file_params("empty",False,'depth estimation'),
	      r"continuous\Neuropix-PXI-100.0\continuous.dat":data_file_params('empty',False,'extraction'),
	      "residuals.dat":data_file_params('spikes',False,'median subtraction'),
	      "pc_features.npy":data_file_params('spikes',False,'sorting'),
	      "template_features.npy":data_file_params('spikes',False,'sorting'),
	      "rez2.mat":data_file_params('spikes',False,'sorting'),
	      "rez.mat":data_file_params('spikes',False,'sorting'),
	      "pc_feature_ind.npy":data_file_params('spikes',False,'sorting'),
	      "template_feature_ind.npy":data_file_params('spikes',False,'sorting')
	      }
	return relpaths, data_files
				
def main():
	app = QApplication([])
	styles.dark(app)

	g = windows.ModernWindow(Processing_Agent())
	# g.resize(350,100)
	g.move(50,270)
	g.setWindowTitle('Neuropixels Surgery/Experiment Notes')
	g.show()
	app.exec_()
	
if __name__ == '__main__':
	main()