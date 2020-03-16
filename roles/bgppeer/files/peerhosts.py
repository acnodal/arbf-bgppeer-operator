#!/usr/bin/env python3

import sys
import json
import yaml
import argparse

peerhosts = []


parser = argparse.ArgumentParser(description="Convert dumped metalb pods to speakers & ipaddrs as yaml variable")
parser.add_argument("--j", required=True, help="Dumped JSON file created by k8sinfo kind=POD" )
parser.add_argument("--y", required=True, help="YAML formated vars for import into ansbile")

args = parser.parse_args()


try:


    with open(args.j) as f:
        data = json.load(f)


        for i, item in enumerate(data):

            if 'speaker' in data[i]["metadata"]["name"]:
                peerhosts.append({'name' : data[i]["spec"]["nodeName"],
                            'podIP': data[i]["status"]["podIP"]
                            })

    f.close()

    with open(args.y, 'w') as o:
        o.write('peerhosts:\n')
        yaml.dump(peerhosts, o)

    o.close()


except IOError:
    print("Error input file ", args.j, " does not exist!")
    sys.exit(1)






