#!/bin/bash
if [[ $(command -v VBoxManage) != '' ]]
then
	while true 
	do
		VBoxManage list runningvms | grep {{ skeleton.module_name }} | awk '{print $1}' | xargs -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep {{ skeleton.module_name }} | awk '{print $1}'  | xargs -IXXX VBoxManage unregistervm 'XXX' --delete
		if [[ $(VBoxManage list vms | grep {{ skeleton.module_name }} | wc -l) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep {{ skeleton.module_name }} | awk '{print $2}' | xargs kill
			sleep 10
		fi
	done
fi

