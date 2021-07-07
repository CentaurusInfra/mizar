from kubernetes import client, config
import time


def daemon_check():
    config.load_incluster_config()
    apps = client.AppsV1Api()
    while True:
        daemon_status = apps.read_namespaced_daemon_set_status('mizar-daemon', 'default')
        if daemon_status.status.number_ready >= 1:
            print('waiting daemon to get ready ...')
            break
        time.sleep(1)


if __name__ == '__main__':
    daemon_check()
