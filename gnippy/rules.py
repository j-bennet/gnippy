# -*- coding: utf-8 -*-

import requests

from gnippy import config
from gnippy.errors import *


def _generate_rules_url(url):
    """ Generate a rules URL from a PowerTrack URL """
    if ".json" not in url:
        raise BadPowerTrackUrlException("Doesn't end with .json")
    return url.replace(".json", "/rules.json")


def _generate_post_object(rules_list):
    """ Generate the JSON object that gets posted to the Rules API. """
    if isinstance(rules_list, list):
        return { "rules": rules_list }
    else:
        raise BadArgumentException("rules_list must be of type list")


def _check_rules_list(rules_list):
    """ Checks a rules_list to ensure that all rules are in the correct format. """
    def fail():
        msg = "rules_list is not in the correct format. Please use build_rule to build your rules list."
        raise RulesListFormatException(msg)

    if not isinstance(rules_list, list):
        fail()

    expected = ("value", "tag")
    for r in rules_list:
        if not isinstance(r, dict):
            fail()

        if "value" not in r:
            fail()

        if not isinstance(r['value'], basestring):
            fail()

        if "tag" in r and not isinstance(r['tag'], basestring):
            fail()

        for k in r:
            if k not in expected:
                fail()


def _post(conf, built_rules):
    """
        Generate the Rules URL and POST data and make the POST request.
        POST data must look like:
        {
            "rules": [
                        {"value":"rule1", "tag":"tag1"},
                        {"value":"rule2"}
                     ]
        }

        Args:
            conf: A configuration object that contains auth and url info.
            built_rules: A single or list of built rules.
    """
    _check_rules_list(built_rules)
    rules_url = _generate_rules_url(conf['url'])
    post_data = _generate_post_object(built_rules)
    r = requests.post(rules_url, auth=conf['auth'], data=post_data)
    if not r.status_code in range(200,300):
        error_text = "HTTP Response Code: %s, Text: '%s'" % (str(r.status_code), r.text)
        raise RuleAddFailedException(error_text)


def build_rule(rule_string, tag=None):
    """
        Takes a rule string and optional tag and turns it into a "built_rule" that looks like:
        { "value": "rule string", "tag": "my tag" }
    """
    if rule_string is None:
        raise BadArgumentException("rule_string cannot be None")
    rule = { "value": rule_string }
    if tag:
        rule['tag'] = tag
    return rule


def add_rule(rule_string, rule_tag, **kwargs):
    """ Synchronously add a single rule to GNIP PowerTrack. """
    conf = config.resolve(kwargs)
    rule = build_rule(rule_string, rule_tag)
    rules_list = [rule,]
    _post(conf, rules_list)


def add_rules(rules_list, **kwargs):
    """ Synchronously add multiple rules to GNIP PowerTrack in one go. """
    conf = config.resolve(kwargs)
    _post(conf, rules_list)
