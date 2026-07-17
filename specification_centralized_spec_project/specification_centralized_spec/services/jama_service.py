from py_jama_rest_client.client import JamaClient
import json
import os
import time

# 1. Initialize your client
# For OAuth authentication:
client = JamaClient(
    host_domain="https://stargate.jamacloud.com/",
    credentials=("vz8jngyfekaygcy", "18ao6z4p2lq0hzlvlezr7jnqt"),
    oauth=True,
)


def get_items_by_project(client, project_id):
    # Alternatively, for Basic authentication:
    # client = JamaClient("https://yourdomain.jamacloud.com", credentials=("username", "password"))

    # 2. Define the project ID you want to fetch items from
    # project_id = 368

    # 3. Fetch all items (the SDK automatically handles pagination internally)
    items = client.get_items(project_id)

    # 4. Print or process your items
    output_file = "up_down_stream_result.json"

    existing = []
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing = json.load(f)

    for item in items:
        # print(f"ID: {item.get('id')} | Name: {item.get('fields', {}).get('name')}")
        # existing.append(item)
        items_upstream_relationships = client.get_items_upstream_relationships(item.get("id"))
        for up in items_upstream_relationships:
            existing.append(up)
            time.sleep(5)
        items_downstream_relationships = client.get_items_downstream_relationships(item.get("id"))
        for down in items_downstream_relationships:
            existing.append(down)
            time.sleep(5)

    with open(output_file, "w") as f:
        json.dump(existing, f, indent=2)


def get_items_version(client, item_id):
    # Alternatively, for Basic authentication:
    # client = JamaClient("https://yourdomain.jamacloud.com", credentials=("username", "password"))

    # 2. Set your target item ID
    # item_id = 12345

    # 3. Retrieve all versions of the item
    versions = client.get_item_versions(item_id)
    # 4. Print or process your items
    output_file = "version_result.json"

    existing = []
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing = json.load(f)

    for version in versions:
        print(f"Version Number: {version.get('versionNumber')}")
        print(f"Created By: {version.get('createdBy')}")
        print(f"Date Modified: {version.get('lastModifiedDate')}")
        print("-" * 20)
        existing.append(version)

    with open(output_file, "w") as f:
        json.dump(existing, f, indent=2)


def get_items_version(client, item_id):
    # Alternatively, for Basic authentication:
    # client = JamaClient("https://yourdomain.jamacloud.com", credentials=("username", "password"))

    # 2. Set your target item ID
    # item_id = 12345

    # 3. Retrieve all versions of the item
    versions = client.get_item_versions(item_id)
    # 4. Print or process your items
    output_file = "version_result.json"

    existing = []
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing = json.load(f)

    for version in versions:
        print(f"Version Number: {version.get('versionNumber')}")
        print(f"Created By: {version.get('createdBy')}")
        print(f"Date Modified: {version.get('lastModifiedDate')}")
        print("-" * 20)
        existing.append(version)

    with open(output_file, "w") as f:
        json.dump(existing, f, indent=2)

def get_relationship_types():
    # Alternatively, for Basic authentication:
    # client = JamaClient("https://yourdomain.jamacloud.com", credentials=("username", "password"))

    # 2. Define the project ID you want to fetch items from
    # project_id = 368

    # 3. Fetch all items (the SDK automatically handles pagination internally)
    items = client.get_relationship_types()

    # 4. Print or process your items
    output_file = "relationship_types_result.json"

    existing = []
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing = json.load(f)

    for item in items:
        print(f"item: {item}")
        existing.append(item)

    with open(output_file, "w") as f:
        json.dump(existing, f, indent=2)

# def get_relationship_types():
#     # Alternatively, for Basic authentication:
#     # client = JamaClient("https://yourdomain.jamacloud.com", credentials=("username", "password"))

#     # 2. Define the project ID you want to fetch items from
#     # project_id = 368

#     # 3. Fetch all items (the SDK automatically handles pagination internally)
#     items = client.get_relationship_types()

#     # 4. Print or process your items
#     output_file = "relationship_bata_by_type_result.json"

#     existing = []
#     if os.path.exists(output_file):
#         with open(output_file, "r") as f:
#             existing = json.load(f)

#     for item in items:
#         try:
#             relationship_items = client.get_relationship(item.get("id"))
#             for relationship_item in relationship_items:
#                 print(f"relationship item: {relationship_item}")
#                 existing.append(relationship_item)
#         except:
#             continue
#     with open(output_file, "w") as f:
#         json.dump(existing, f, indent=2)

def extract_component():

def main():
    get_items_by_project(client,368)

if __name__ == "__main__":
    main()
