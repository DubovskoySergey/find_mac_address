from netmiko import ConnectHandler
from netmiko.base_connection import BaseConnection
import re
import time

username = input("Введите ипя пользователя JunOS: ")
password = input("Введите пароль пользователя JunOS: ")

#Кроссовые БЦ
bc3 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc5 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc8 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc13 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc18 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc20 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
bc22 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}

#Кроссовые ТС
tc11 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc12 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc13 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc14 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc31 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc32 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc33 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc34 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}
tc51 = {'device_type' : 'juniper', 'ip' : '', 'username' : '{}'.format(username), 'password' : '{}'.format(password)}

#Список кроссовых
bc_list = {'bc3' : bc3, 'bc5' : bc5, 'bc8' : bc8, 'bc18' : bc18, 'bc20' : bc20, 'bc22' : bc22}
tc_list = {'tc11' : tc11, 'tc12' : tc12, 'tc13' : tc13, 'tc14' : tc14, 'tc31' : tc31, 'tc32' : tc32, 'tc33' : tc33, 'tc34' : tc34, 'tc51' : tc51}

# Получение мак-адреса по ip с dhcp сервера
def search_mac():
    device_params = {
        'device_type' : 'linux',
        'ip' : '',
        'username' : '',
        'password' : '',
        'session_log': "output.txt",
    }
    s_ip = str(input("Введите ip: "))
    print('Ищу mac-adress устройства.')
    with BaseConnection(**device_params) as ssh:
        ssh.send_command('cd /var/log')
        result = ssh.send_command('grep -i "{} to ..:..:..:..:..:.." dhcpd.log | tail -1'.format(s_ip))
        mac_addres = re.search(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', result)
        mac_addres = mac_addres.group()
        print("MAC-adress: {}".format(mac_addres))
    return mac_addres

# Поиск и перезагрузка порта по POE
def connect_jun(mac_addres, device_params):
    print('Connection to device', device_params['ip'])
    with ConnectHandler(**device_params) as ssh:
        ssh.config_mode()
        result = ssh.send_command('run show ethernet-switching table | match {}'.format(mac_addres),strip_prompt = False, cmd_verify = False)
        port = re.search(r'ge-[0-9]{1,2}/0/[0-9]{1,2}', result)
        port = port.group()
        print("Выключаю port: {}".format(port))
        command = 'set poe interface {} disable'.format(port)
        result = ssh.send_command(command,strip_prompt = False, cmd_verify = False)
        time.sleep(3)
        ssh.commit()
        time.sleep(5)
        print("Включаю port: {}".format(port))
        result = ssh.send_command('delete poe interface {} disable'.format(port))
        time.sleep(3)
        ssh.commit()
        print("Порт {} перезагружен.".format(port))

# Получение мак адреса устройства и поиск с последующей перезагрузкой порта по mac адресу.
mac_addres = search_mac()
cross = input("Укажите кроссовую(tc№,bc№): ")
if "bc" in cross.lower():
    if cross.lower() in bc_list.keys():
        connect_jun(mac_addres, bc_list.get(cross))
    else:
        print("В БЦ нет кроссовой {}".format(cross))
elif "tc" in cross.lower():
    if cross.lower() in tc_list.keys():
        connect_jun(mac_addres, bc_list.get(cross))
    else:
        print("В ТЦ нет кроссовой {}".format(cross))
