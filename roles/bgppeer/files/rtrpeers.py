#!/usr/bin/env python3

import sys
import json
import yaml
import argparse

rtrpeers = []


parser = argparse.ArgumentParser(description="Extract dumped router peers cleanup unused output yaml")
parser.add_argument("--j", required=True, help="Dumped JSON file from vtysh show bgp sum json" )
parser.add_argument("--y", required=True, help="YAML formated vars for import into ansbile")

args = parser.parse_args()


try:


    with open(args.j) as f:
        data = json.load(f)



        for i, item in enumerate(data["ipv4Unicast"]["peers"]):

            rtrpeers.append({'nodeipaddr' : item ,
                        'nodeas' : data["ipv4Unicast"]["peers"][item]["remoteAs"],
                        'connections' : data["ipv4Unicast"]["peers"][item]["connectionsEstablished"]
                         })


         
    f.close()

    with open(args.y, 'w') as o:
        o.write('rtrpeerstatus:\n')
        yaml.dump(rtrpeers, o)

    o.close()



except IOError:
    print("Error input file ", args.j, " does not exist!")
    sys.exit(1)






