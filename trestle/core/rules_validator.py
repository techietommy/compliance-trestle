# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2023 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Validate by confirming rule parameter values are consistent."""
from trestle.common.common_types import TopLevelOscalModel
from trestle.core.validator import Validator


class RulesValidator(Validator):
    """Validator to confirm all rule parameter values are consistent."""

    def model_is_valid(self, model: TopLevelOscalModel, quiet: bool) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.

        returns:
            True (valid) if the model's responsible parties match those found in roles.
        """
        # FIXME add actual check for rule and rule param validity
        return True
