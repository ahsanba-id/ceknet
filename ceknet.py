# A simple tool for managing network adapters on your Windows local machine.

# Disclaimer: This program is provided as-is, and I am not responsible for any misuse, damages, or consequences resulting from its use.
# Use this program responsibly and follow any applicable laws and guidelines. By using this code, you acknowledge and agree to these terms.

import json
import sys
import os
import argparse
import subprocess
import psutil
import time
import select
import urllib.request
import urllib.error

def read_file(filename):
	try:
		with open(filename, 'r', encoding='utf-8') as file:
			return json.load(file)
	except (FileNotFoundError, IOError, UnicodeDecodeError):
		return None

# Translation file handling
language = 'english'
for file in os.listdir():
	if file.endswith('.lang'):
		language = file.split('.')[0] # extract the language name without extension
		break
translation = read_file(f'{language}.lang')

# Translation handling function
def get_translation(key, translation):
	if translation is None:
		return key
	if key in translation:
		return translation[key]
	return key

# Function
def get_adapters():
	try:
		command = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True, check=True)
		line_splitting = command.stdout.strip().split('\n')
		adapter_list = []
		for adapter_name in line_splitting:
			if len(adapter_name.split()) >=4 and adapter_name.split()[0] == 'Enabled':
				adapter_list.append(' '.join(adapter_name.split()[3:])) # admin state, state, type, interface, name
		return adapter_list
	except subprocess.CalledProcessError as e:
		print(get_translation('Error occurred:', translation) + ' ' + f'{e}')
		return None

def get_adapters_inactive():
	try:
		command = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True, check=True)
		line_splitting = command.stdout.strip().split('\n')
		adapter_list_inactive = []
		for adapter_name_inactive in line_splitting:
			if len(adapter_name_inactive.split()) >= 4 and adapter_name_inactive.split()[0] == 'Disabled':
				adapter_list_inactive.append(' '.join(adapter_name_inactive.split()[3:])) # admin state, state, type, interface, name
		return adapter_list_inactive
	except subprocess.CalledProcessError as e:
		print(get_translation('Error occurred:', translation) + ' ' + f'{e}')
		return None

def get_adapters_all():
	try:
		command = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True, check=True)
		line_splitting = command.stdout.split('\n')
		adapter_list_all = []
		for adapter_name_all in line_splitting:
			adapter_list_all.append(adapter_name_all.strip())
		return adapter_list_all
	except subprocess.CalledProcessError as e:
		print(get_translation('Error occurred:', translation) + ' ' + f'{e}')
		return None

def get_network_traffic(interface):
	try:
		stats = psutil.net_io_counters(pernic=True)
		if interface in stats:
			traffic = stats[interface]
			upload_kb = round(traffic.bytes_sent, 2)
			download_kb = round(traffic.bytes_recv, 2)
			return upload_kb, download_kb
		else:
			return None, None
	except KeyError:
		return None, None

def display_network_traffic(interface):
	try:
		upload, download = get_network_traffic(interface)
		if int(upload) and int(download) is not None:
			print(get_translation('Data uploaded   :', translation) + ' ' + f'{upload/1024/1024:,.2f}' + ' ' + 'MB') # f'{upload:.2f} to add 2 decimal numbers
			print(get_translation('Data downloaded :', translation) + ' ' + f'{download/1024/1024:,.2f}' + ' ' + 'MB')
			print(get_translation('Data in Total   :', translation) + ' ' + f'{(upload + download)/1024/1024:,.2f}' + ' ' + 'MB')
		else:
			print(get_translation('Unable to retrieve traffic information for the specified interface.', translation))
	except KeyError:
		return None

def display_network_traffic_live(interface):
	while True:
		upload, download = get_network_traffic(interface)
		try:
			if int(upload) and int(download) is not None:
				sys.stdout.write('\r' + get_translation('Data uploaded   :', translation) + ' ' + f'{upload/1024/1024:,.0f}' + ' MB' + f' | ' + f'{upload:,.0f}' + ' bytes' + (' '*20))
				sys.stdout.write('\n' + get_translation('Data downloaded :', translation) + ' ' + f'{download/1024/1024:,.0f}' + ' MB' + f' | ' + f'{download:,.0f}' + ' bytes' + (' '*20))
				sys.stdout.write('\n' + get_translation('Data in Total   :', translation) + ' ' + f'{(upload + download)/1024/1024:,.0f}' + ' MB' + f' | ' + f'{(upload + download):,.0f}' + ' bytes')
				sys.stdout.flush()
			else:
				sys.stdout.write(get_translation('\rUnable to retrieve traffic information for the specified interface.', translation))
				sys.stdout.flush()
			time.sleep(1)
		except KeyboardInterrupt:
			print(get_translation('\n\nProgram terminated by user.', translation), flush=True)
			return ''

def display_established_connections():
	try:
		def get_established_connections():
			established_connections = [conn for conn in psutil.net_connections() if conn.status == psutil.CONN_ESTABLISHED]
			return established_connections
		def filter_localhost(connections):
			return [conn for conn in connections if conn.laddr.ip != '127.0.0.1']
		while True:
			os.system('cls' if os.name=='nt' else 'clear')
			if filter_localhost(get_established_connections()):
				for conn in filter_localhost(get_established_connections()):
					print(f'{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}. {conn.status} {get_translation("and registered as process ID:", translation)} {conn.pid}', flush=True)
			else:
				print(get_translation('No established connections.', translation), flush=True)
			time.sleep(1)
	except KeyboardInterrupt:
		print(get_translation('\n\nProgram terminated by user.', translation), flush=True)
		return ''

def disable_adapter(adapter_name):
	try:
		subprocess.run(['netsh', 'interface', 'set', 'interface', f'{adapter_name}', 'admin=disabled'], capture_output=True, text=True, check=True)
		print(get_translation('Network adapter', translation) + ' ' + f'{adapter_name}' + ' ' + get_translation('disabled successfully.', translation))
	except subprocess.CalledProcessError as e:
		print(get_translation('Failed to disable network adapter', translation) + ' ' + f'{adapter_name}' + '. ' + get_translation('Error:', translation) + ' ' + f'{e}')

def enable_adapter(adapter_name_inactive):
	try:
		subprocess.run(['netsh', 'interface', 'set', 'interface', f'{adapter_name_inactive}', 'admin=enabled'], capture_output=True, text=True, check=True)
		print(get_translation('Network adapter', translation) + ' ' + f'{adapter_name_inactive}' + ' ' + get_translation('enabled sucessfully.', translation))
	except subprocess.CalledProcessError as e:
		print(get_translation('Failed to enable network adapter', translation) + ' ' + f'{adapter_name_inactive}' + '. ' + get_translation('Error:', translation) + ' ' + f'{e}')

def get_public_ip():
	# The URL can be added or replaced with another sites
	url = ['https://ifconfig.me', 'https://ipinfo.io/ip', 'https://icanhazip.com', 'https://myexternalip.com/raw', 'https://ifconfig.co']
	for site in url:
		print(get_translation('Checking the', translation) + ' ' + f'{site}' + ' ' + get_translation('for availability...', translation), flush=True)
		try:
			with urllib.request.urlopen(site, timeout=5) as response:
				public_ip = response.read().decode('utf-8')
				if public_ip.strip() != '':
					return public_ip
		except urllib.error.URLError:
			pass
	return None

def get_version():
	return get_translation('Version', translation) + ' 0.1 (BETA)\n@ahsanba'

# Translation help
translate_help = get_translation('show this help message and exit', translation)
translate_description = get_translation('Ceknet is a simple tool for managing network adapters on your Windows local machine.', translation)
translate_epilog = get_translation('Example 1: python ceknet.py --interface \"Wi-Fi\" --traffic\nExample 2: python ceknet.py -c', translation)
translate_list = get_translation('list enabled network adapters', translation)
translate_listdisable = get_translation('list disabled network adapters', translation)
translate_listall = get_translation('list all network adapters', translation)
translate_connection = get_translation('displaying established network connection in real-time', translation)
translate_publicip = get_translation('displaying your public IP address', translation)
translate_version = get_translation('show the tool version', translation)
translate_interface = get_translation('specify the network interface', translation)
translate_traffic = get_translation('displaying data upload and download', translation)
translate_trafficlive = get_translation('displaying data upload and download in real-time.\nCTRL+C can be used to exit from the real-time view', translation)
translate_off = get_translation('disabling the adapter', translation)
translate_on = get_translation('enabling the adapter', translation)

# Parsing command-line arguments
parser = argparse.ArgumentParser(description=translate_description, epilog=translate_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-l', '--list', action='store_true', help=translate_list)
parser.add_argument('-ld', '--listdisable', action='store_true', help=translate_listdisable)
parser.add_argument('-la', '--listall', action='store_true', help=translate_listall)
parser.add_argument('-c', '--connection', action='store_true', help=translate_connection)
parser.add_argument('-ip', '--publicip', action='store_true', help=translate_publicip)
parser.add_argument('-v', '--version', action='store_true', help=translate_version)
parser.add_argument('-i', '--interface', help=translate_interface)
parser.add_argument('-t', '--traffic', action='store_true', help=translate_traffic)
parser.add_argument('-tl', '--trafficlive', action='store_true', help=translate_trafficlive)
parser.add_argument('-off', '--off', action='store_true', help=translate_off)
parser.add_argument('-on', '--on', action='store_true', help=translate_on)
args = parser.parse_args()

# Main function
if __name__ == '__main__':
	if args.list:
		print(get_translation('\nLIST OF ENABLED DEVICES:', translation))
		print('-'*25)
		for adapter_name in get_adapters():
			print(adapter_name)
	elif args.listdisable:
		print(get_translation('\nLIST OF DISABLED DEVICES:', translation))
		print('-'*25)
		for adapter_name_inactive in get_adapters_inactive():
			print(adapter_name_inactive)
	elif args.listall:
		for adapter_name_all in get_adapters_all():
			print(adapter_name_all)
	elif args.interface:
		if args.interface in get_adapters():
			print(get_translation('Network adapter', translation) + ' ' + f'{args.interface}'+ '.')
			if args.traffic:
				display_network_traffic(args.interface)
			if args.trafficlive:
				display_network_traffic_live(args.interface)
			if args.off:
				disable_adapter(args.interface)
		elif args.interface in get_adapters_inactive():
			print(get_translation('Network adapter', translation) + ' ' + f'{args.interface}' + '.')
			if args.on:
				enable_adapter(args.interface)
		else:
			print(get_translation('Network adapter', translation) + ' ' + f'{args.interface}' + ' ' + get_translation('does not exist.', translation))
	elif args.connection:
		print(display_established_connections())
	elif args.publicip:
		print(get_translation('Your public IP address is:', translation) + ' ' + get_public_ip())
	elif args.version:
		print(get_version())
	else:
		print(get_translation('Please use --help to learn how to use it.', translation))
