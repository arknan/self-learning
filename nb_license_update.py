# Someone wrote this script and I am saving it for learning more about winreg

import errno, os, winreg, subprocess, sys, urllib.request, os.path

proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
proc_arch64 = None

try:
    proc_arch64 = os.environ['PROCESSOR_ARCHITEW6432'].lower()
except KeyError:
    pass

if proc_arch == 'x86' and not proc_arch64:
    arch_keys = {0}
elif proc_arch == 'x86' or proc_arch == 'amd64':
    arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
else:
    raise Exception("Unhandled arch: %s" % arch)

# Get NetBackup Path using the INSTALLDIR registry

for arch_key in arch_keys:
    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Veritas\NetBackup", 0, winreg.KEY_READ | arch_key)
    except FileNotFoundError:
        continue

    for i in range(0, winreg.QueryInfoKey(key)[0]):
        skey_name = winreg.EnumKey(key, i)
        skey = winreg.OpenKey(key, skey_name)
        try:
            nb_path = winreg.QueryValueEx(skey, 'INSTALLDIR')[0]
            print("NetBackup is installed in:",nb_path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # DisplayName doesn't exist in this skey
                pass
        finally:
            skey.Close()

# Path to NetBackup binaries
nb_bin = "NetBackup\\bin\\"
nb_path_bin = nb_path + nb_bin
print ("\nPath to NetBackup binaries ",nb_path_bin)

# Running bpminlicense
bpminlic_cmd = "admincmd\\bpminlicense.exe"
bpminlic_bin = nb_path_bin + bpminlic_cmd
bpminlic_syn_verbose = " -verbose"
bpminlic_verbose = bpminlic_bin + bpminlic_syn_verbose
print ("\nRunning bpminlicense -verbose using command", bpminlic_verbose)
print ("\n")
bpminlic_subprocess = subprocess.Popen([bpminlic_bin, "-verbose"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
i = 0

for err in bpminlic_subprocess.stderr:
    print ("bpminlicense command error: ", err)

for bpminlic_out in bpminlic_subprocess.stdout:
    i = i+1
    if i == 1:
        capture_license = bpminlic_out.rstrip()
        capture_license_str = capture_license.decode(encoding='windows-1252')

    print (bpminlic_out.rstrip())
    bpminlic_out_str = bpminlic_out.decode(encoding='windows-1252')
    if "Not expired" in bpminlic_out_str:
        print ("\nLicense is not expired")
        print ("\nLicense is ", capture_license_str)
        break
    if "Expired" in bpminlic_out_str:
        print ("\nLicense is expired, checking for updated license")
        netbackup_license = capture_license_str[0:46]
        print ("\nCurrent license key is: ", netbackup_license)
        print ("\nRemoving license")
        bpminlic_del_subprocess = subprocess.Popen([bpminlic_bin, "-delete_keys", netbackup_license], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for err1 in bpminlic_del_subprocess.stderr:
            print ("bpminlicense command error: ", err1)
        print ("\nChecking for file nblic_location")
        if os.path.isfile("nblic_location.txt") and os.access("nblic_location.txt", os.R_OK):
            print ("File nblic_location exist and is readable")
            print ("\nChecking file nblic_location.txt for current license location")
            nblic_location = open("nblic_location.txt", "r").readline()
            print ("New license is located at: ", nblic_location)
            print ("Downloading new license")
            with urllib.request.urlopen(nblic_location) as response:
               download_license = response.read()
            new_license = download_license[84:132].decode("utf-8")
            print ("\nAdding new downloaded license: ", new_license)
            bpminlic_add_subprocess = subprocess.Popen([bpminlic_bin, "-add_keys", new_license], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for err2 in bpminlic_add_subprocess.stderr:
                print ("bpminlicense command error: ", err2)
            print ("\nCurrent NetBackup License", new_license)
        else:
            print ("\nEither the nblic_location.txt is missing or is not readable")
            print ("Downloading new license")
            nblic_location = 'http://vrts-evidence.labs.veritas.com/evidence/vrts/save/nblic_updater/nblic_updater.txt'
            with urllib.request.urlopen(nblic_location) as response:
               download_license = response.read()
            new_license = download_license[84:132].decode("utf-8")
            print ("\nAdding new downloaded license: ", new_license)
            bpminlic_add_subprocess = subprocess.Popen([bpminlic_bin, "-add_keys", new_license], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for err2 in bpminlic_add_subprocess.stderr:
                print ("bpminlicense command error: ", err2)
            print ("\nCurrent NetBackup License", new_license)

            break
    if "No keys to list" in bpminlic_out_str:
        print ("\nChecking for file nblic_location")
        if os.path.isfile("nblic_location.txt") and os.access("nblic_location.txt", os.R_OK):
            print ("File nblic_location exist and is readable")
            print ("\nChecking file nblic_location.txt for current license location")
            nblic_location = open("nblic_location.txt", "r").readline()
            print ("New license is located at: ", nblic_location)
            print ("Downloading new license")
            with urllib.request.urlopen(nblic_location) as response:
               download_license = response.read()
            new_license = download_license[84:132].decode("utf-8")
            print ("\nAdding new downloaded license: ", new_license)
            bpminlic_add_subprocess = subprocess.Popen([bpminlic_bin, "-add_keys", new_license], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for err2 in bpminlic_add_subprocess.stderr:
                print ("bpminlicense command error: ", err2)
            print ("\nCurrent NetBackup License", new_license)
        else:
            print ("\nEither the nblic_location.txt is missing or is not readable")
            print ("Downloading new license")
            nblic_location = 'http://vrts-evidence.labs.veritas.com/evidence/vrts/save/nblic_updater/nblic_updater.txt'
            with urllib.request.urlopen(nblic_location) as response:
               download_license = response.read()
            new_license = download_license[84:132].decode("utf-8")
            print ("\nAdding new downloaded license: ", new_license)
            bpminlic_add_subprocess = subprocess.Popen([bpminlic_bin, "-add_keys", new_license], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for err2 in bpminlic_add_subprocess.stderr:
                print ("bpminlicense command error: ", err2)
            print ("\nCurrent NetBackup License", new_license)

        break
print("Exiting")
