#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CommandParam(object):
    @property
    def name(self) -> str:
        return self._name

    @property
    def details(self) -> str:
        return self._details

    @property
    def annotation(self) -> type:
        return self._annotation

    def __init__(self, name: str, details: str, annotation: type, default_value, has_default: bool, index: int):
        self._name = name

        if details is None:
            self._details = "No documentation provided."
        else:
            self._details = details

        self._annotation = annotation
        self.default_value = default_value
        self.has_default = has_default
        self.index = index

    def __str__(self) -> str:
        common = f":param {self._name}:"

        if self.annotation is not None:
            common = f"{common} ({self.annotation})"

        if self.has_default:
            return f"{common} {self._details} Default is {self.default_value}."
        else:
            return f"{common} {self._details}"
