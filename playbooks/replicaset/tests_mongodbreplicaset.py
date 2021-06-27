import os
import time
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['ANSIBLE_INVENTORY']
).get_hosts('all')

def test_mongodb_config(host):
    file = host.file("/etc/mongod.conf")
    assert file.exists


def test_monbgodb_service(host):
    service = host.service("mongod")
    assert service.is_running
    assert service.is_enabled


def test_mongodb_replicaset(host):
    cmd = host.run("mongo --eval 'db.runCommand({ isMaster: 1 })'")
    assert "mongodb-1.local:27017" in cmd.stdout
    assert "mongodb-2.local:27017" in cmd.stdout
    assert "mongodb-3.local:27017" in cmd.stdout


@pytest.mark.skipif(os.environ.get('MONGO_VERSION', '') == '', reason="MONGO_VERSION environment variable is not set")
def test_mongodb_version(host):
    MONGO_VERSION = os.environ.get('MONGO_VERSION')
    hostname = host.check_output('hostname -s')
    if hostname.startswith("mongodb"):
        cmd = host.run("mongod --version")
        assert MONGO_VERSION in cmd.stdout


@pytest.mark.skipif(os.environ.get('MONGO_REBOOT_TEST', '') != 'TRUE', reason="MONGO_REBOOT_TEST environment variable is not set")
def test_mongodb_reboot(host):
    '''
    Reboot the host and check the mongod service comes back up
    '''
    host.run("sudo reboot")
    time.sleep(60)

    service = host.service("mongod")
    assert service.is_running
    assert service.is_enabled

    socket = host.socket("tcp://0.0.0.0:27017")
    assert socket.is_listening
