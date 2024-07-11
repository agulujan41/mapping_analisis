from enum import Enum


def create_enum(name, enum_list):
    enum = {}
    for i, value in enumerate(enum_list):
        enum[value] = i
    return Enum(name, enum)
