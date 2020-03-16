## FRR BGP Peer Manager Operator

[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)

This operator works in conjunction with Metallb configured in BGP mode and a Linux Router to create a LoadBalancer structure for k8s clusters.  The function of this operator is to automate the configuration of BGP neighbors in the Linux Router


## How it works

THe operator runs every reconcilePeriod interval, it reads the metallb configuration and checks the metalb namespace for pods running speakers.

If the speaker node does not have a neighbor entry in the FRR router, an entry is added.

If the operator finds a neighbor with no connections, configured for the AS used by metallb, the neighbor statement is removed.

For more information on [metallb]

## Prerequisites

- Linux host for Router - Ubuntu 18.04 LTS recommended
- Routing software on Linux host -  [FRRouting][frr]

- k8s cluster with [Metallb][metallb] installed

- Configure linux router for bgp (frr) - bgp needs to be configured, the operator will add neighbors
the bgp speaker

```
$ kubectl get pods -o wide
NAME                         READY   STATUS    RESTARTS   AGE   IP              NODE
controller-dc7447947-snw28   1/1     Running   10         10d   10.244.0.241    k8s1
speaker-7x4bq                1/1     Running   37         56d   172.30.250.11   k8s2
speaker-hbnxp                1/1     Running   36         56d   172.30.250.10   k8s1
speaker-kxf68                1/1     Running   37         56d   172.30.250.12   k8s3
```

Example simple frr configuraiton

```
frr# show run
Building configuration...

Current configuration:
!
frr version 7.2.1
frr defaults traditional
hostname frr
log file /var/log/frr/log
service integrated-vtysh-config
!
router bgp 65551
 bgp log-neighbor-changes
 !
 address-family ipv4 unicast
  redistribute connected
 exit-address-family
!
line vty
!
end
```
## Installation of bgppeer-operator

1. Setup Router access for operator.  The ansible operator configures the Router over SSH, requiring that the router has access and the account keys.

```
# Add ansible-operator user
$ sudo useradd ansible-operator -m -u 1001 -s /bin/bash
# set a temp password for the ansible-operator user
```
2.  Create ssh keys on host with kubectl configured for cluster.  As the ansible operator connects to the router, the private key for the ansible-operator user is stored as a k8s secret and projected into the operator containers.  (Setting RBAC to restrict access is recommended)

```
$ ssh-keygen -f ansible-operator -t rsa

# copy keys to Router
$ ssh-copy-id -i ansible-operator.pub ansible-operator@172.30.250.1

# check keys
$ ssh -o "IdentifiesOnly=yes" -i ansible-operator ansible-operator@172.30.250.1

# add private key to k8s secrets

$ kubectl create namespace arbf-operators

$ kubectl -n arbf-operators create secret generic ansible-operator-ssh --from-file=ansible-operator

# Recommend:  removing the keys from the host after installation complete and verified
```

3.  Install the Operator

To install the bgppeer-operator, apply this manifest:

```
$ kubectl apply -f https://raw.githubusercontent.com/acnodal/arbf-bgppeer-operator/master/manifests/arbf-nft-operator.yml  
```
This will deploy the bgppeer-operator in your cluster in the arbf-operators namespace.  The components of the manifest are:

 - Custom Resource Definations
 - Service Account, Roles & Role Bindings required by the operator
 - The bgppeer-operator

4. Configure the Operator

No specific configuration of the operator is required, unless metallb is installed in a namespace other than metalb-system.  The metallb namespace can be configured in the bgppeers custom resource

4.  Troubleshooting

Troubleshooting consists of checking the oeprator and the linux router.

Checking the status of the operator

```
$ kubectl -n arbf-operators get bgppeer -o yaml
apiVersion: v1
items:
- apiVersion: bgppeer.acnodal.com/v1alpha1
  kind: Bgppeer
  metadata:
    annotations:
      ansible.operator-sdk/verbosity: "4"
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"bgppeer.acnodal.com/v1alpha1","kind":"Bgppeer","metadata":{"annotations":{},"name":"bgppeer","namespace":"arbf-operators"},"spec":{"metallb_namespace":"metallb-system"}}
    creationTimestamp: "2020-03-16T13:54:29Z"
    generation: 1
    name: bgppeer
    namespace: arbf-operators
    resourceVersion: "3915798"
    selfLink: /apis/bgppeer.acnodal.com/v1alpha1/namespaces/arbf-operators/bgppeers/bgppeer
    uid: 3ade5456-be9f-42d2-9d11-155750ce535e
  spec:
    metallb_namespace: metallb-system
  status:
    conditions:
    - lastTransitionTime: "2020-03-16T13:54:36Z"
      message: Running reconciliation
      reason: Running
      status: "True"
      type: Running
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
```
Inspecting the operator logs will show output familar to ansible users.  Note that the pod contains two containers, the ansible container shows the ansible output

```
$ kubectl -n arbf-operators logs arbf-bgppeer-operator-55d6b4754c-whx78 -c ansible
```

Finally compare the bgp speakers and the state of peers/configuration in the linux router.  There should be a neighbor for every pod running a speaker.

```
$ kubectl get pods -n metallb-system -o wide
NAME                         READY   STATUS    RESTARTS   AGE   IP              NODE
controller-dc7447947-snw28   1/1     Running   19         28d   10.244.0.99     k8s1
speaker-7x4bq                1/1     Running   46         73d   172.30.250.11   k8s2 
speaker-hbnxp                1/1     Running   45         73d   172.30.250.10   k8s1 
speaker-kxf68                1/1     Running   46         73d   172.30.250.12   k8s3

rr# show bgp summary 

IPv4 Unicast Summary:
BGP router identifier 172.30.255.254, local AS number 65551 vrf-id 0
BGP table version 18
RIB entries 15, using 3680 bytes of memory
Peers 3, using 82 KiB of memory

Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
172.30.250.10   4      65552     623     625        0    0    0 05:07:12            5
172.30.250.11   4      65552     620     622        0    0    0 05:06:50            5
172.30.250.12   4      65552     600     601        0    0    0 04:56:35            5

Total number of neighbors 3

```


[frr]: https://frrouting.org
[metallb]: https://metallb.universe.tf
