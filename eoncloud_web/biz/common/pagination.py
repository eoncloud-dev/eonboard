#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
