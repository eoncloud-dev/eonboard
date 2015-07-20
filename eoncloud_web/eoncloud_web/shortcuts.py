#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'


def retrieve_params(data, *keys):
    return tuple(data[key] for key in keys)
