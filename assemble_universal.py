import json
from os.path import exists, join, normpath, basename
import sys

def load_file(filename):
    path = join(full_path, 'extracted', f"{base_name}_{filename}.txt")
    if exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None

def assemble():
    if exists(full_path) == False:
        print("[!] Unable to find device directory name")
        return

    # All should have these
    manufacturer = base_name.split('_')[0].replace('-', ' ').replace("   ", "-")
    name = base_name.split('_')[1].replace('-', ' ').replace("   ", "-")
    
    device_class = load_file("device_class")
    chip = load_file("chip")
    sdk = load_file("sdk")
    bv = load_file("bv")
    uuid = load_file("uuid")

    ap_ssid = load_file("ap_ssid")
    auth_key = load_file("auth_key")
    address_finish = load_file("address_finish")
    icon = load_file("icon")

    # Optional items
    swv = load_file("swv")
    if swv is None:
        swv = "0.0.0"
    key = load_file("key")
    address_datagram = load_file("address_datagram")
    address_ssid = load_file("address_ssid")
    address_passwd = load_file("address_passwd")
    schema_id = load_file("schema_id")
    schema = load_file("schema")
    if schema is not None and schema != '':
        schema = json.loads(schema)
    issue = load_file("issue")

    profile = {}
    firmware = {}
    data = {}

    profile["name"] = f"{swv} - {chip}"
    profile["sub_name"] = device_class
    profile["type"] = "Universal"
    profile["icon"] = icon

    firmware["chip"] = chip
    firmware["name"] = device_class
    firmware["version"] = swv
    firmware["sdk"] = sdk
    if key is not None:
        firmware["key"] = key

    profile["firmware"] = firmware

    data["address_finish"] = address_finish
    if address_datagram is not None:
        data["address_datagram"] = address_datagram
    if address_ssid is not None:
        data["address_ssid"] = address_ssid
    if address_passwd is not None:
        data["address_passwd"] = address_passwd

    profile["data"] = data

    universal_profile_name = f"{device_class}-{swv}-sdk-{sdk}-{bv}"

    print(f"[+] Dumping universal profile {universal_profile_name}")
    with open(join(full_path, f"{universal_profile_name}.json"), 'w') as f:
        f.write(json.dumps(profile, indent=4))

    device = {}
    device["manufacturer"] = manufacturer
    device["name"] = name
    # this won't be used in exploiting, bit it is useful to have a known one
    # in case we need to regenerate schemas from Tuya's API
    device["uuid"] = uuid
    device["auth_key"] = auth_key
    device["ap_ssid"] = ap_ssid

    if issue is not None:
        device["github_issues"] = [ int(issue) ]

    device["profiles"] = [ universal_profile_name ]

    if schema_id is not None and schema is not None:
        schema_dict = {}
        schema_dict[f"{schema_id}"] = schema
        device["schema"] = schema_dict

    device_filename = f"{manufacturer.replace(' ', '-')}-{name.replace(' ', '-')}"
    print(f"[+] Dumping device profile {device_filename}")
    with open(join(full_path, f"{device_filename}.json"), 'w') as f:
        f.write(json.dumps(profile, indent=4))


if __name__ == '__main__':
    if not sys.argv[1:]:
        # this currently expects a specific folder structure to work, subject to change
        # folder named manufacturer-name_device-model-AA---123
        # inside should be a folder named "extracted"
        # inside the extracted folder should be various other files generated by other
        # adjascent scripts all prefixed with the base folder name
        print('Usage: python assemble_universal.py <device_folder_name>')
        sys.exit(1)

    global full_path
    global base_name
    full_path = sys.argv[1]
    base_name = basename(normpath(full_path))

    assemble()
