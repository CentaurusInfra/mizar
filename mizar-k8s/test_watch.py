from __future__ import print_function
import time
from kubernetes import client, config, watch
from pprint import pprint


config.load_kube_config()
obj_api = client.CustomObjectsApi()


print("Starting stream")
watcher = watch.Watch()
stream = watcher.stream(obj_api.list_namespaced_custom_object,
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			field_selector = "metadata.name=test3-ep",
			watch = True
			)

for event in stream:
	print(event)