#!/usr/bin/env python3
"""
Convert jupyter notebook into Jekyll blogpost.

Example useage:
```
./notebook_convert.py --nbpath <filename>.ipynb --date "YYYY-MM-DD" --layout <layout_template>
```
"""
import os
from pathlib import Path
import argparse
from nbconvert import HTMLExporter
from bs4 import BeautifulSoup


# Get the base directory of this project relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Get input arguments
parser = argparse.ArgumentParser(
    description='Convert notebook to Jekyll blogpost.')
parser.add_argument(
    '--nbpath', type=str,
    help='File path of notebook file to convert to blogpost')
parser.add_argument(
    '--date', type=str,
    help='Date of original publication of post.')
parser.add_argument(
    '--layout', type=str,
    help='Layout template name to use as Jekyll layout for blogpost.')
parser.add_argument(
    '--description', type=str,
    help='Description of the blogpost.')


def nb2html(nb_filepath):
    """
    Convert notebook to html string.

    Args:
        nb_filepath (str): Path of notbook file

    Returns:
        (str): HMTL of converted notebook.
    """
    # Save notebook
    exporter = HTMLExporter(template_name='classic')
    exporter.template_file = 'base.html.j2'
    output, resources = exporter.from_filename(nb_filepath)
    return output


def insert_collapse_buttons(soup):
    """
    Insert the collapse buttons on the code input field.
    If the input field ends with a line with only `#` it gets
    collapsed by defaultself.

    Args:
        soup (BeautifulSoup): HTML parsed notebook.

    Effect:
        Changes soup object to have the collapse buttons.
    """
    input_areas = soup.select('div.inner_cell > div.input_area')
    for idx, input_area in enumerate(input_areas):
        # Add the collapse/expand button
        collapse_expand_button_tag = soup.new_tag('div')
        collapse_expand_button_tag['class'] = 'collapse_expand_button fa fa-1x fa-minus-square-o'
        input_area.insert(0, collapse_expand_button_tag)
        # Collapse if needed (annotated by `#` on last line)
        last_span = input_area('span')[-1]
        if last_span.text.strip() == '#':
            input_area['class'].append('collapsed')


def remove_title(soup):
    """
    Remove the title element and return the str representation.

    Args:
        soup (BeautifulSoup): HTML parsed notebook.

    Effect:
        Changes soup object to have title (h1) element removed.

    Returns:
        (str): Title text
    """
    title = str(soup.h1.contents[0])
    soup.h1.decompose()
    # escape colon character to avoid Jekyll issues
    title = title.replace(':', '&#58;')
    return title


def remove_output_stderr(soup):
    """
    Remove the `output_stderr` elements from the notebook outputs.

    Args:
        soup (BeautifulSoup): HTML parsed notebook.

    Effect:
        Changes soup object to have divs with class `output_stderr` removed.
    """
    for div in soup.find_all('div', {'class':'output_stderr'}):
        div.decompose()


def add_table_class(soup):
    """
    Add `.table` class to table dataframe.
    Now pandas tables are visualised by html `<table class="dataframe">`. To
     be able to use bootstrap tables they need to have the `.table` class.
     https://getbootstrap.com/docs/4.0/content/tables/
    Args:
        soup (BeautifulSoup): HTML parsed notebook.

    Effect:
        Changes soup object to have divs with class `output_stderr` removed.
    """
    for table in soup.find_all('table', {'class':'dataframe'}):
        table['class'] = table.get('class', []) + [
            'table', 'table-sm', 'table-hover', 'w-auto', 'text-right']


def add_jekyll_header(html_str, layout, title, description):
    """
    Add the Jekyll header to the html strings.

    Args:
        html_str (str): HTML of converted notebook.
        layout (str): Jekyll layout to use.
        title (str): Title to use.
        description (str): Description to use

    Returns:
        (str): HTML with Jekyll layout header on top.
    """
    header = '\n'.join([
        '---',
        f'layout: {layout}',
        f'title: {title}',
        f'description: {description}',
        '---',
        ''
    ])
    return '\n'.join([header, html_str])


def save_conversion(html_str, nbpath, date):
    """
    Save converted notebook file to Jekyll templated html file.

    args:
        html_str (str): Jekyll templated html str.
        nbpath (str): Filepath of original notebook file.
        date (str): Blogpost orginal publishing date (YYYY-MM-DD)

    Effect:

    """
    filename = Path(nbpath).stem
    output_path = os.path.join(
        BASE_DIR, '_posts', f'{date}-{filename}.html')
    print('output_path: ', output_path)
    with open(output_path, 'w') as f:
        f.write(html_str)


def main():
    """Run conversion script."""
    args = parser.parse_args()
    print('\nConverting: ', args.nbpath)
    html_str = nb2html(args.nbpath)
    soup = BeautifulSoup(html_str, 'html.parser')
    insert_collapse_buttons(soup)
    title = remove_title(soup)
    print('title: ', title)
    remove_output_stderr(soup)
    add_table_class(soup)
    html_str = soup.prettify()
    html_str = add_jekyll_header(
        html_str, args.layout, title, args.description)
    save_conversion(html_str, args.nbpath, args.date)



if __name__ == "__main__":
    main()
