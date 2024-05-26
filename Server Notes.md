# AWS Minecraft

## Something Login?

### Username

`ben`

### Password

`hH|4{hlx`

## Something Else Login

### Access Key

`AKIAQ3EGQ6Y4INA3W5OX`

### Secret Access Key

`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`

## Fingerprints

`aws ec2 get-console-output --instance-id i-09194785048b629ea --query Output --output text > fingerprint.txt`

    #############################################################
    -----BEGIN SSH HOST KEY FINGERPRINTS-----
    1024 SHA256:WL7d/UBAwqO7xbBb+o0qjEO7CRkJwYhtAu9Qd7AlHT4 root@ip-172-31-40-219 (DSA)
    256 SHA256:oQO8Dokvc+PTJ2JhreG+eQsjtRsOkxZ/fAHkJR8IxQw root@ip-172-31-40-219 (ECDSA)
    256 SHA256:5x42ASHteYK8CXuS0BEDCV4DR73/vT2nyrHawzDpogE root@ip-172-31-40-219 (ED25519)
    3072 SHA256:sr2JlAldvxyitIfH8G1i4WtqcIPY6byCuSsntFQqkaU root@ip-172-31-40-219 (RSA)
    -----END SSH HOST KEY FINGERPRINTS-----
    #############################################################

## Install OpenSSH / Choco

`Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0`

`Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))`

`choco install nano`

# Server Setup

## EC2 Instace Price Comparisons

| Name | Cost per Hour | GPUs(?) | RAM | Network |
| :--: | ------------- | ------- | --- | ------- |
| r7a.medium | $0.07608 | 1 | 8 GiB | Up to 12500 Megabit
| t3.medium | $0.0416 | 2 | 4 GiB | Up to 5 Gigabit |
| m7a.medium | $0.05796 | 1 | 4 GiB | Up to 12500 Megabit

## Latest EC2

### Setup Details

AMI Type: Ubuntu Server 24.04 LTS (HVM), SSD Volume Type

AMI ID: `ami-04b70fa74e45c3917`

Architecture: 64-bit (x86)

Instance Type: `r7a.medium`

Root Volume: 8 GiB gp3

EBS Volume: 16 GiB gp3

### Instance Details

Instance ID: `i-06c14e9d86188ac76`

Public IPv4: `18.206.48.178`, `18.206.48.178:25565`

Private IPv4: `172.31.76.21`

Public IPv4 DNS: `ec2-18-206-48-178.compute-1.amazonaws.com`

## Connect to Instance

`ssh -i [Key Location] ubuntu@[Public IPv4 DNS]`

Ex: `ssh -i 'C:\Users\Ben\.ssh\ubuntu_login.pem' ubuntu@ec2-18-206-48-178.compute-1.amazonaws.com`

## Install Java

`sudo apt update && sudo apt upgrade -y`  
`sudo apt install openjdk-[Version]-jre-headless`

Ex: `sudo apt install openjdk-21-jre-headless`

## Set Up Minecraft

`mkdir minecraft && cd minecraft`

`wget -O paper_server_[Version].jar [Link]`

Ex: `wget -O paper_server_1.20.6.jar https://api.papermc.io/v2/projects/paper/versions/1.20.6/builds/85/downloads/paper-1.20.6-85.jar`

Ex: `wget -O minecraft_server_1.20.6.jar https://piston-data.mojang.com/v1/objects/145ff0858209bcfc164859ba735d4199aafa1eea/server.jar`

`screen`

Run: `java -Xms1024M -Xmx[Max RAM]G -jar [Jar File] nogui`

Ex: `java -Xms1024M -Xmx4000M -jar paper_server_1.20.6.jar nogui`

Ex: `java -Xms1024M -Xmx7G -jar paper_server_1.20.6.jar nogui`

## Copying Files / Making Backups

`scp -i [Key Location] -r -p [Source] [Destination]`

Ex. Bring setup files to new server:  `scp -i 'C:\Users\Ben\.ssh\ubuntu_login.pem' -r -p "G:/My Drive/Minecraft/Trunkraft/Server Setup/*" ubuntu@ec2-18-206-48-178.compute-1.amazonaws.com:~/minecraft`

Ex. Bring old backup files to new server: `scp -i 'C:\Users\Ben\.ssh\ubuntu_login.pem' -r -p "G:/My Drive/Minecraft/Trunkraft/Backups/*" ubuntu@ec2-18-206-48-178.compute-1.amazonaws.com:~/minecraft`

Ex. Backup current server: `scp -i 'C:\Users\Ben\.ssh\ubuntu_login.pem' -r -p ubuntu@ec2-18-206-48-178.compute-1.amazonaws.com:~/minecraft/* "B:/Minecraft/Trunkraft/Backups/5_26"`

<!-- Ex: `scp -i 'C:\Users\Ben\.ssh\ubuntu_login.pem' -r -p ubuntu@ec2-52-91-73-231.compute-1.amazonaws.com:~/minecraft/* "G:/My Drive/Minecraft/Trunkraft/Backups/"` -->

## Old Servers

### Summer Trunkraft Mini

#### Setup Details

AMI Type: Ubuntu Server 24.04 LTS (HVM), SSD Volume Type

AMI ID: `ami-04b70fa74e45c3917`

Architecture: 64-bit (x86)

Instance Type: `t3.medium`

Root Volume: 8 GiB gp3

EBS Volume: 16 GiB gp3

#### Instance Details

Instance ID: `i-00ce6e45e01cc1d57`

Public IPv4: `52.91.73.231`, `52.91.73.231:25565`

Private IPv4: `172.31.44.186`

Public IPv4 DNS: `ec2-52-91-73-231.compute-1.amazonaws.com`

### Expensive OG

#### Public IP

`18.234.251.211`, `18.234.251.211:25565`

#### Public IPv4 DNS Name

`ec2-18-234-251-211.compute-1.amazonaws.com`

### New Trunkraft

#### Public IP

`34.207.140.250`, `34.207.140.250:25565`

#### Public IPv4 DNS Name

`ec2-34-207-140-250.compute-1.amazonaws.com`

## Misc

See memory usage: `htop`

### Screen Commands

`screen` to setup screen  
`CTRL + A + D` to detach  
`screen -r` to re-attach
