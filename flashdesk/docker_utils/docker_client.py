import docker
import socket
import json
from datetime import datetime
import humanize

# import frappe

client = docker.from_env()

DOCKER_EXISTS = False

def find_available_ports(num_ports, starting_port=49152, ending_port=65535):
    reserved_ports = [22, 80, 443, 3306]  #List of reserved ports
    
    available_ports = []
    current_port = starting_port

    while len(available_ports) < num_ports and current_port <= ending_port:
        if current_port not in reserved_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", current_port))
                    available_ports.append(current_port)
                except:
                    pass
        current_port += 1

    return available_ports


def check_if_docker_exists():
    global DOCKER_EXISTS
    if bool(client.version()):
        DOCKER_EXISTS = True
        return DOCKER_EXISTS
    else:
        return DOCKER_EXISTS


def start_container_using_image_id(image_id):
    available_ports = find_available_ports(2)
    container = client.containers.run(
        image=image_id, detach=True, ports={"5901":available_ports[0], "6901":available_ports[1]}
    )
    metadata = {
        "container_short_id" : container.short_id,
        "available_ports" : available_ports,
        "vnc_port" : available_ports[1],
    }
    return metadata

def kill_container_using_container_id(container_id):
    client.containers.get(container_id).kill()


def get_all_filesystem_docker_images():
    try:
        images = client.images.list()
        image_list = []
        for image in images:
            image_info = {
                "image_id": image.id,
                "short_id": image.short_id,
                "labels": image.labels,
                "tags": image.tags,
                "created": image.attrs["Created"],
                "size": humanize.naturalsize(image.attrs["Size"]),
                "architecture": image.attrs["Architecture"],
                "os": image.attrs["Os"],
            }
            image_list.append(image_info)
        return image_list
    except docker.errors.APIError as e:
        print("Error:", e)
        return []


def get_all_actively_running_docker_images():
    try:
        containers = client.containers.list()
        running_containers = []
        for container in containers:
            running_container = {
                "container_id": container.id,
                "container_image_tags" :container.image.tags,
                "container_name": container.name,
                "container_labels": container.labels,
                "container_shortid": container.short_id,
                "container_status": container.status,
            }
            running_containers.append(running_container)
        return running_containers
    except docker.errors.APIError as e:
        print("Error:", e)
        return []

def docker_search(query):
    try:
        search_results = client.images.search(query)
        return search_results
    except docker.errors.DockerException as e:
        print("Error:", e)
        return []


# @frappe.whitelist()
# def pull_container_from_hub(container_id):
#     resp = client.api.pull(container_id, stream=True, decode=True, all_tags=True)
#     for line in resp:
#         frappe.publish_realtime("event_name", data={"key": "value"})
#     return "done"
