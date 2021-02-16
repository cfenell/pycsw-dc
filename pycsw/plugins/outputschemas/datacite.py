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

"""
datacite.py
Output plugin for DataCite 4.3 schema output
Defines function write_record
Input:  result, esn, context, url  (pycsw query results)
Output: XML etree according to DataCite schema
"""

NAMESPACE = 'http://datacite.org/schema/kernel-4'
NAMESPACES = {'datacite': NAMESPACE}


 XPATH_MAPPINGS = {
     'pycsw:Identifier': 'datacite:identifier',
     'pycsw:Creator': 'datacite:creators',
     'pycsw:Title': 'datacite:title',
     'pycsw:Publisher': 'datacite:publisher'
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

    ## DataCite  properties
    ## Identifier
    ident = etree.SubElement(node, util.nspath_eval('identifier', NAMESPACES))
    ident.text = util.getqattr(result, context.md_core_model['mappings']['pycsw:Identifier'])
    ident.attrib["identifierType"] = "DOI"  #  FIXME Mandatory for DataCite harvesting but plan to use this schema with other IDs too
    
    ## Creators
    cvals = util.getqattr(result, context.md_core_model['mappings']['pycsw:Creator']) #FIXME get multiple creators possible?
    creators = etree.SubElement(node, util.nspath_eval('creators', NAMESPACES))
    for cval in cvals:
        creator = etree.SubElement(creators,  util.nspath_eval('creator', NAMESPACES))
        creator.text = cval
        creatorName = etree.SubElement(creator,  util.nspath_eval('creatorName', NAMESPACES))
        creatorName.attrib['xml:lang'] = "en"
        # FIXME get name type personal, organizational ..
        if person_or_org_name == "org":
            # Get the org name
            creatorName.attrib['nameType'] = "Organizational"
            creatorName.text = orgName
        elif person_or_org_name == "person":
            lastName = 'Fixme'
            firstName = 'Fixme'
            creatorName.attrib['nameType'] = "Personal"
            creatorName.text = "%s, %s" % (lastName, firstName)
            avals = ""  # FIXME find multiple affiliation names...
            for aval in avals:
                creatorAffil = etree.SubElement(creator,  util.nspath_eval('affiliation', NAMESPACES)).text = aval
                creatorAffil.attribute['affiliationIdentifier', context.namespaces)] = "Fixme"
                creatorAffil.attribute['affiliationIdentifierScheme', context.namespaces)] = "Fixme"
            if lastName:
                etree.SubElement(creator,  util.nspath_eval('familyName', NAMESPACES)).text = lastName
            if firstName:
                etree.SubElement(creator,  util.nspath_eval('givenName', NAMESPACES)).text = firstName
            nameIdentifier = "00001-00002-00003-00004"
            if nameIdentifier:
                creatorNameIdentifier = etree.SubElement(creator,  util.nspath_eval('nameIdentifier', NAMESPACES))
                creatorNameIdentifier.text = nameIdentifier
                creatorNameIdentifier.attrib['schemeURI']= "http://orcid.org/"
                creatorNameIdentifier.attrib['nameIdentifierScheme'] = "ORCID"
        else:
            pass

    ## Title
    titles = etree.SubElement(node, util.nspath_eval('titles', NAMESPACES))
    tvals = util.getqattr(result, context.md_core_model['mappings']['pycsw:Title']) #FIXME get multiple titles possible?
    for tval in tvals:
        etree.SubElement(titles, util.nspath_eval('title', NAMESPACES)).text = val
    svals = 'Fixme'  # FIXME are subtitles available in pycsw?
    for sval in svals:
        subtitle = etree.SubElement(titles, util.nspath_eval('title', NAMESPACES))
        subtitle.attrib["titleType"] = "Subtitle"
        subtitle.text = sval


    # Here 20210213
        
    # Publisher
    # val = "EISCAT Scientific Association"
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Publisher'])
    etree.SubElement(node, util.nspath_eval('publisher', NAMESPACES)).text = val

    # PublicationYear
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:PublicationDate'])
    etree.SubElement(node, util.nspath_eval('publicationYear', NAMESPACES)).text = val

    # resourceType
    restype = etree.SubElement(node, util.nspath_eval('resourceType', NAMESPACES))
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Format'])
    restype.text = val  
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Type'])
    restype.attrib["resourceTypeGeneral"] = basename(val) # FIXME check for allowed types

    # End DataCite mandatory properties
    # TODO add all optional DataCite properties
    return node

