#!/usr/bin/python3
"""
Fabric script (based on the file 2-do_deploy_web_static.py) that creates
and distributes an archive to your web servers, using the function deploy
"""
from fabric.api import *
from datetime import datetime
import os


env.hosts = ['52.91.125.119', '52.86.30.214']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'


def do_pack():
    """Function to compress directory
    Return archive path on success; None on fail
    """
    # Set up datetime
    now = datetime.now()
    now = now.strftime('%Y%m%d%H%M%S')
    archive_path = 'versions/web_static_' + now + '.tgz'

    # Create archive
    local('mkdir -p versions/')
    result = local('tar -cvzf {} web_static/'.format(archive_path))

    # Check if archiving was successful
    if result.succeeded:
        return archive_path
    return None


def do_deploy(archive_path):
    """
    creates and distributes an archive to your web servers
    """
    try:
        # Check if file path exists
        if not (os.path.exists(archive_path)):
            return False

        # upload archive to web server tmp directory
        put(archive_path, '/tmp/')

        # target directory
        target = archive_path[-18:-4]
        run('sudo mkdir -p /data/web_static/\
releases/web_static_{}/'.format(target))

        # uncompress archive and delete .tgz
        run('sudo tar -xzf /tmp/web_static_{}.tgz -C \
/data/web_static/releases/web_static_{}/'
            .format(target, target))

        # delete archive from web server
        run('sudo rm /tmp/web_static_{}.tgz'.format(target))

        # move files to web_static
        run('sudo mv /data/web_static/releases/web_static_{}/web_static/* \
/data/web_static/releases/web_static_{}/'.format(target, target))

        # remove cached data
        run('sudo rm -rf /data/web_static/releases/\
web_static_{}/web_static'.format(target))

        # delete pre-existing sym link
        run('sudo rm -rf /data/web_static/current')

        # create new symbolic link
        run('sudo ln -s /data/web_static/releases/\
web_static_{}/ /data/web_static/current'.format(target))
    except FileNotFoundError:
        return False

    # if all ops are don correctly
    return True


def deploy():
    """
    Deploy web static
    """
    archive_path = do_pack()
    if archive_path is None:
        return False
    success = do_deploy(archive_path)
    return success


def do_clean(number=0):
    """
    Deletes out of date archives
    """
    if number == 0:
        number = 1
    with cd.local('./versions'):
        local("ls -lt | tail -n +{} | rev | cut -f1 -d" " | rev | \
            xargs -d '\n' rm".format(1 + number))
    with cd('/data/web_static/releases/'):
        run("ls -lt | tail -n +{} | rev | cut -f1 -d" " | rev | \
            xargs -d '\n' rm".format(1 + number))
