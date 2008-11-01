#
from pyon import loads, dumps
from etree import Element, Item

htmlTags = ["html", "meta", "header", "body", "table", "td", "tr", "p", "h1", "h2", "h3", "h4", "li", "it"]
moduleDict = globals()
for tag in htmlTags:
    def func(*args, _thisTag=tag, **kwargs):
        if args:
            return Item(_thisTag, args[0])
        else:
            return Element(_thisTag, **kwargs)
    func.__name__ = tag
    moduleDict[tag] = func
    del func
del moduleDict, htmlTags

print(dir())

if __name__ == '__main__':
    text = r"""
html(*[
    body(*[
        h1('Title'),
        p('text', class_='a'),
        table(*[
            tr(*[
                td(1), td(2)
            ]),
            tr(*[
                td(3), td(4)
            ]),
            tr(*[
                td(6), td(7)
            ]),
        ])
    ])
])
"""
    print(text)
    ob = loads(text)
    text = dumps(ob)
    print(text)
    