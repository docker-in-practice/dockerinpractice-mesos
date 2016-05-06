"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule
import random
import string

class dockerinpractice_mesos(ShutItModule):

	def build(self, shutit):
		# Some useful API calls for reference. See shutit's docs for more info and options:
		#
		# ISSUING BASH COMMANDS
		# shutit.send(send,expect=<default>) - Send a command, wait for expect (string or compiled regexp)
		#                                      to be seen before continuing. By default this is managed
		#                                      by ShutIt with shell prompts.
		# shutit.multisend(send,send_dict)   - Send a command, dict contains {expect1:response1,expect2:response2,...}
		# shutit.send_and_get_output(send)   - Returns the output of the sent command
		# shutit.send_and_match_output(send, matches)
		#                                    - Returns True if any lines in output match any of
		#                                      the regexp strings in the matches list
		# shutit.send_until(send,regexps)    - Send command over and over until one of the regexps seen in the output.
		# shutit.run_script(script)          - Run the passed-in string as a script
		# shutit.install(package)            - Install a package
		# shutit.remove(package)             - Remove a package
		# shutit.login(user='root', command='su -')
		#                                    - Log user in with given command, and set up prompt and expects.
		#                                      Use this if your env (or more specifically, prompt) changes at all,
		#                                      eg reboot, bash, ssh
		# shutit.logout(command='exit')      - Clean up from a login.
		#
		# COMMAND HELPER FUNCTIONS
		# shutit.add_to_bashrc(line)         - Add a line to bashrc
		# shutit.get_url(fname, locations)   - Get a file via url from locations specified in a list
		# shutit.get_ip_address()            - Returns the ip address of the target
		# shutit.command_available(command)  - Returns true if the command is available to run
		#
		# LOGGING AND DEBUG
		# shutit.log(msg,add_final_message=False) -
		#                                      Send a message to the log. add_final_message adds message to
		#                                      output at end of build
		# shutit.pause_point(msg='')         - Give control of the terminal to the user
		# shutit.step_through(msg='')        - Give control to the user and allow them to step through commands
		#
		# SENDING FILES/TEXT
		# shutit.send_file(path, contents)   - Send file to path on target with given contents as a string
		# shutit.send_host_file(path, hostfilepath)
		#                                    - Send file from host machine to path on the target
		# shutit.send_host_dir(path, hostfilepath)
		#                                    - Send directory and contents to path on the target
		# shutit.insert_text(text, fname, pattern)
		#                                    - Insert text into file fname after the first occurrence of
		#                                      regexp pattern.
		# shutit.delete_text(text, fname, pattern)
		#                                    - Delete text from file fname after the first occurrence of
		#                                      regexp pattern.
		# shutit.replace_text(text, fname, pattern)
		#                                    - Replace text from file fname after the first occurrence of
		#                                      regexp pattern.
		# ENVIRONMENT QUERYING
		# shutit.host_file_exists(filename, directory=False)
		#                                    - Returns True if file exists on host
		# shutit.file_exists(filename, directory=False)
		#                                    - Returns True if file exists on target
		# shutit.user_exists(user)           - Returns True if the user exists on the target
		# shutit.package_installed(package)  - Returns True if the package exists on the target
		# shutit.set_password(password, user='')
		#                                    - Set password for a given user on target
		#
		# USER INTERACTION
		# shutit.get_input(msg,default,valid[],boolean?,ispass?)
		#                                    - Get input from user and return output
		# shutit.fail(msg)                   - Fail the program and exit with status 1
		#
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		module_name = 'dockerinpractice_mesos_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.send('rm -rf /tmp/' + module_name + ' && mkdir -p /tmp/' + module_name + ' && cd /tmp/' + module_name)
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send('vagrant up --provider virtualbox',timeout=99999)
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -',password='vagrant')

		# Install docker and git
		shutit.send('apt-get install git docker.io')

		# Start master
		shutit.send('docker run -d --name mesmaster redjack/mesos:0.21.0 mesos-master --work_dir=/opt')
		shutit.send('sleep 20')
		shutit.send('''docker inspect -f '{{.NetworkSettings.IPAddress}}' mesmaster''')
		shutit.send('docker logs -f mesmaster')

		# Start slave
		shutit.send('docker run -d --name messlave --pid=host -v /var/run/docker.sock:/var/run/docker.sock -v /sys:/sys redjack/mesos:0.21.0 mesos-slave --master=172.17.0.2:5050 --executor_registration_timeout=5mins --isolation=cgroups/cpu,cgroups/mem -')
		shutit.send('sleep 20')
		shutit.send('''docker inspect -f '{{.NetworkSettings.IPAddress}}' messlave''')

		# Example framework
		shutit.send('git clone https://github.com/docker-in-practice/mesos-nc.git')
		shutit.login('docker run -it --rm -v $(pwd)/mesos-nc:/opt redjack/mesos:0.21.0 bash')
		shutit.send('cd /opt')
		shutit.send('export PYTHONUSERBASE=/usr/local')
		shutit.send('python myframework.py 172.17.0.2:5050')
		shutit.logout() # log out of docker run

		shutit.logout() # log out of vagrant root
		shutit.logout() # log out of vagrant machine
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/trusty64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		return True

def module():
	return dockerinpractice_mesos(
		'tk.shutit.dockerinpractice_mesos', 1845506479.0001,
		description='Mesos framework example',
		maintainer='ian.miell@gmail.com',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualbox.virtualbox.virtualbox','tk.shutit.vagrant.vagrant.vagrant']
	)
