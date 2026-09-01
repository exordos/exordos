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
