import frappe
import os
from werkzeug.wrappers import Response
from werkzeug.wsgi import wrap_file
from werkzeug.utils import secure_filename
from flashdesk.docker_utils.docker_client import *

@frappe.whitelist()
def insert_image():
    data = frappe.request.get_json()
    doc = frappe.get_doc(
        {
            "doctype": "Pod Image",
            "image_name": data.get("image_name"),
            "image_description": data.get("image_description"),
            "image_file": os.path.basename(data.get("image_file")),
            "image_id": data.get("image_id"),
            "tags": data.get("tags"),
            "status": data.get("status"),
        }
    )
    doc.insert()
    return doc