# help/template.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from operator import itemgetter
from bloggertool.config.post import Post
from bloggertool.str_util import T

from . import add_topic


out = []
for name, val in sorted(Post.TEMPLATE_VARS.iteritems(), key=itemgetter(0)):
    out.append("{name:<10} - {val}".format(name='{{' + name + '}}', val=val))


var_list = '\n'.join(out)


add_topic('template', T("Recomendations about user template setup"), T("""
Template is used to generate pretty html for local preview.
The problem is: after processing source file by markdown output is "naked"
html. It means absence of <html> and <body> tags, user styles etc.

Use
$ blog info --template path/to/template
to register jinja2 template for making preview.

Perhaps the easiest way to get template with look-and-feel very close
to actual site style is:

- Open any published post in browser.
- Open source for given page. Save it as, for example, template/template.html
    under project root.
- Register template file:
    $ blog info --template <project_dir>/template/template.html
- Open that template/template.html in your preferred editor.

Replace text inside <title> tag to {{title}}, article content to {{inner}}.

For labels you can use construction like
{% for label in labels %}
  <a href='http://<yourblog>.blogspot.com/search/label/{{label}}'
  rel='tag'>{{label}}</a>,
{% endfor %}""") + '\n\n' + T("""

Full list of available template variables:

{var_list}

Complete documentation for jinja2 rendering engine can be found at
http://jinja.pocoo.org/
""")(var_list=var_list))
