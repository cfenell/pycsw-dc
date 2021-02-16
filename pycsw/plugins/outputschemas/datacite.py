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
NAMESPACES = {'xml': 'http://www.w3.org/XML/1998/namespace','datacite': NAMESPACE}


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

    ### DataCite  properties
    print(result)
    
    ## Type
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
    type.attrib["resourceTypeGeneral"] = resTypeGeneral
    
    ## Identifier
    ident = etree.SubElement(node, util.nspath_eval('identifier', NAMESPACES))
    ident.text = util.getqattr(result, context.md_core_model['mappings']['pycsw:Identifier'])
    ident.attrib["identifierType"] = "DOI"  #  NB DOI is mandatory for DataCite proper but we plan to use the schema with other IDs too
    
    ## Creators
    cvals = util.getqattr(result, context.md_core_model['mappings']['pycsw:Creator']) #FIXME get multiple creators possible?
    creators = etree.SubElement(node, util.nspath_eval('creators', NAMESPACES))
    if not cvals is None:
        for cval in cvals:
            creator = etree.SubElement(creators,  util.nspath_eval('creator', NAMESPACES))
            creatorName = etree.SubElement(creator,  util.nspath_eval('creatorName', NAMESPACES))
            creatorName.attrib['lang'] = "xml:en"
            # FIXME get name type personal, organizational ..
            person_or_org_name = "person"
            if person_or_org_name == "org":
                # Get the org name
                creatorName.attrib['nameType'] = "Organizational"
                creatorName.text = cval
            elif person_or_org_name == "person":
                cval = cval.split(",")
                lastName = cval[0]
                firstName = cval[1]
                creatorName.attrib['nameType'] = "Personal"
                creatorName.text = "%s, %s" % (lastName, firstName)
                avals = ["EISCAT Scientific Association"]  # FIXME find affiliation names...
                for aval in avals:
                    creatorAffil = etree.SubElement(creator,  util.nspath_eval('affiliation', NAMESPACES)).text = aval
                    creatorAffil.attrib['affiliationIdentifier'] = "Fixme"
                    creatorAffil.attrib['affiliationIdentifierScheme'] = "Fixme"
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
    #FIXME get multiple titles possible?
    tval = util.getqattr(result, context.md_core_model['mappings']['pycsw:Title'])
    # for tval in [tvals]:
    title = etree.SubElement(titles, util.nspath_eval('title', NAMESPACES))
    title.attrib["lang"]="xml:en" # FIXME
    title.text = tval
    #svals = ["Fixme"]  # FIXME are subtitles available in pycsw?
    #for sval in svals:
    #    subtitle = etree.SubElement(titles, util.nspath_eval('title', NAMESPACES))
    #    subtitle.attrib["titleType"] = "Subtitle"
    #    subtitle.text = sval
        
    ## Publisher
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Publisher'])
    etree.SubElement(node, util.nspath_eval('publisher', NAMESPACES)).text = val  # Free format string

    # PublicationYear
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:PublicationDate'])
    # FIXME convert date to year in a general way. String 'YYYY' 
    etree.SubElement(node, util.nspath_eval('publicationYear', NAMESPACES)).text = val
    
    ## End DataCite mandatory properties
    ## TODO add all optional DataCite properties
    return node
