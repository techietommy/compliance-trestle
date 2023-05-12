# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""OSCAL transformation tasks."""

import configparser
import logging
import pathlib
import traceback
from typing import Dict, Optional

from trestle.common import const
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.xccdf import XccdfTransformer

logger = logging.getLogger(__name__)

default_type = 'Validator'
default_title = 'XCCDF'
default_description = 'XCCDF Scan Results'


class XccdfResultToOscalAR(TaskBase):
    """
    Task to convert Xccdf result to OSCAL json.

    Attributes:
        name: Name of the task.
    """

    name = 'xccdf-result-to-oscal-ar'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task xccdf-result-to-oscal-ar.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        opt = '(optional)'
        req = '(required)'
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info(
            'Purpose: Transform Xccdf files into Open Security Controls Assessment Language (OSCAL) '
            + 'partial results files.'
        )
        logger.info('')
        logger.info('Configuration flags sit under [task.xccdf-result-to-oscal-ar]:')
        #
        t1 = f'  input-dir              = {req} '
        t2 = 'the path of the input directory comprising Xccdf results.'
        logger.info(f'{t1}{t2}')
        t1 = f'  output-dir             = {req} '
        t2 = 'the path of the output directory comprising synthesized OSCAL .json files.'
        logger.info(f'{t1}{t2}')
        t1 = f'  checking               = {opt} '
        t2 = 'True indicates perform strict checking of OSCAL properties, default is False.'
        logger.info(f'{t1}{t2}')
        t1 = f'  output-overwrite       = {opt} '
        t2 = 'true [default] or false; replace existing output when true.'
        logger.info(f'{t1}{t2}')
        t1 = f'  quiet                  = {opt} '
        t2 = 'true or false [default]; display file creations and rules analysis when false.'
        logger.info(f'{t1}{t2}')
        t1 = f'  title                  = {opt} '
        t2 = f'default={default_title}.'
        logger.info(f'{t1}{t2}')
        t1 = f'  description            = {opt} '
        t2 = f'default={default_description}.'
        logger.info(f'{t1}{t2}')
        t1 = f'  type                   = {opt} '
        t2 = f'default={default_type}.'
        logger.info(f'{t1}{t2}')
        t1 = f'  property-name-to-class = {opt} '
        t2 = 'list of name:class pairs for tagging named property with class, '
        t3 = 'e.g. "target:scc_inventory_item_id, version:scc_check_version".'
        logger.info(f'{t1}{t2}{t3}')
        t1 = f'  timestamp              = {opt} '
        t2 = 'timestamp for the Observations in ISO 8601 format, such as '
        t3 = ' 2021-01-04T00:05:23+04:00 for example; if not specified then value for "Timestamp" key in the Xccdf '
        t4 = ' result is used if present, otherwise current time is used.'
        logger.info(f'{t1}{t2}{t3}{t4}')
        #
        logger.info('')
        logger.info(
            'Operation: A transformation is performed on one or more Xccdf input files to produce output in OSCAL '
            + 'partial results format.'
        )

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        self._simulate = True
        return self._transform()

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        self._simulate = False
        return self._transform()

    def _transform(self) -> TaskOutcome:
        """Perform transformation."""
        try:
            return self._transform_work()
        except Exception:
            logger.debug(traceback.format_exc())
            mode = ''
            if self._simulate:
                mode = 'simulated-'
            return TaskOutcome(mode + 'failure')

    def _transform_work(self) -> TaskOutcome:
        """
        Perform transformation work steps.

        Work steps: read input, process, write output, display analysis
        """
        mode = ''
        if self._simulate:
            mode = 'simulated-'
        if not self._config:
            logger.warning('config missing')
            return TaskOutcome(mode + 'failure')
        # config required input & output dirs
        try:
            idir = self._config['input-dir']
            ipth = pathlib.Path(idir)
            odir = self._config['output-dir']
            opth = pathlib.Path(odir)
        except KeyError as e:
            logger.debug(f'key {e.args[0]} missing')
            return TaskOutcome(mode + 'failure')
        # config optional overwrite & quiet
        self._overwrite = self._config.getboolean('output-overwrite', True)
        quiet = self._config.get('quiet', False)
        self._verbose = not self._simulate and not quiet
        # title, description, type
        title = self._config.get('title', default_title)
        description = self._config.get('description', default_description)
        type_ = self._config.get('type', default_type)
        # property-name-to-class
        tags = self._get_tags()
        # config optional timestamp
        timestamp = self._config.get('timestamp')
        if timestamp is not None:
            try:
                XccdfTransformer.set_timestamp(timestamp)
            except Exception:
                logger.warning('config invalid "timestamp"')
                return TaskOutcome(mode + 'failure')
        # config optional performance
        modes = {
            'checking': self._config.getboolean('checking', False),
        }
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # process
        for ifile in sorted(ipth.iterdir()):
            if ifile.suffix not in ['.json', '.jsn', '.yaml', '.yml', '.xml']:
                continue
            blob = self._read_file(ifile)
            xccdf_transformer = XccdfTransformer()
            xccdf_transformer.set_title(title)
            xccdf_transformer.set_description(description)
            xccdf_transformer.set_type(type_)
            xccdf_transformer.set_modes(modes)
            xccdf_transformer.set_tags(tags)
            results = xccdf_transformer.transform(blob)
            oname = ifile.stem + '.oscal' + '.json'
            ofile = opth / oname
            if not self._overwrite and pathlib.Path(ofile).exists():
                logger.warning(f'output: {ofile} already exists')
                return TaskOutcome(mode + 'failure')
            self._write_file(results, ofile)
            self._show_analysis(xccdf_transformer)
        return TaskOutcome(mode + 'success')

    def _get_tags(self) -> Dict:
        """Get property name to class tags, if any."""
        tags = {}
        data = self._config.get('property-name-to-class')
        if data is not None:
            for item in data.split(','):
                item = item.strip()
                parts = item.split(':')
                if len(parts) == 2:
                    name = parts[0]
                    value = parts[1]
                    tags[name] = value
        return tags

    def _read_file(self, ifile: str) -> str:
        """Read raw input file."""
        if not self._simulate and self._verbose:
            logger.info(f'input: {ifile}')
        with open(ifile, encoding=const.FILE_ENCODING) as fp:
            blob = fp.read()
        return blob

    def _write_file(self, result: str, ofile: str) -> None:
        """Write oscal results file."""
        if not self._simulate:
            if self._verbose:
                logger.info(f'output: {ofile}')
            result.oscal_write(pathlib.Path(ofile))

    def _show_analysis(self, xccdf_transformer: XccdfTransformer) -> None:
        """Show analysis."""
        if not self._simulate and self._verbose:
            analysis = xccdf_transformer.analysis
            for line in analysis:
                logger.info(line)
