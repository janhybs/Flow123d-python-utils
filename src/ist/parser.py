# encoding: utf-8
# author:   Jan Hybs

#
import json

from ist.formatters.json2html import HTMLFormatter
from ist.formatters.json2latex import LatexFormatter
from ist.nodes import TypedList
from ist.utils.htmltree import htmltree


class ProfilerJSONDecoder(json.JSONDecoder):
    def decode(self, json_string):
        default_obj = super(ProfilerJSONDecoder, self).decode(json_string)
        lst = TypedList()
        lst.parse(default_obj)
        return lst


def json2latex(input_file='examples/example.json', output_file='../../docs/input_reference_red.tex'):
    with open(input_file, 'r') as fp:
        json_object = json.load(fp, encoding="utf-8", cls=ProfilerJSONDecoder)

    latex_result = ''.join(LatexFormatter.format(json_object))
    with open(output_file, 'w') as fp:
        fp.write(latex_result)


def json2html(input_file='examples/example.json', output_file='../../docs/input_reference_red.html'):
    with open(input_file, 'r') as fp:
        json_object = json.load(fp, encoding="utf-8", cls=ProfilerJSONDecoder)

    html_content = HTMLFormatter.format(json_object)

    html_body = htmltree('body')
    with html_body.open('div', '', { 'class': 'jumbotron' }):
        with html_body.open('div', '', { 'class': 'container' }):
            html_body.add(html_content.current())

    html_head = htmltree('head')
    html_head.tag('title', 'Flow123d input reference')
    html_head.style('css/main.css')
    html_head.style('css/bootstrap.min.css')

    html = htmltree('html')
    html.add(html_head.current())
    html.add(html_body.current())

    with open(output_file, 'w') as fp:
        fp.write(html.dump())


json2html()

# md_latex = MdLatexSupport()
# markdown_example = md_latex.prepare(markdown_example)
# html_example = markdown.markdown(markdown_example, extensions=[
# 'markdown.extensions.sane_lists',
#     'markdown.extensions.nl2br',
#     'ist.formatters.extensions.md_links'])
# html_example = md_latex.finish(html_example)
# tree = ET.fromstring('<html_example>' + html_example + "</html_example>")
