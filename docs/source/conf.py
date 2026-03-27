# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'birdsarentreal'
copyright = '2026, Borsato A. — Elsawalhi A. — Parekh V.'
author = 'Borsato A. — Elsawalhi A. — Parekh V.'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Extensions
extensions = [
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'autoapi.extension'
]
# AutoAPI settings
autoapi_type = 'python'
autoapi_dirs = ['../../app']
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary'
]
autoapi_template_dir = "_templates/autoapi"

# Theme settings
html_theme = 'sphinx_rtd_theme'
