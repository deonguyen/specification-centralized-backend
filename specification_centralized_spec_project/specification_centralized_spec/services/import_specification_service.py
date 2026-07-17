import json

from bs4 import BeautifulSoup
from django.db.models import Q
from specification_centralized_core.models.component_model import ComponentModel
from specification_centralized_core.models.jama_item_type_model import JamaItemTypeModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.services import ai_service, github_service, wovey_api_service
from specification_centralized_spec.services import specification_service
from specification_centralized_spec.services.extract_item_types import extract_item_type_fields
from specification_centralized_spec.services.google_drive_service import (
    initialize_google_drive_service,
    list_google_drive_files,
)
from rest_framework import status
import base64
import markdown
import os
import re
from py_jama_rest_client.client import JamaClient

def recursive_spec_structure_into_database(project, tree_data, current_version, user):
    root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
        project=project,
        category1="root",
        category2="root",
        defaults={"specification_order": 0},
    )

    tree_data.sort(key=lambda x: x.get("path", "").count("/"))
    created_count = 0

    all_components = list(ComponentModel.objects.all())
    uncategorized_component = ComponentModel.objects.filter(code="Uncategorized").first()
    for item in tree_data:
        path = item.get("path", "")
        item_type = item.get("type", "")
        file_id = item.get("id")

        parts = path.split("/")
        name = parts[-1]

        current_parent = root_spec
        current_path = ""

        component = uncategorized_component
        for comp in all_components:
            if comp.code.lower() in path.lower():
                component = comp
                break

        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            current_path = os.path.join(current_path, part).replace(os.sep, "/")

            req_id = None
            spec_content = None
            interface_content = None
            sub_spec_content = []
            raw_content = None

            if current_path.endswith(".md"):
                req_id = item.get("req_id")
                spec_content = item.get("parsed_spec_content")
                interface_content = item.get("interface_content")
                sub_spec_content = item.get("sub_spec_content")
                raw_content = item.get("raw_content")

            spec_obj, spec_created = SpecificationModel.objects.update_or_create(
                project=project,
                name=part.lower(),
                code=part.lower(),
                local_file_path=current_path,
                defaults={
                    "content": spec_content,
                    "raw_content": raw_content,
                    "interface": interface_content,
                    "internal_id": req_id,
                    "local_file_fullpath": None,
                    "source": "Local",
                    "status": "draft",
                    "type": "Specification" if is_last else "Folder",
                    "version": current_version,
                },
            )

            previous_version_revision = SpecificationRevisionModel.objects.filter(
                ~Q(version=current_version), specification=spec_obj
            ).first()
            previous_version = (
                previous_version_revision.version if previous_version_revision else ""
            )

            change_summary = ""
            if is_last:
                if not previous_version or previous_version == "":
                    change_summary = "Content created"
                else:
                    current_content = raw_content
                    previous_content = ""

                    if (
                        previous_version_revision
                        and previous_version_revision.local_file_path
                    ):
                        previous_content = previous_version_revision.content or ""

                    if previous_content == "" and current_content != "":
                        change_summary = "Content updated, no previous content"
                    elif current_content == previous_content:
                        change_summary = "No changes detected"
                    else:
                        # change_summary = "CALL TO AI TO COMPARE CHANGES"
                        change_summary = wovey_api_service.compare_diff_summary(
                            previous_content, current_content
                        )[0]

            project_spec_revision, _ = (
                SpecificationRevisionModel.objects.update_or_create(
                    specification=spec_obj,
                    version=current_version,
                    project=project,
                    defaults={
                        "updated_by": user,
                        "previous_version": previous_version,
                        "change_summary": change_summary,
                        "local_file_path": current_path,
                        "local_file_fullpath": None,
                        "content": spec_content,
                        "raw_content": raw_content,
                    },
                )
            )

            current_project_spec, project_spec_created = (
                ProjectSpecificationModel.objects.update_or_create(
                    project=project,
                    specification=spec_obj,
                    defaults={
                        "component": component,
                        "parent": current_parent,
                        "category1": "",
                        "category2": "",
                        "specification_revision": project_spec_revision,
                    },
                )
            )

            current_parent = current_project_spec

            if project_spec_created:
                created_count += 1

            try:
                for sub_spec in sub_spec_content:
                    sub_header_text = sub_spec["header"]["text"]

                    sub_spec_obj, sub_spec_created = (
                        SpecificationModel.objects.update_or_create(
                            name=sub_header_text.lower(),
                            code=sub_header_text.lower(),
                            local_file_path=current_path,
                            project=project,
                            defaults={
                                "content": sub_spec["content"],
                                "source": "Local",
                                "status": "draft",
                                "type": "Sub Specification",
                                "version": current_version,
                                "local_file_fullpath": None,
                                "internal_id": sub_header_text.lower(),
                            },
                        )
                    )

                    sub_previous_version_revision = (
                        SpecificationRevisionModel.objects.filter(
                            ~Q(version=current_version), specification=sub_spec_obj
                        ).first()
                    )
                    sub_previous_version = (
                        sub_previous_version_revision.version
                        if sub_previous_version_revision
                        else ""
                    )

                    change_summary = ""
                    if not sub_previous_version or sub_previous_version == "":
                        change_summary = "Content created"
                    else:
                        sub_current_content = sub_spec["content"]
                        sub_previous_content = sub_previous_version_revision.content

                        if sub_previous_content == "" and sub_current_content != "":
                            change_summary = "Content updated, no previous content"
                        elif sub_current_content == sub_previous_content:
                            change_summary = "No changes detected"
                        else:
                            # change_summary = "CALL TO AI TO COMPARE CHANGES"
                            change_summary = wovey_api_service.compare_diff_summary(
                                previous_content, current_content
                            )[0]

                    sub_project_spec_revision, _ = (
                        SpecificationRevisionModel.objects.update_or_create(
                            specification=sub_spec_obj,
                            version=current_version,
                            project=project,
                            defaults={
                                "updated_by": user,
                                "previous_version": sub_previous_version,
                                "change_summary": change_summary,
                                "local_file_path": current_path.replace(os.sep, "/"),
                                "content": sub_spec["content"],
                            },
                        )
                    )

                    _, sub_project_spec_created = (
                        ProjectSpecificationModel.objects.update_or_create(
                            project=project,
                            specification=sub_spec_obj,
                            defaults={
                                "component": component,
                                "parent": current_project_spec,
                                "category1": "",
                                "category2": "",
                                "specification_revision": sub_project_spec_revision,
                            },
                        )
                    )

                    if sub_project_spec_created:
                        created_count += 1
            except Exception as e:
                import traceback

                print(f"Exception processing sub-specifications: {e}")
                traceback.print_exc()

        print(
            f"Processed {current_path} (type: {item_type}, created: {project_spec_created})"
        )

    return created_count


def process_import_specification_from_local(
    project, full_path: str, base_dir: str, current_version: str, user
):
    """
    Recursively parses local files and syncs them to project specifications.
    """
    # Software Requirement Document (SwRD) files are expected to be under a folder named "swrd" (case-insensitive) in the provided path.
    # This is to ensure that only relevant specification files are processed, while ignoring other files that may be present in the directory structure. The code will recursively walk through the directory structure starting from the provided full_path, and only process .md files that are located within any folder named "swrd".
    swrd_folder = "swrd"
    tree_data = []

    try:
        for root, dirs, files in os.walk(full_path):
            if swrd_folder not in root.lower():
                continue
            for name in files:
                if name.endswith(".md"):
                    f_path = os.path.join(root, name)
                    rel_path = os.path.relpath(f_path, base_dir).replace(os.sep, "/")
                    try:
                        with open(f_path, "r", encoding="utf-8") as file:
                            raw_content = file.read()
                            (
                                req_id,
                                interface_content,
                                parsed_spec_content,
                                sub_spec_content,
                            ) = specification_service.parse_specification_content(
                                raw_content
                            )
                        if req_id:
                            tree_data.append(
                                {
                                    "path": rel_path,
                                    "type": "blob",
                                    "id": f_path,
                                    "name": name,
                                    "raw_content": raw_content,
                                    "req_id": req_id,
                                    "interface_content": interface_content,
                                    "parsed_spec_content": parsed_spec_content,
                                    "sub_spec_content": sub_spec_content,
                                }
                            )
                    except Exception as e:
                        print(f"Error reading local file {f_path}: {e}")
    except Exception as err:
        print(f"Error walking directory {full_path}: {err}")
        pass

    created_count = recursive_spec_structure_into_database(
        project, tree_data, current_version, user
    )

    return created_count


def process_import_specification_from_google_drive(
    project, folder_id, current_version, user
):
    try:
        service = initialize_google_drive_service()

        tree_data = list_google_drive_files(service, folder_id)

        created_count = recursive_spec_structure_into_database(
            project, tree_data, current_version, user
        )

        return created_count
    except Exception as e:
        import traceback

        print(f"Exception in process_import_specification_from_google_drive: {e}")
        traceback.print_exc()
        raise e


def process_import_specification_from_github(
    branch, github_token, owner, project, repo, user, version
):
    root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
        project=project,
        category1="root",
        category2="root",
        defaults={"specification_order": 0},
    )

    latest_commit_sha = None
    previous_commit_sha = None

    last_two_commits_response = github_service.last_two_commits(
        branch, github_token, owner, project, repo, user, version
    )
    if last_two_commits_response.status_code == status.HTTP_200_OK:
        commits = last_two_commits_response.data
        if len(commits) > 0:
            latest_commit_sha = commits[0].get("sha")
        if len(commits) > 1:
            previous_commit_sha = commits[1].get("sha")

    tree_response = github_service.tree(
        branch, github_token, owner, project, repo, user, version
    )
    if tree_response.status_code != 200:
        return tree_response

    tree_data = tree_response.data.get("tree", [])
    tree_data.sort(key=lambda x: x.get("path", "").count("/"))

    path_to_spec = {"": root_spec}
    created_count = 0

    all_components = list(ComponentModel.objects.all())
    uncategorized_component = ComponentModel.objects.filter(code="Uncategorized").first()
    for item in tree_data:
        path = item.get("path", "")
        item_type = item.get("type", "")

        if not path or path.endswith("README.md"):
            continue

        component = uncategorized_component
        for comp in all_components:
            if comp.code.lower() in path.lower():
                component = comp
                break

        change_summary = ""
        raw_content = ""
        req_id = None
        interface_content = None
        sub_spec_content = []
        has_spec_header = False

        if item_type == "blob" and latest_commit_sha and previous_commit_sha:
            previous_content = github_service.get_file_content_base64(
                branch=branch,
                github_token=github_token,
                owner=owner,
                path=path,
                project=project,
                ref=previous_commit_sha,
                repo=repo,
                user=user,
                version=version,
            )
            latest_content = github_service.get_file_content_base64(
                branch=branch,
                github_token=github_token,
                owner=owner,
                path=path,
                project=project,
                ref=latest_commit_sha,
                repo=repo,
                user=user,
                version=version,
            )
            if latest_content is None and previous_content is None:
                pass
            elif latest_content is not None and previous_content is None:
                change_summary = "Add new document content"
            elif latest_content != previous_content:
                change_summary = ai_service.get_diff_summary(
                    previous_content, latest_content
                )

            if latest_content:
                try:
                    raw_content = base64.b64decode(latest_content).decode("utf-8")
                    html = markdown.markdown(raw_content)
                    soup = BeautifulSoup(html, "html.parser")
                    spec_header = soup.find(
                        ["h1", "h2", "h3", "h4", "h5", "h6"],
                        string=re.compile(r"Specification", re.I),
                    )
                    if spec_header:
                        has_spec_header = True
                        (
                            req_id,
                            interface_content,
                            parsed_spec_content,
                            sub_spec_content,
                        ) = specification_service.parse_specification_content(
                            raw_content
                        )
                except Exception:
                    pass

        if item_type == "blob" and not has_spec_header:
            continue

        parts = path.split("/")
        name = parts[-1]
        parent_path = "/".join(parts[:-1])
        parent_spec = path_to_spec.get(parent_path, root_spec)

        spec_obj, _ = SpecificationModel.objects.update_or_create(
            name=name,
            code=name,
            project=project,
            defaults={
                "content": raw_content if raw_content else None,
                "interface": interface_content,
                "internal_id": req_id,
                "source": "GitHub",
                "status": "draft",
                "type": (
                    "Specification"
                    if item_type == "blob"
                    else ("Folder" if item_type == "tree" else item_type)
                ),
            },
        )

        spec_revision_obj, _ = SpecificationRevisionModel.objects.update_or_create(
            project=project,
            specification=spec_obj,
            version=latest_commit_sha or "",
            defaults={
                "updated_by": user,
                "previous_version": previous_commit_sha or "",
                "change_summary": change_summary,
                "content": raw_content if raw_content else None,
            },
        )

        spec, created = ProjectSpecificationModel.objects.update_or_create(
            project=project,
            specification=spec_obj,
            defaults={
                "component": component,
                "parent": parent_spec,
                "specification_revision": spec_revision_obj,
                "category1": "",
                "category2": "",
            },
        )

        if created:
            created_count += 1

        if item_type == "tree":
            path_to_spec[path] = spec

    return created_count


def process_import_specification_from_jama(
    project, jama_url, jama_project_id, version, client_id, client_secret, user
):
    client = JamaClient(
        host_domain=jama_url,
        credentials=(client_id, client_secret),
        oauth=True,
    )

    # item_types = client.get_item_types()

    # for item_type in item_types:
    #     JamaItemTypeModel.objects.update_or_create(
    #         id=item_type.get("id"),
    #         type_key=item_type.get("typeKey"),
    #         display=item_type.get("display"),
    #     )
    #     print(f"Process {item_type}")
    
    items = client.get_items(jama_project_id)
    
    created_count = 0

    jama_id_to_spec_map = {}
    root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
        project=project,
        category1="root",
        category2="root",
        defaults={"specification_order": 0},
    )

    all_components = list(ComponentModel.objects.all())
    uncategorized_component = ComponentModel.objects.filter(code="Uncategorized").first()

    # Sort items by sequence to process parents before children
    items.sort(key=lambda x: x.get("location", {}).get("sequence", ""))

    for item in items:
        jama_id = item.get("id", "")

        item_fields = item.get("fields", {})
        document_key = item_fields.get("documentKey", "")
        global_id = item_fields.get("globalId", "")
        spec_name = item_fields.get("name", "")
        raw_content = item_fields.get("description", "")

        item_version = item.get("version", "")

        item_location = item.get("location", {})
        location_parent = item_location.get("parent", {})
        parent_id = location_parent.get("item", "")
        
        relationship = client.get_relationship(jama_id)
        print(f"Relation ship {relationship}")
        
        if "SWRD" not in spec_name or raw_content is "":
            continue
        
        (
            interface_content,
            parsed_spec_content,
            sub_spec_content,
        ) = specification_service.parse_jama_specification_content(raw_content)

        component = uncategorized_component
        for comp in all_components:
            if comp.code.lower() in spec_name.lower():
                component = comp
                break

        spec_obj, spec_created = SpecificationModel.objects.update_or_create(
            name=spec_name,
            code=document_key,
            project=project,
            defaults={             
                "content": parsed_spec_content,
                "raw_content": raw_content,
                "interface": interface_content,
                "internal_id": global_id,
                "source": "Jama",
                "status": "draft",
                "type": "Specification",
                #"version": item_version,
                "version": version,
            },
        )

        previous_version_revision = (
            SpecificationRevisionModel.objects.filter(
                ~Q(version=item_version), specification=spec_obj
            )
            .order_by("-change_date")
            .first()
        )
        previous_version = (
            previous_version_revision.version if previous_version_revision else ""
        )
        previous_content = (
            previous_version_revision.raw_content if previous_version_revision else ""
        )

        change_summary = ""
        if not previous_version:
            change_summary = "Content created"
        elif raw_content == previous_content:
            change_summary = "No changes detected"
        else:
            summary_tuple = wovey_api_service.compare_diff_summary(
                previous_content, raw_content
            )
            change_summary = summary_tuple[0] if summary_tuple else "Error generating summary"

        spec_revision_obj, _ = SpecificationRevisionModel.objects.update_or_create(
            project=project,
            specification=spec_obj,
            version=item_version or "",
            defaults={
                "updated_by": user,
                "previous_version": previous_version or "",
                "change_summary": change_summary,
                "content": raw_content if raw_content else None,
            },
        )

        parent_spec = root_spec
        if parent_id and parent_id in jama_id_to_spec_map:
            parent_spec = jama_id_to_spec_map[parent_id]

        spec, created = ProjectSpecificationModel.objects.update_or_create(
            project=project,
            specification=spec_obj,
            defaults={
                "component": component,
                "parent": parent_spec,
                "specification_revision": spec_revision_obj,
                "category1": "",
                "category2": "",
            },
        )
        jama_id_to_spec_map[jama_id] = spec

        if created:
            created_count += 1

        for sub_spec in sub_spec_content:
            sub_header_text = sub_spec["header"]["text"]
            sub_content = sub_spec["content"]

            sub_spec_obj, sub_spec_created = SpecificationModel.objects.update_or_create(
                name=sub_header_text.lower(),
                code=sub_header_text.lower(),
                project=project,
                defaults={    
                    "internal_id": global_id,
                    "content": sub_content,
                    "source": "Jama",
                    "status": "draft",
                    "type": "Sub Specification",
                    #"version": item_version,
                    "version": version,
                },
            )

            sub_previous_revision = (
                SpecificationRevisionModel.objects.filter(
                    ~Q(version=item_version), specification=sub_spec_obj
                )
                .order_by("-change_date")
                .first()
            )
            sub_previous_version = (
                sub_previous_revision.version if sub_previous_revision else ""
            )

            sub_revision_obj, _ = SpecificationRevisionModel.objects.update_or_create(
                specification=sub_spec_obj,
                version=item_version,
                project=project,
                defaults={
                    "updated_by": user,
                    "previous_version": sub_previous_version,
                    "content": sub_content,
                    "change_summary": change_summary,
                },
            )

            sub_project_spec, sub_created = ProjectSpecificationModel.objects.update_or_create(
                project=project,
                specification=sub_spec_obj,
                defaults={
                    "component": component,
                    "parent": spec,
                    "specification_revision": spec_revision_obj,
                    "category1": "",
                    "category2": "",
                },
            )

            if sub_created:
                created_count += 1

    return created_count
