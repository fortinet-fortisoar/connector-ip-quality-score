""" 
Copyright start 
Copyright (C) 2008 - 2022 Fortinet Inc.
All rights reserved. 
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE 
Copyright end 
"""
from connectors.core.connector import Connector, get_logger, ConnectorError
from integrations.crudhub import make_request
from django.conf import settings
from .operations import operations, _check_health, MACRO_LIST, CONNECTOR_NAME

logger = get_logger('ip-quality-score')


class IPQualityScore(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            logger.info('In execute() Operation: {}'.format(operation))
            operation = operations.get(operation)
            return operation(config, params)
        except Exception as err:
            logger.error('An exception occurred {}'.format(err))
            raise ConnectorError('{}'.format(err))

    def check_health(self, config):
        try:
            return _check_health(config)
        except Exception as e:
            logger.exception("An exception occurred {}".format(e))
            raise ConnectorError(e)

    def del_micro(self, config, enable=True):
        if not settings.LW_AGENT:
            for macro in MACRO_LIST:
                try:
                    resp = make_request(f'/api/wf/api/dynamic-variable/?name={macro}', 'GET')
                    if resp['hydra:member']:
                        # macro exists
                        # on config add and activate, we need to add to the list, so no changes required if it is already there
                        if enable and CONNECTOR_NAME in resp['hydra:member'][0].get('name'):
                            continue
                        # on config remove and deactivate, we need to remove from the list, so no changes required if it is not already there
                        if not enable and CONNECTOR_NAME not in resp['hydra:member'][0].get('name'):
                            continue
                        logger.info("resetting global variable '%s'" % macro)
                        macro_id = resp['hydra:member'][0]['id']
                        resp = make_request(f'/api/wf/api/dynamic-variable/{macro_id}/?format=json', 'DELETE')
                except Exception as e:
                    logger.error(e)

    def on_deactivate(self, config):
        self.del_micro(config, False)

    def on_activate(self, config):
        self.del_micro(config, True)

    def on_add_config(self, config, active):
        self.del_micro(config, True)

    def on_delete_config(self, config):
        self.del_micro(config, False)
