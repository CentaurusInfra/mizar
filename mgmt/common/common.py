import subprocess

def run_cmd(cmd):
	result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	text = result.stdout.read().decode()
	returncode = result.returncode
	return (returncode, text)