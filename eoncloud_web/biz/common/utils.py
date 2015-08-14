#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'


def retrieve_params(data, *keys):
    return tuple(data[key] for key in keys)


def retrieve_list_params(data, *keys):
    return tuple(data.getlist(key) for key in keys)
