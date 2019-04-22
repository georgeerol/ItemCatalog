# Item Catalog

This project provides a list of items within a variety of categories as well
as providing a user registration and authentication system. Registered user have
the ability to post edit and delete their own items.

## Prerequisite

This project makes use of  Linux-based virtual machine (VM) as the preceding lessons.

### Vagrant
Vagrant is the software that configures the VM and lets you share files
between your host computer and the VM's filesystem.

### VirtualBox
VirtualBox is the software that actually runs the virtual machine.The supported version
of VirtualBox to install is version 5.1. Newer versions do not work with
the current release of Vagrant.

### VM Configuration
Download this repo: https://github.com/udacity/fullstack-nanodegree-vm
and from your terminal `cd` to the vagrant folder

## Start the Virtual Machine
From the vagrant subdirectory run the command:
```sh
vagrant up
```
When `vagrant up` is finished running run the command below to log int to
the installed Linux VM:
```sh
vagrant ssh
```


## Run

To run the program first setup the database by running from vagrant `python database_setup.py` and then `python ritem_catalog_server.py` from the command
line
