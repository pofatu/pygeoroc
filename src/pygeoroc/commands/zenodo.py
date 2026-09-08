"""
Cteate metadata for Zenodo.
"""
import json
import collections


def run(args):
    desc = "<p>Cite the sources of this dataset as:</p>"
    rels = []
    for ds in args.repos.index:
        desc += '\n\n<blockquote><p>{}</p></blockquote>'.format(ds.citation)
        rels.append(collections.OrderedDict([
            ('scheme', 'doi'), ('identifier', ds.doi), ('relation', 'cites')]))

    print(json.dumps(
        collections.OrderedDict([
            ("title", "GEOROC data as SQLite database derived from GEOROC Compilations provided by "
                      "DIGIS Team"),
            ("access_right", "open"),
            ("creators", [{"name": "Robert Forkel"}]),
            ("upload_type", "dataset"),
            ("license", {"id": "CC-BY-4.0"}),
            ('description', desc),
            ('related_identifiers', rels),
        ]),
        indent=4))
