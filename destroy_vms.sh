#!/bin/bash
while true 
do
	VBoxManage list runningvms | grep dockerinpractice_mesos | awk '{print $1}' | xargs --no-run-if-empty -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | awk '{print $1}'  | xargs --no-run-if-empty -IXXX VBoxManage unregistervm 'XXX' --delete
	if [[ $(VBoxManage list vms | wc -l) == '0' ]]
	then
		break
	else
		ps -ef | grep virtualbox | grep dockerinpractice_mesos | awk '{print $2}' | xargs kill
		sleep 10
	fi
done