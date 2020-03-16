BGP Peer
=========

A role runs at the reconcilePeriod specificed in watches.yaml.  On execution this role updates the bgp neighbor configuration on an FRR Router

Requirements
------------

This role does not have any specific ansible requirements however the base operator container has been updated to include ssh so targets outside of the cluster can be configured

Role Variables
--------------

Role variables are contained in the cr.yml. It also uses variable found in the metallb configmap

Dependencies
------------

None

Example Playbook
----------------

The role is run by the ansible operator

License
-------

Apache 2

Author Information
------------------

Adam Dunstan adam@acnodal.com