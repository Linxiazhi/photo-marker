# coding:utf8
from fabric.api import *
import os
import platform

# 登录用户和主机名：
env.user = 'root'
env.password = 'AIMarker@2018'
env.hosts = ['139.224.235.63']# 如果有多个主机，fabric会自动依次部署

_TAR_FILE = 'AIMarker.tar.gz'
_PROJECT = 'aimarker'
_REMOTE_PROJECT_DIR = '/var/www/%s' % _PROJECT


# 获取当前路径
def _current_path():
    return os.path.abspath('.')


def pack():
    includes = ['app', 'aimarker', 'pip.conf', 'requirements.txt', '*.py']
    excludes = ['migrations', 'venv', '.*', '*.pyc', '*.pyo', 'fabfile.py']
    if platform.system() == 'Windows':
        with lcd(_current_path()):
            if os.path.exists(_TAR_FILE):
                local('DEL %s' % _TAR_FILE)
            cmd = ['tar', '--dereference', '-czvf', './%s' % _TAR_FILE]
            cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
            cmd.extend(includes)
            local(' '.join(cmd))
    else:
        if os.path.exists(_TAR_FILE):
            local('rm -f /%s' % _TAR_FILE)
        with lcd(_current_path()):
            cmd = ['tar', '--dereference', '-czvf', './%s' % _TAR_FILE]
            cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
            cmd.extend(includes)
            local(' '.join(cmd))


def deploy():
    # 远程服务器的临时文件：
    remote_tmp_tar = '%s/%s' % (_REMOTE_PROJECT_DIR, _TAR_FILE)
    # 上传tar文件至远程服务器：
    put(_TAR_FILE, remote_tmp_tar)
    # 解压：
    with cd(_REMOTE_PROJECT_DIR):
        run('tar -xzvf %s' % remote_tmp_tar)
        run('supervisorctl restart aimarker')

# 初始化
def init():
    with cd(_REMOTE_PROJECT_DIR):
        run('source venv/bin/activate && pip install -r requirements.txt')
        run('source venv/bin/activate && python manage.py db init')

# 迁移数据库
def migrate_mysql():
    with cd(_REMOTE_PROJECT_DIR):
        run('source venv/bin/activate && python manage.py db migrate')
        run('source venv/bin/activate && python manage.py db upgrade')
