#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional


class CommandReturn(object):
    @property
    def details(self) -> str:
        return self._details

    def __init__(self, details: str, anno: Optional[type]):
        self._details = details
        self.annotation = anno

    def __str__(self):
        if self.annotation is None:
            return f":return: {self._details}"
        else:
            return f":return: ({self.annotation}) {self._details}"
