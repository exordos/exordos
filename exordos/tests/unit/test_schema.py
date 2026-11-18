#    Copyright 2026 Genesis Corporation.
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

import typing as tp

import pytest

from exordos.spec import schema


def make_scheme(model: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
    return {
        "properties": {
            "resources": {
                "properties": {
                    "$core.nodes": {
                        "additionalProperties": {
                            "$ref": "#/components/schemas/Node",
                        },
                    },
                },
            },
        },
        "components": {"schemas": {"Node": model}},
    }


class TestSearchParameterExample:
    def test_search_parameter_example_direct_property(self) -> None:
        scheme = make_scheme({"properties": {"uuid": {"example": "node-uuid"}}})

        assert (
            schema.search_parameter_example(scheme, "$core.nodes", "uuid")
            == "node-uuid"
        )

    def test_search_parameter_example_one_of_with_properties(self) -> None:
        scheme = make_scheme(
            {
                "properties": {
                    "spec": {
                        "oneOf": [
                            {"properties": {"uuid": {"example": "node-uuid"}}},
                        ],
                    },
                },
            }
        )

        assert (
            schema.search_parameter_example(scheme, "$core.nodes", "uuid")
            == "node-uuid"
        )

    def test_search_parameter_example_one_of_with_ref(self) -> None:
        scheme = make_scheme(
            {
                "properties": {
                    "spec": {"oneOf": [{"$ref": "#/components/schemas/Spec"}]},
                },
            }
        )
        scheme["components"]["schemas"]["Spec"] = {
            "properties": {"uuid": {"example": "node-uuid"}},
        }

        assert (
            schema.search_parameter_example(scheme, "$core.nodes", "uuid")
            == "node-uuid"
        )

    def test_search_parameter_example_one_of_without_properties(self) -> None:
        scheme = make_scheme(
            {
                "properties": {
                    "spec": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                },
            }
        )

        assert schema.search_parameter_example(scheme, "$core.nodes", "uuid") is None

    def test_search_parameter_example_model_without_properties(self) -> None:
        scheme = make_scheme({"type": "object"})

        assert schema.search_parameter_example(scheme, "$core.nodes", "uuid") is None

    @pytest.mark.parametrize(
        "field,path",
        [
            ({"properties": {"value": {"example": "nested"}}}, ("spec", "value")),
            (
                {"type": "array", "items": {"example": "nested"}},
                ("spec", 0),
            ),
            (
                {"oneOf": [{"$ref": "#/components/schemas/Spec"}]},
                ("spec", "value"),
            ),
        ],
    )
    def test_search_parameter_example_nested_path(self, field, path) -> None:
        scheme = make_scheme({"properties": {"spec": field}})
        scheme["components"]["schemas"]["Spec"] = {
            "properties": {"value": {"example": "nested"}},
        }

        assert (
            schema.search_parameter_example(scheme, "$core.nodes", "value", path)
            == "nested"
        )


class TestMutateManifest:
    def test_mutate_manifest_nested_callback_variable(self) -> None:
        scheme = make_scheme(
            {
                "type": "object",
                "properties": {
                    "callback": {
                        "type": "object",
                        "example": {"key": "value"},
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string",
                                        "enum": ["callback_uri"],
                                    },
                                    "callback": {
                                        "type": "string",
                                        "example": "any_string",
                                    },
                                },
                            },
                        ],
                    },
                },
            }
        )
        manifest = {
            "resources": {
                "$core.nodes": {
                    "grafana_idp": {
                        "callback": {
                            "kind": "callback_uri",
                            "callback": 'f"{$core.vs.variables.$var_grafana_root_url:value}/login/generic_oauth"',
                        },
                    },
                },
            },
        }

        mutated = schema.mutate_manifest(manifest, scheme)

        assert mutated["resources"]["$core.nodes"]["grafana_idp"]["callback"] == {
            "kind": "callback_uri",
            "callback": "any_string/login/generic_oauth",
        }
        schema.validate_yaml(mutated, scheme)


@pytest.mark.parametrize("in_list", [False, True])
@pytest.mark.parametrize(
    "url",
    [
        'f"https://{$core.vs.variables.$oidc_ui_domain:value}"',
        'f"https://{$core.nodes.$node:name}/{$core.nodes.$node:uuid}"',
    ],
)
def test_mutate_manifest_interpolated_redirect_url(in_list, url) -> None:
    expected = (
        "https://example.com/path" if "$core.nodes" in url else "https://example.com"
    )
    url_schema = {
        "type": "string",
        "pattern": "^https://[a-z.]+(?:/path)?$",
        "example": expected,
    }
    action_schema = {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["redirect"]},
            "url": ({"type": "array", "items": url_schema} if in_list else url_schema),
            "code": {"type": "integer", "minimum": 300, "maximum": 399},
        },
    }
    scheme = make_scheme(
        {
            "properties": {
                "condition": {
                    "oneOf": [
                        {
                            "properties": {
                                "actions": {"type": "array", "items": action_schema},
                            },
                        }
                    ],
                },
            },
        }
    )
    action = {"kind": "redirect", "url": [url] if in_list else url, "code": 301}
    manifest = {
        "resources": {
            "$core.nodes": {
                "redirect": {"condition": {"actions": [action]}},
            }
        }
    }

    with pytest.raises(ValueError):
        schema.validate_yaml(manifest, scheme)
    schema.mutate_manifest(manifest, scheme)

    assert action["url"] == ([expected] if in_list else expected)
    schema.validate_yaml(manifest, scheme)
    action["code"] = 400
    with pytest.raises(ValueError):
        schema.validate_yaml(manifest, scheme)


def test_mutate_manifest_literal_invalid_url() -> None:
    scheme = make_scheme(
        {
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": "^https://",
                    "example": "https://example.com",
                }
            }
        }
    )
    manifest = {"resources": {"$core.nodes": {"redirect": {"url": "invalid"}}}}

    schema.mutate_manifest(manifest, scheme)

    with pytest.raises(ValueError):
        schema.validate_yaml(manifest, scheme)


@pytest.mark.parametrize("in_list", [False, True])
@pytest.mark.parametrize(
    "value,field",
    [
        ('f"https://{$bad}"', {"type": "string", "example": "https://example.com"}),
        (
            'f"https://{$core.vs.variables.$domain:value"',
            {"type": "string", "example": "https://example.com"},
        ),
        ('f"{$core.vs.variables.$code:value}"', {"type": "integer", "example": 301}),
        (
            'f"http://{$core.vs.variables.$domain:value}"',
            {
                "type": "string",
                "pattern": "^https://",
                "example": "https://example.com",
            },
        ),
    ],
)
def test_mutate_manifest_invalid_interpolation(in_list, value, field):
    scheme = make_scheme(
        {
            "properties": {
                "value": {"type": "array", "items": field} if in_list else field
            }
        }
    )
    manifest = {
        "resources": {"$core.nodes": {"node": {"value": [value] if in_list else value}}}
    }
    with pytest.raises(ValueError):
        schema.mutate_manifest(manifest, scheme)
        schema.validate_yaml(manifest, scheme)


@pytest.mark.parametrize("composition", ["allOf", "anyOf", "oneOf"])
@pytest.mark.parametrize("in_list", [False, True])
def test_mutate_manifest_interpolation_composed_schema(composition, in_list):
    field = {composition: [{"$ref": "#/components/schemas/Url"}]}
    scheme = make_scheme(
        {
            "properties": {
                "value": {"type": "array", "items": field} if in_list else field
            }
        }
    )
    scheme["components"]["schemas"]["Url"] = {
        "type": "string",
        "pattern": "^https://",
        "example": "https://example.com",
    }
    value = 'f"https://{$core.vs.variables.$domain:value}"'
    manifest = {
        "resources": {"$core.nodes": {"node": {"value": [value] if in_list else value}}}
    }
    schema.mutate_manifest(manifest, scheme)
    schema.validate_yaml(manifest, scheme)
    assert manifest["resources"]["$core.nodes"]["node"]["value"] == (
        ["https://example.com"] if in_list else "https://example.com"
    )


def test_interpolation_example_preserves_scheme_with_http_example():
    value = 'f"https://{$core.vs.variables.$domain:value}"'
    assert (
        schema.interpolation_example(value, {}, "http://example.com")
        == "https://example.com"
    )
