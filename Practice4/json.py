import sys
_path0 = sys.path.pop(0)
import json
sys.path.insert(0, _path0)

with open("sample-data.json", "r") as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<22} {'Speed':<8} {'MTU'}")
print(f"{'-'*50} {'-'*20}  {'------'}  {'------'}")

for item in data["imdata"]:
    attrs = item["l1PhysIf"]["attributes"]
    dn = attrs["dn"]
    descr = attrs.get("descr", "")
    speed = attrs["speed"]
    mtu = attrs["mtu"]
    print(f"{dn:<50} {descr:<22} {speed:<8} {mtu}")
