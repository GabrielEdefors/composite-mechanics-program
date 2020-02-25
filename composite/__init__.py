"""Package with tools used in composite mechanics mechanics. Currently contains tools based on classical laminate theory.

Authors: Gabriel Edefors
Year: 2020

Classes:

"""
version = "1.0.0"

from . lamina import Lamina
from . laminate import Laminate
from . parser import read_input_file
from . material import Material