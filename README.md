# oai_scenario

This project is based on M-CORD `cord-4.1` branch.  
And only support `cord-4.1` branch.  

`cord-5.0` support is work in progress, will support in the furture.

## Branchs

We have 2 major branchs, master(ciab) and cordpod.
Now both support on ONF CORD project `cord-4.1` branch.

Difference between ciab and cordpod is implement in OAI Services network.

ciab uses the Service Dependencies function to make services communicate with
each gateway.

![](https://raw.githubusercontent.com/aweimeow/oai_scenario/master/assets/service_graph.png)

cordpod uses flat network insteads of service chain, 
and have 2 layer XOS Services, vepc in upper layer, vhss, vmme, vspgw in lower
layer.

We can assign connection relation in vepc and vepc will going to create other
child services.

## Installation

```
git clone https://github.com/aweimeow/oai_scenario ~/oai_scenario
cd ~/oai_scenario
```

Use `start.sh` to overwrite original files.  
This script will delete original M-CORD services directory,  
and use modified services source code instead.

```bash
bash start.sh
```

And execute following commands to build OAI M-CORD.

```
cd ~/cord/build
make PODCONFIG=mcord-oai-virtual.yml config
make -j4 build
```

Then you can check Service Instance by `nova` command.

```
$ ssh head1
head1 $ source /opt/cord_profile/admin-openrc.sh
head1 $ nova list --all-tenants

+--------------------------------------+-------------------+--------+------------+-------------+----------------------------------------------------------------+
| ID                                   | Name              | Status | Task State | Power State | Networks                                                       |
+--------------------------------------+-------------------+--------+------------+-------------+----------------------------------------------------------------+
| 040804e0-5f6d-48d1-a44e-7334f18795ce | mysite_oaispgw1-2 | ACTIVE | -          | Running     | management=172.27.0.2; public=10.8.1.2; vspgw_network=10.0.8.2 |
| e6fa7b25-6e54-4882-98dd-5e731e76239b | mysite_oaispgw1-4 | ACTIVE | -          | Running     | management=172.27.0.5; public=10.8.1.3; vspgw_network=10.0.8.3 |
| 2bb5f57d-7858-41d3-9d18-4b056055853f | mysite_vhss1-3    | ACTIVE | -          | Running     | management=172.27.0.4; vhss_network=10.0.7.2                   |
| f61cd0cb-cac1-492e-86c0-6524e795d0b4 | mysite_vmme1-1    | ACTIVE | -          | Running     | management=172.27.0.3; vmme_network=10.0.6.2                   |
+--------------------------------------+-------------------+--------+------------+-------------+----------------------------------------------------------------+
```

### Patch

ONOS's application: CORDVTN has bugs, so you may need execute `vtn-patch.py`
to complete Service Gateway.

```
cd ~/oai_scenario
python vtn-patch.py
```

You can check `flow` and `group` information in ONOS WebUI.

```
ssh -NfL 0.0.0.0:8182:0.0.0.0:8182 head1
```

and access `http://<your_CORD_ip>:8182/onos/ui` to check flows.

## Usage

```
ssh head1
head1$ scp ~/.ssh/id_rsa ubuntu@10.1.0.14:~/.ssh
head1$ ssh ubuntu@10.1.0.14

# SSH into Service Instance, reference to nova output
ubuntu@multicolored-jump:~$ ssh ubuntu@172.27.0.2

# This is vHSS Service Instance
ubuntu@vhss:~$ sudo su -
root@vhss:~$ cd ~/openair-cn/SCRIPT/
root@vhss:~/openair-cn/SCRIPT$ ./run_hss

# This is vMME Service Instance
ubuntu@nano:~$ sudo su -
root@nano:~$ cd ~/openair-cn/SCRIPT/
root@nano:~/openair-cn/SCRIPT$ ./run_mme

# This is vSPGW Service Instance
ubuntu@spgw:~$ sudo su -
root@spgw:~$ cd ~/openair-cn/SCRIPT/
root@spgw:~/openair-cn/SCRIPT$ ./run_spgw
```

As following snapshot:  
![](https://raw.githubusercontent.com/aweimeow/oai_scenario/master/assets/snapshot.png)

## LICENSE

Source Code in this project is under MIT License.  
Open Air Interface image is built by [Open Air Interface Source
Code](https://gitlab.eurecom.fr/oai/openair-cn).  
It is under Apache License v2 (APLv2).
