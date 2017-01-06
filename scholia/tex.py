r"""tex.

Usage:
  scholia.tex extract-qs-from-aux <file>
  scholia.tex write-bbl-from-aux <file>
  scholia.tex write-bib-from-aux <file>

Description:
  Work with latex and bibtex.

  The functionality is not complete.


Example latex document:

\documentclass{article}
\pdfoutput=1
\usepackage[utf8]{inputenc}

\begin{document}
Scientific citations \cite{Q26857876,Q21172284}.
Semantic relatedness \cite{Q26973018}.
\bibliographystyle{unsrt}
\bibliography{}
\end{document}

"""


from __future__ import print_function

from os.path import splitext

import re

from .api import (
    entity_to_authors, entity_to_classes, entity_to_doi,
    entity_to_journal_title, entity_to_month,
    entity_to_pages, entity_to_title, entity_to_volume, entity_to_year,
    wb_get_entities)


STRING_TO_TEX = {
    '<': r'\textless{}',
    '>': r'\textgreater{}',
    '~': r'\~{}',
    '{': r'\{',
    '}': r'\}',
    '_': r'\_',
    '\\': r'\textbackslash{}',
    '#': r'\#',
    '&': r'\&',
    '^': r'\^{}',
    '%': r'\%',
    '$': r'\$',
}

STRING_TO_TEX_URL = {
    '{': r'\{',
    '}': r'\}',
    '#': r'\#',
    '&': r'\&',
    '^': r'\^{}',
    '%': r'\%',
    '$': r'\$',
}

STRING_TO_TEX_PATTERN = re.compile(
    u'|'.join(re.escape(key) for key in STRING_TO_TEX),
    flags=re.UNICODE)

STRING_TO_TEX_URL_PATTERN = re.compile(
    u'|'.join(re.escape(key) for key in STRING_TO_TEX_URL),
    flags=re.UNICODE)


def escape_to_tex(string, escape_type='normal'):
    r"""Escape a text to the a tex/latex safe.

    Parameters
    ----------
    string : str
        Unicode string to be excaped.

    Returns
    -------
    escaped_string : str
        Escaped unicode string.

    Examples
    --------
    >>> escape_to_tex("^^") == r'\^{}\^{}'
    True

    >>> escape_to_tex('10.1007/978-3-319-18111-0_26', 'url')
    '10.1007/978-3-319-18111-0_26'

    References
    ----------
    - https://en.wikibooks.org/wiki/LaTeX/Special_Characters
    - http://stackoverflow.com/questions/16259923/

    """
    if escape_type == 'normal':
        unescaped_string = STRING_TO_TEX_PATTERN.sub(
            lambda match: STRING_TO_TEX[match.group()], string)
    elif escape_type == 'url':
        unescaped_string = STRING_TO_TEX_URL_PATTERN.sub(
            lambda match: STRING_TO_TEX_URL[match.group()], string)
    else:
        raise ValueError('Wrong value for parameter "url": {}'.format(type))
    return unescaped_string


def guess_bibtex_entry_type(entity):
    """Guess Bibtex entry type.

    Parameters
    ----------
    entity : dict
        Wikidata item.

    Returns
    -------
    entry_type : str
        Entry type as a string: 'Article', 'InProceedings', etc.

    """
    classes = entity_to_classes(entity)
    if "Q13442814" in classes:
        # TODO
        # Scientific article: Article, InProceedings, Misc, ...
        entry_type = 'Article'

    elif 'Q1143604' in classes:
        entry_type = 'Proceedings'

    elif 'Q26995865' in classes:
        entry_type = 'PhdThesis'

    elif 'Q571' in classes:
        entry_type = 'Book'

    else:
        pass

    return entry_type


def extract_qs_from_aux_string(string):
    r"""Extract qs from string.

    Paramaters
    ----------
    string : str
        Extract Wikidata identifiers from citations.

    Returns
    -------
    qs : list of str
        List of strings.

    Examples
    --------
    >>> string = "\citation{Q28042913}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913']

    >>> string = "\citation{Q28042913,Q27615040}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913', 'Q27615040']

    >>> string = "\citation{Q28042913,Q27615040,Q27615040}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913', 'Q27615040', 'Q27615040']

    >>> string = "\citation{Q28042913,NielsenF2002Neuroinformatics,Q27615040}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913', 'Q27615040']

    """
    matches = re.findall(r'^\\citation{(.+?)}', string,
                         flags=re.MULTILINE | re.UNICODE)
    qs = []
    for submatches in matches:
        for q in submatches.split(','):
            if re.match('Q\d+', q):
                qs.append(q)

    return qs


def entity_to_bibtex_entry(entity):
    """Convert Wikidata entity to bibtex-formatted entry.

    Parameters
    ----------
    entity : dict
        Wikidata entity as hierarchical structure.
    q : str
        Wikidata identifier

    Returns
    -------
    entry : str
        Bibtex entry.

    """
    entry = "@Article{%s,\n" % entity['id']
    entry += "  author =   {%s},\n" % \
             escape_to_tex(u" and ".join(entity_to_authors(entity)))
    entry += "  title =    {{%s}},\n" % escape_to_tex(entity_to_title(entity))
    entry += "  journal =  {%s},\n" % (
        escape_to_tex(entity_to_journal_title(entity)))
    entry += "  year =     {%s},\n" % escape_to_tex(entity_to_year(entity))
    entry += "  volume =   {%s},\n" % escape_to_tex(entity_to_volume(entity))
    entry += "  number =   {},\n"
    entry += "  month =    {%s},\n" % escape_to_tex(entity_to_month(entity))
    entry += "  pages =    {%s},\n" % escape_to_tex(entity_to_pages(entity))
    entry += "  DOI =      {%s},\n" % escape_to_tex(entity_to_doi(entity),
                                                    'url')
    entry += "  wikidata = {%s}\n" % escape_to_tex(entity['id'])
    entry += '}\n'
    return entry


def main():
    """Handle command-line arguments."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['extract-qs-from-aux']:
        string = open(arguments['<file>']).read()
        print(" ".join(extract_qs_from_aux_string(string)))

    elif arguments['write-bbl-from-aux']:
        aux_filename = arguments['<file>']
        base_filename, _ = splitext(aux_filename)
        bbl_filename = base_filename + '.bbl'

        string = open(aux_filename).read()
        qs = extract_qs_from_aux_string(string)
        entities = wb_get_entities(qs)

        widest_label = max([len(q) for q in qs])
        bbl = u'\\begin{thebibliography}{%d}\n\n' % widest_label

        for q in qs:
            entity = entities[q]
            bbl += '\\bibitem{%s}\n' % q
            bbl += u", ".join(entity_to_authors(entity)) + '.\n'
            bbl += entity_to_title(entity) + '.\n'

            bbl += '\n'

        bbl += '\\end{thebibliography}\n'

        with open(bbl_filename, 'w') as f:
            f.write(bbl.encode('utf-8'))

        with open(aux_filename, 'a') as f:
            for n, q in enumerate(qs, 1):
                f.write('\\bibcite{%s}{%d}\n' % (q, n))

    elif arguments['write-bib-from-aux']:
        aux_filename = arguments['<file>']
        base_filename, _ = splitext(aux_filename)
        bib_filename = base_filename + '.bib'

        string = open(aux_filename).read()
        qs = extract_qs_from_aux_string(string)
        entities = wb_get_entities(qs)

        bib = ""
        for q in qs:
            entity = entities[q]
            bib += entity_to_bibtex_entry(entity)
            bib += '\n'

        with open(bib_filename, 'w') as f:
            f.write(bib.encode('utf-8'))


if __name__ == '__main__':
    main()