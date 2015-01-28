
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2014- ZwodahS
# github.com/ZwodahS/
# zwodahs.me
# @ZwodahS

"""
Every function that can be called are implemented as a class

The class MUST have a few property in order for it to be registered.

allowed_context : a list containing what context it can be run on
args : number of arguments, raise RuntimeException if argument don't fit.
name : name of the function i.e. #

Try to use namespace for function name that are not part of the default package.
For example, if you are implementing a new sort, don't override sort, instead call it foo.sort instead.

A copy of the data will be passed to the function.
"""

from jstql import JSTQLRuntimeException
from operator import itemgetter, attrgetter

def _sort_func(context, reverse=False, key=None, keyType=None):
    if not key:
        context.mdata.sort(reverse=reverse)
        return context.mdata

    keyType = keyType or "item"
    if keyType == "attr":
        context.mdata.sort(key=attrgetter(key), reverse=reverse)
    elif keyType == "item":
        context.mdata.sort(key=itemgetter(key), reverse=reverse)
    else:
        raise JSTQLRuntimeException(current_state=context.data, message="Unknown sort type {0}".format(keyType))

    return context.mdata


class SortFunction(object):

    name = "sort"
    allowed_context = [list]
    args = [0, 1, 2]

    @classmethod
    def run(cls, context, *args):
        if len(args) == 0:
            return _sort_func(context)
        elif len(args) == 1:
            return _sort_func(context, key=args[0])
        else:
            return _sort_func(context, key=args[1], ketType=args[0])


class RSortFunction(object):

    name = "rsort"
    allowed_context = [list]
    args = [0, 1, 2]

    @classmethod
    def run(cls, context, *args):
        if len(args) == 0:
            return _sort_func(context, reverse=True)
        elif len(args) == 1:
            return _sort_func(context, key=args[0], reverse=True)
        else:
            return _sort_func(context, key=args[1], ketType=args[0], reverse=True)


class StringUpperFunction(object):

    name = "upper"
    allowed_context = [str]
    args = [0]

    @classmethod
    def run(cls, context, *args):
        return context.mdata.upper()


class StringLowerFunction(object):

    name = "lower"
    allowed_context = [str]
    args = [0]

    @classmethod
    def run(cls, context, *args):
        return context.mdata.lower()

functions = [SortFunction, RSortFunction, StringUpperFunction, StringLowerFunction]
