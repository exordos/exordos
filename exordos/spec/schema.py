#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import dataclasses
import os
import re
import typing as tp

import rich_click as click
import yaml

from exordos import utils
from exordos.clients import repo
from exordos.common import version as version_lib

REGEXP = re.compile(r"\$(.+?)(?:\:(.+))?$")


@dataclasses.dataclass
class Parsed:
    input_string: str
    valid: bool = True
    error: str | None = None
    resource_type: str | None = None
    element_name: str | None = None
    resource_paths: list[str] | None = None
    resource_name: str | None = None
    value: str | None = None
    is_variable: bool = False
    is_resource: bool = False
    is_resource_type: bool = False
    is_imported: bool = False


def validate_yaml(data: dict, schema: tp.Optional[dict]) -> None:
    try:
        from jsonschema.exceptions import ValidationError
        from jsonschema.exceptions import _WrappedReferencingError
        import openapi_schema_validator

        if data and schema:
            try:
                openapi_schema_validator.validate(
                    data, schema, cls=openapi_schema_validator.OAS30Validator
                )
            except ValidationError as err:
                raise ValueError(f"{err.message} in {err.json_path}")
            except _WrappedReferencingError as err:
                raise ValueError(f"Not found {err.ref} in schema")
    except ModuleNotFoundError:
        pass
    return None


def load_base_manifest_schema() -> dict:
    with open(
        os.path.join(utils.PROJECT_PATH, "exordos", "spec", "base_manifest_spec.yaml"),
        "r",
    ) as f:
        return yaml.safe_load(f)


def update_manifest_schema(base_manifest_schema: dict, user_api_spec: dict) -> dict:
    base_manifest_schema["components"]["schemas"].update(
        user_api_spec.get("components", {}).get("schemas", {})
    )
    for path, path_obj in user_api_spec.get("paths", {}).items():
        path_parts = path.split("/")
        post_path = path_obj.get("post")
        if post_path:
            operation_id = post_path.get("operationId")
            if operation_id and operation_id.startswith("Create_v1"):
                schema_ref = post_path["requestBody"]["content"]["application/json"][
                    "schema"
                ]
                ref = schema_ref.get("$ref")
                if not ref:
                    continue
                refs = ref.split("/")
                if not refs:
                    continue
                model_name = refs[-1]
                api_parts = ".".join(
                    [
                        path_part
                        for path_part in path_parts[2:]
                        if path_part and not path_part.startswith("{")
                    ]
                )
                model = (
                    user_api_spec.get("components", {})
                    .get("schemas", {})
                    .get(model_name)
                )
                if not model:
                    continue
                resource = f"$core.{api_parts}"
                model["path"] = path
                base_manifest_schema["components"]["schemas"][model_name] = model
                base_manifest_schema["properties"]["resources"]["properties"][
                    resource
                ] = {
                    "type": "object",
                    "additionalProperties": schema_ref,
                }
    return base_manifest_schema


def search_parameter_example(
    scheme: dict, resource_type: str, parameter: str
) -> tp.Any:
    resource_type = scheme["properties"]["resources"]["properties"].get(resource_type)
    if not resource_type:
        return None
    ref = resource_type.get("additionalProperties", {}).get("$ref")
    if not ref:
        return None
    model_name = ref.split("/")[-1]
    model = scheme["components"]["schemas"].get(model_name)
    if model:
        model_ref = model.get("$ref")
        if model_ref:
            model_ref_name = model_ref.split("/")[-1]
            model = scheme["components"]["schemas"].get(model_ref_name)
        example = model.get("properties", {}).get(parameter, {}).get("example")
        if example is not None:
            return example
        for prop in model["properties"].values():
            if "oneOf" in prop:
                for oneOf in prop["oneOf"]:
                    example = oneOf["properties"].get(parameter, {}).get("example")
                    if example is not None:
                        return example
    return None


def parse_variable(var: str, manifest: dict) -> Parsed:

    res = re.findall(REGEXP, var)

    result = Parsed(input_string=var)
    if not res or len(res[0]) == 0:
        result.valid = False
        result.error = "Invalid format"
        return result

    parts = res[0][0].split(".")

    if len(parts) <= 1:
        result.valid = False
        result.error = "Invalid format"
        return result

    value, resource_parts, resource_name, resource_type = None, None, None, None
    is_variable, is_resource, is_resource_type, is_imported = False, False, False, False
    element_name = parts[0]

    if len(parts) == 2:
        is_resource_type = True
        resource_parts = parts[1:]
    elif len(parts) == 3:
        if parts[-1].startswith("$"):
            resource_name = parts[-1][1:]
            resource_parts = parts[1:-1]
            is_resource = True
            if parts[1] == "imports":
                is_imported = True
                if resource_name not in manifest.get("imports", {}):
                    result.valid = False
                    result.error = f"Resource {resource_name} not found in imports"
                else:
                    import_var = parse_variable(
                        manifest["imports"][resource_name]["link"], manifest
                    )
                    if import_var.valid:
                        resource_type = import_var.resource_type
                        is_variable = True
                    else:
                        result.valid = False
                        result.error = import_var.error
            else:
                resource_type = f"${element_name}.{'.'.join(resource_parts)}"
        else:
            is_resource_type = True
            resource_parts = parts[1:]
    elif len(parts) > 3:
        if len(res[0]) == 2 and res[0][1]:
            value = res[0][1]

        if parts[-1].startswith("$"):
            resource_name = parts[-1][1:]
            resource_parts = parts[1:-1]
            is_resource = True
            is_variable = True if value else False
            resource_type = f"${element_name}.{'.'.join(resource_parts)}"
        elif value:
            result.valid = False
            result.error = "Not found resource"
            return result
        else:
            is_resource_type = True
            resource_parts = parts[1:]

    result.element_name = element_name
    result.resource_paths = resource_parts
    result.resource_name = resource_name
    result.value = value
    result.is_variable = is_variable
    result.is_resource = is_resource
    result.is_resource_type = is_resource_type
    result.resource_type = resource_type
    result.is_imported = is_imported

    return result


def walk_replace(
    resource_type: str, manifest: dict, scheme: dict, node: tp.Union[dict, list, str]
):
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str):
                parsed_var = parse_variable(value, manifest)
                if parsed_var.valid and parsed_var.is_variable:
                    if parsed_var.resource_type == "$core.vs.variables":
                        example = search_parameter_example(scheme, resource_type, key)
                    else:
                        example = search_parameter_example(
                            scheme, parsed_var.resource_type, parsed_var.value
                        )
                    if example is not None:
                        node[key] = example
            else:
                walk_replace(resource_type, manifest, scheme, value)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, str):
                parsed_var = parse_variable(item, manifest)
                if parsed_var.valid and parsed_var.is_variable:
                    if parsed_var.resource_type == "$core.vs.variables":
                        example = search_parameter_example(scheme, resource_type, item)
                    else:
                        example = search_parameter_example(
                            scheme, parsed_var.resource_type, parsed_var.value
                        )
                    if example is not None:
                        node[i] = example
            else:
                walk_replace(resource_type, manifest, scheme, item)


def remove_middle_parts(input_string):
    parts = input_string.split(".")

    if len(parts) <= 2:
        return input_string

    result_parts = []
    for i, part in enumerate(parts):
        if i > 0 and part.startswith("$"):
            continue
        result_parts.append(part)
    return ".".join(result_parts)


def mutate_resource_types(manifest: dict) -> dict:
    mutated_map = {}
    for resource_type in manifest["resources"].keys():
        mutated_resource_type = remove_middle_parts(resource_type)
        if resource_type != mutated_resource_type:
            mutated_map[mutated_resource_type] = resource_type
    for mutated_resource_type, resource_type in mutated_map.items():
        manifest["resources"][mutated_resource_type] = manifest["resources"].pop(
            resource_type
        )
    return manifest


def mutate_manifest(manifest: dict, scheme: dict) -> dict:
    manifest = mutate_resource_types(manifest)
    for resource_type, resource in manifest["resources"].items():
        for resource_name, resource_value in resource.items():
            walk_replace(resource_type, manifest, scheme, resource_value)
    return manifest


def validate_manifest(manifest: dict, repository_url: str) -> None:
    manifest_schema = load_base_manifest_schema()
    validate_yaml(manifest, manifest_schema)
    if not manifest.get("resources"):
        return
    if not manifest.get("requirements"):
        return
    need_full_validate = False
    repository = repo.Repository(repository_url)
    for req_element_name, req_spec in manifest.get("requirements", {}).items():
        try:
            versions = repository.get_versions(
                req_element_name,
                skip_latest=True,
                stable=True,
            )
            element_version = version_lib.get_target_version(versions, req_spec)
            user_api_spec = repository.openapi_spec(req_element_name, element_version)
            if user_api_spec:
                need_full_validate = True
                manifest_schema = update_manifest_schema(manifest_schema, user_api_spec)
        except Exception as e:
            click.secho(
                f"Error getting user api spec for {req_element_name}: {e}", fg="red"
            )
            return
    if need_full_validate:
        mutated_manifest = mutate_manifest(manifest, manifest_schema)
        validate_yaml(mutated_manifest, manifest_schema)
