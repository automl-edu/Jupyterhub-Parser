#!/usr/bin python

"""
Clear outputs of IPython notebooks.
By default, it prints the notebooks without outputs into stdout.
When the --in-place option is given, all files will be overwritten.
"""

import sys

import nbformat

NB_VERSION = 4


def clear_outputs(nb):
    """Clear output of notebook `nb` INPLACE."""
    for cell in nb.cells:
        cell.outputs = []

    # consider using https://nbconvert.readthedocs.io/en/latest/removing_cells.html instead.
    nb.cells = [cell for cell in nb.cells
                if not cell.source.lstrip().startswith('#! Solution')]

def stripoutput(inputs, inplace=False):
    """
    Strip output of notebooks.
    Parameters
    ----------
    inputs : list of string
        Path to the notebooks to be processed.
    inplace : bool
        If this is `True`, outputs in the input files will be deleted.
        Default is `False`.
    """
    for inpath in inputs:
        with open(inpath) as fp:
            nb = nbformat.read(fp, NB_VERSION)
        clear_outputs(nb)

        if inplace:
            with open(inpath, 'w') as fp:
                nbformat.write(nb, fp, NB_VERSION)
        else:
            nbformat.write(nb, sys.stdout)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('inputs', nargs='+', metavar='input',
                        help='Paths to notebook files.')
    # XXX: TODO: handle alternative outputs here, such as to stdout or to FILE
    parser.add_argument('-i', '--inplace', '--in-place', default=True,
                        action='store_true',
                        help='Overwrite existing notebook when given.')

    args = parser.parse_args()
    stripoutput(**vars(args))


if __name__ == '__main__':
    stripoutput(['/home/ruhkopf/PycharmProjects/DataScience/labs/exercises/04_visualization.ipynb'],
                inplace=True)
    main()
