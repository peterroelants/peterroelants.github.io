#!/usr/bin/env python3
"""
Convert jupyter notebook into Jekyll blogpost.

Example useage:
```
./notebook_convert.py \
    --nbpath <filename>.ipynb \
    --date "YYYY-MM-DD" \
    --layout <layout_template>
    --subdir <_posts subdir to move exported html to> \
    --description <Post description> \
    --tags <List of tags>
```
"""
import argparse
import os
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter

# Get the base directory of this project relative to this script
BASE_DIR = Path(os.path.realpath(__file__)).parent.parent


def nb2html(nb_filepath: Path) -> str:
    """
    Convert notebook to html string.
    """
    # Save notebook
    exporter = HTMLExporter(template_name="classic")
    # Use simple `nbconvert` provided template that excludes css and js.
    exporter.template_file = "base.html.j2"
    output, _ = exporter.from_filename(nb_filepath)
    return output


def insert_collapse_buttons(soup: BeautifulSoup):
    """
    Insert the collapse buttons on the code input field.
    If the input field ends with a line with only `#` it gets
    collapsed by defaultself.

    Effect:
        Changes soup object to have the collapse buttons.
    """
    input_areas = soup.select("div.inner_cell > div.input_area")
    for idx, input_area in enumerate(input_areas):
        # Add the collapse/expand button
        collapse_expand_button_tag = soup.new_tag("div")
        collapse_expand_button_tag["class"] = "collapse_expand_button fa-1x"
        input_area.insert(0, collapse_expand_button_tag)
        # Collapse if needed (annotated by `#` on last line)
        last_span = input_area("span")[-1]
        if last_span.text.strip() == "#":
            input_area["class"].append("collapsed")


def get_title(soup: BeautifulSoup) -> str:
    """
    Get the title element and return the str representation.

    Effect:
        Changes soup object to have title (h1) element removed.
    """
    title = str(soup.h1.contents[0])
    return title


def remove_output_stderr(soup: BeautifulSoup):
    """
    Remove the `output_stderr` elements from the notebook outputs.

    Effect:
        Changes soup object to have divs with class `output_stderr` removed.
    """
    for div_tag in soup.find_all("div", {"class": "output_stderr"}):
        div_tag.decompose()


def set_anchor_links(soup: BeautifulSoup):
    """
    Set the anchor links to link symbol

    Effect:
        Change anchor-link content to link symbol.
    """
    for a_tag in soup.find_all("a", {"class": "anchor-link"}):
        # Remove previous content
        a_tag.string = ""
        # Insert link symbol as tag
        a_tag.append(soup.new_tag("i", attrs={"class": "fas fa-sm fa-link"}))


def add_table_class(soup: BeautifulSoup):
    """
    Add `.table` class to table dataframe.
    Now pandas tables are visualised by html `<table class="dataframe">`. To
     be able to use bootstrap tables they need to have the `.table` class.
     https://getbootstrap.com/docs/4.0/content/tables/

    Effect:
        Changes soup object to have divs with class `output_stderr` removed.
    """
    for table in soup.find_all("table", {"class": "dataframe"}):
        table["class"] = table.get("class", []) + [
            "table",
            "table-sm",
            "table-hover",
            "w-auto",
            "text-right",
        ]
        # Add table container class to parent
        table.parent["class"] = table.parent.get("class", []) + [
            "contains-table",
        ]


def get_front_matter(args: argparse.Namespace, title: str) -> str:
    """
    Return Jekyll Front-Matter metadata.

    Front-Matter is YAML formatted.
    """
    dct = {
        "layout": args.layout,
        "title": title,
        "description": args.description,
        "tags": args.tags,
    }
    header_str = "\n".join(
        [
            "---",
            yaml.safe_dump(
                dct, sort_keys=False, default_flow_style=False, width=2147483647
            ).rstrip("\n"),
            "---",
            "",
        ]
    )
    return header_str


def add_jekyll_header(html_str: str, args: argparse.Namespace, title: str) -> str:
    """
    Add the Jekyll header to the given html (as str).
    """
    header = get_front_matter(args, title)
    return "\n".join([header, html_str])


def save_conversion(html_str: str, nbpath: Path, date: str, subdir: str = ""):
    """
    Save converted notebook file to Jekyll templated html file.

    args:
        html_str (str): Jekyll templated html str.
        nbpath (str): Filepath of original notebook file.
        date (str): Blogpost orginal publishing date (YYYY-MM-DD)

    Effect:

    """
    filename = nbpath.stem
    output_path = BASE_DIR / "_posts" / subdir / f"{date}-{filename}.html"
    print(f"conversion output path: {output_path!s}")
    with output_path.open("w") as f:
        f.write(html_str)


def get_arguments() -> argparse.ArgumentParser:
    """Get input arguments"""
    parser = argparse.ArgumentParser(description="Convert notebook to Jekyll blogpost.")
    parser.add_argument(
        "--nbpath", type=str, help="File path of notebook file to convert to blogpost"
    )
    parser.add_argument(
        "--date", type=str, help="Date of original publication of post."
    )
    parser.add_argument(
        "--layout",
        type=str,
        help="Layout template name to use as Jekyll layout for blogpost.",
    )
    parser.add_argument("--description", type=str, help="Description of the blogpost.")
    parser.add_argument(
        "--subdir", type=str, default="", help="Sub directory of base dir to put post."
    )
    parser.add_argument(
        "--tags", nargs="+", type=str, default=[], help="Tags related to the post."
    )
    return parser


def run(args: argparse.Namespace):
    """Run conversion script."""
    nb_path = Path(args.nbpath)
    print(f"\nConverting: {nb_path!s}")
    # Convert notebook into html
    html_str = nb2html(nb_path)
    soup = BeautifulSoup(html_str, "html.parser")
    # Create Title, cell collapse buttons, remove stderr, pandas tables
    insert_collapse_buttons(soup)
    title = get_title(soup)
    print("title: ", title)
    remove_output_stderr(soup)
    add_table_class(soup)
    set_anchor_links(soup)
    html_str = soup.prettify()
    # Add Jekyll header
    html_str = add_jekyll_header(html_str, args, title)
    # Export
    save_conversion(html_str, nb_path, args.date, args.subdir)


def main():
    parser = get_arguments()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
