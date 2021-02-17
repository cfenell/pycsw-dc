# -*- coding: utf-8 -*-
# =================================================================
#
# - pycsw DataCite output plugin -
#
# Authors: Carl-Fredrik Enell <carl-fredrik.enell@eiscat.se>
# Based on pycsw plugins by  Tom Kralidis <tomkralidis@gmail.com>
# DataCite schema follows:
# https://github.com/inveniosoftware/datacite/blob/master/datacite/schema42.py
# https://schema.datacite.org/meta/kernel-4.3/example/datacite-example-full-v4.xml
#
# This module intends to follow DataCite 4.3
#
# PyCSW  Copyright (C) 2015 Tom Kralidis
# Schema Copyright (C) 2016 CERN
# Schema Copyright (C) 2019 Caltech
# This file Copyright (C) 2020 EISCAT Scientific Association
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
from pycsw.core import util
from pycsw.core.etree import etree
from os.path import basename
from datetime import datetime

"""
datacite.py
Output plugin for DataCite 4.3 schema output
Defines function write_record
Input:  result, esn, context, url  (pycsw query results)
Output: XML etree according to DataCite schema
"""

NAMESPACE = 'http://datacite.org/schema/kernel-4'
NAMESPACES = {'xml': 'http://www.w3.org/XML/1998/namespace', 'datacite': NAMESPACE}


# Datacite schema required records
# resourceType
# identifier identifierType DOI
# creators -> creator
# titles -> title
# publisher
# publicationYear

# Datacite schema optional records
# subjects
# contributors
# dates
# language
# alternateIdentifiers
# relatedIdentifiers
# sizes
# formats
# version
# rightsList
# descriptions
# geoLocations
# fundingReferences

XPATH_MAPPINGS = {
     'pycsw:Identifier': 'identifier',
     'pycsw:Creator': 'creators/creator',
     'pycsw:Title': 'titles/title',
     'pycsw:Publisher': 'publisher',
     'pycsw:PublicationDate': 'publicationYear'
}


def write_record(result, esn, context, url=None):
    """
    Main function
    Return csw:SearchResults child as lxml.etree.Element
    """
    typename = util.getqattr(result, context.md_core_model['mappings']['pycsw:Typename'])
    # Check if we already have DataCite formatted metadata
    if esn == 'full' and typename == 'datacite':
        # dump record as is and exit
        return etree.fromstring(util.getqattr(result, context.md_core_model['mappings']['pycsw:XML']), context.parser)
    # Otherwise build XML tree from available metadata
    node = etree.Element(util.nspath_eval('resource', NAMESPACES))
    node.attrib[util.nspath_eval('xsi:schemaLocation', context.namespaces)] = \
        '%s http://schema.datacite.org/meta/kernel-4.3/metadata.xsd' % NAMESPACE
    # Type
    type = etree.SubElement(node, util.nspath_eval('resourceType', NAMESPACES))
    type.text = "XML"
    resTypeGeneral = basename(util.getqattr(result, context.md_core_model['mappings']['pycsw:Type']))
    assert resTypeGeneral in  [
        "Audiovisual",
        "Collection",
        "DataPaper",
        "Dataset",
        "Event",
        "Image",
        "InteractiveResource",
        "Model",
        "PhysicalObject",
        "Service",
        "Software",
        "Sound",
        "Text",
        "Workflow",
        "Other"
      ]
    type.attrib[util.nspath_eval('resourceTypeGeneral', NAMESPACES)] = resTypeGeneral
    # Identifier
    ident = etree.SubElement(node, util.nspath_eval('identifier', NAMESPACES))
    ival = util.getqattr(result, context.md_core_model['mappings']['pycsw:Identifier'])
    ident.text = ival
    #Identifier type:
    # NB DOI is mandatory for DataCite proper but we plan to use the schema with other IDs too. Modify as necessary.
    if ival.lower().startswith("doi"):
        idType = "DOI"
    elif ival.lower().startswith("handle"):
        idType = "Handle"
    elif ival.lower().startswith("urn"):
        idType = "URN"
    ident.attrib[util.nspath_eval('identifierType', NAMESPACES)] = idType or "DOI"
    # Creators
    creators = etree.SubElement(node, util.nspath_eval('creators', NAMESPACES))
    cval = util.getqattr(result, context.md_core_model['mappings']['pycsw:OrganizationName'])
    if cval:
        creator = etree.SubElement(creators,  util.nspath_eval('creator', NAMESPACES))
        creatorName = etree.SubElement(creator,  util.nspath_eval('creatorName', NAMESPACES))
        # FIXME difference between Language and ResourceLanguage?
        creatorName.attrib[util.nspath_eval('xml:lang', NAMESPACES)] = util.getqattr(context.md_core_model['mappings']['pycsw:Language']) or "en" #Default to English
        creatorName.attrib[util.nspath_eval('nameType', NAMESPACES)] = "Organizational"
    
        creatorName.text = cval
    # Person NB assuming Lastname, Firstname
    cval = util.getqattr(result, context.md_core_model['mappings']['pycsw:Creator'])
    if cval:
        creator = etree.SubElement(creators,  util.nspath_eval('creator', NAMESPACES))
        creatorName = etree.SubElement(creator,  util.nspath_eval('creatorName', NAMESPACES))
        creatorName.attrib[util.nspath_eval('nameType', NAMESPACES)] = "Personal"
        creatorName.text = cval
        cval = cval.split(",")
        lastName = cval[0]
        firstName = cval[1]
        if lastName:
            etree.SubElement(creator,  util.nspath_eval('familyName', NAMESPACES)).text = lastName
        if firstName:
            etree.SubElement(creator,  util.nspath_eval('givenName', NAMESPACES)).text = firstName
        # FIXME are affiliations available?
        #avals = ["EISCAT Scientific Association"] 
        #for aval in avals:
        #    creatorAffil = etree.SubElement(creator,  util.nspath_eval('affiliation', NAMESPACES)).text = aval
        #    creatorAffil.attrib[util.nspath_eval('affiliationIdentifier', NAMESPACES)] = "Fixme"
        #    creatorAffil.attrib[util.nspath_eval('affiliationIdentifierScheme', NAMESPACES)] = "Fixme"
        # FIXME are other identifiers available? eg ORCID
        #nameIdentifier = "00001-00002-00003-00004"
        #if nameIdentifier:
        #    creatorNameIdentifier = etree.SubElement(creator,  util.nspath_eval('nameIdentifier', NAMESPACES))
        #    creatorNameIdentifier.text = nameIdentifier
        #    creatorNameIdentifier.attrib[util.nspath_eval('schemeURI', NAMESPACES)]= "http://orcid.org/"
        #    creatorNameIdentifier.attrib[util.nspath_eval('nameIdentifierScheme', NAMESPACES)] = "ORCID"
    # Title
    titles = etree.SubElement(node, util.nspath_eval('titles', NAMESPACES))
    tval = util.getqattr(result, context.md_core_model['mappings']['pycsw:Title'])
    title = etree.SubElement(titles, util.nspath_eval('title', NAMESPACES))
    title.attrib[util.nspath_eval("xml:lang", NAMESPACES)]= util.getqattr(result, context.md_core_model['mappings']['pycsw:Language']) or "en"
    title.text = tval
    sval = util.getqattr(result, context.md_core_model['mappings']['pycsw:AlternateTitle'])
    if sval:
        subtitle = etree.SubElement(titles, util.nspath_eval('title', NAMESPACES))
        subtitle.attrib["titleType"] = "Subtitle"
        subtitle.text = sval
    # Publisher
    etree.SubElement(node, util.nspath_eval('publisher', NAMESPACES)).text = util.getqattr(result, context.md_core_model['mappings']['pycsw:Publisher'])
    # PublicationYear
    dval = util.getqattr(result, context.md_core_model['mappings']['pycsw:PublicationDate'])
    if dval:
        dt = datetime.fromisoformat(dval)
        dt = dt.strftime("%Y")
    else:
        dt = "9999" #Date missing
    etree.SubElement(node, util.nspath_eval('publicationYear', NAMESPACES)).text = dt
    # End DataCite mandatory properties
    # TODO add all optional DataCite properties
    return node
