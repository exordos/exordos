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

import enum


class Profile(str, enum.Enum):
    DEVELOP = "develop"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LEGACY = "legacy"

    @property
    def ram(self) -> int:
        """Return memory in Mb based on current element in enum."""
        memory = {
            self.DEVELOP: 1024,
            self.SMALL: 2048,
            self.MEDIUM: 8192,
            self.LARGE: 16384,
            self.LEGACY: 4096,
        }
        return memory[self]

    @property
    def cores(self) -> int:
        """Return CPU cores based on current element in enum."""
        cores = {
            self.DEVELOP: 1,
            self.SMALL: 2,
            self.MEDIUM: 4,
            self.LARGE: 8,
            self.LEGACY: 2,
        }
        return cores[self]
