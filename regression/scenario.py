import os
import shutil
import sys

from textwrap import dedent

import jinja2

from .util import Executor, Q

from bloggertool.str_util import qname

email = "andrew.svetlov@gmail.com"
blogid = "1016801571750880882"


def run():
    folder = os.path.dirname(os.path.abspath(sys.argv[0]))
    regr_folder = os.path.join(folder, 'regr-data')
    blog_cmd = 'blog'

    exe = Executor(blog_cmd, regr_folder)
    exe.rmtree()
    exe.mkdir('.')

    project_dir = exe.full_name('sample_blog')

    CREATE_PROJECT = Q("INFO Create project {0!q}")
    ALREADY_IN_PROJECT = Q("ERROR Already a project: {0!q}")
    USER_INFO = Q("""
        INFO User info:
            email: {email!Q}
            blogid: {blogid!Q}
            template:
                dir: {dir!Q}
                file: {file!Q}
            source-encoding: utf-8
        """)
    USER_UPDATED = Q("INFO User updated")
    ADD = Q("INFO Add {name!q} -> {file!q}")

    HTML = Q("INFO Generate html for {name!q}")
    HTML_WARNING_NO_TEMPLATE = HTML + '\n' + Q("""
        WARNING User settings has no template specified.
        Use markdown output as html.
        """)
    SKIP_FRESH = Q("INFO Skip fresh {name!q}")

    ############################################
    print '***** INIT ******'

    print 'init project'
    out = exe.go('init sample_blog')
    #import pdb;pdb.set_trace()
    CREATE_PROJECT(project_dir) == out

    print 'init same project'
    out = exe.go('init sample_blog', 255)
    ALREADY_IN_PROJECT(project_dir) == out

    print 'init sub project'
    out = exe.go('init sample_blog/sample', 255)
    ALREADY_IN_PROJECT(project_dir) == out

    print "init sub project with cd"
    with exe.cd('sample_blog'):
        out = exe.go('init sample', 255)
    ALREADY_IN_PROJECT(project_dir) == out

    shutil.rmtree(project_dir)
    print "init project in current folder"
    exe.mkdir('sample_blog')
    with exe.cd('sample_blog'):
        out = exe.go('init .')
    CREATE_PROJECT(project_dir) == out

    with exe.cd('sample_blog'):
        out = exe.go('ls')
    Q("INFO No posts") == out

    #############################
    print "***** USER *****"

    print "info of empty project"
    with exe.cd('sample_blog'):
        out = exe.go('info')
    #import pdb;pdb.set_trace()
    USER_INFO() == out

    print "fail rinfo for empty user"
    with exe.cd('sample_blog'):
        out = exe.go('rinfo', 255)
    Q("ERROR Set user email first") == out

    print "setup project info"
    with exe.cd('sample_blog'):
        cmd = 'info --email %s --blogid %s' % (email, blogid)
        out = exe.go(cmd)
    USER_UPDATED == out

    print "info of filled project"
    with exe.cd('sample_blog'):
        out = exe.go('info')
    USER_INFO(email=email, blogid=blogid) == out

    ###############################
    print "*********** rinfo ************"

    print "simple"
    with exe.cd('sample_blog'):
        out = exe.go('rinfo')
    found = False
    for m in Q(r"[[](?P<blogid>\d+)]").ifind(out):
        if m['blogid'] == blogid:
            found = True
            break
    assert found

    ##############################
    print "****** SIMPLE HTML *******"

    TXT = 'Text of sample article'
    INNER_HTML = '<p>' + TXT + '</p>'

    print "add post"
    with exe.cd('sample_blog'):
        exe.write('article.rst', TXT)
        rst_fname = exe.full_name('article.rst')
        out = exe.go('add article.rst')
    ADD(name='article', file='article.rst') == out

    print "generate html without template"
    with exe.cd('sample_blog'):
        out = exe.go('html article.rst')
        Q(INNER_HTML) == exe.read('article.inner.html')
    HTML_WARNING_NO_TEMPLATE(name='article', file=rst_fname) == out

    print "generate fresh html without template"
    with exe.cd('sample_blog'):
        out = exe.go('html article.rst')
        Q(INNER_HTML) == exe.read('article.inner.html')
    SKIP_FRESH(name='article') == out

    print "generate fresh html with --always parameter without template"
    with exe.cd('sample_blog'):
        out = exe.go('html article.rst --always')
        Q(INNER_HTML) == exe.read('article.inner.html')
    HTML_WARNING_NO_TEMPLATE(name='article', file=rst_fname) == out

    ###########################################
    print "******* TEMPLATED HTML *******"

    TEMPLATE_BODY = Q("""\
        <html>
          <head>
            <title>{{title}}</title>
          </head>
          <body>
            <h1>{{title}}</h1>
            <p>Slug: <em>{{slug}}</em></p>
            <p>Labels: <em>
            {% for label in labels %}
              {{label}},
            {% endfor %}
            <hr>
            {{inner}}
          </body>
        </html>
        """)

    env = jinja2.Environment(loader=jinja2.DictLoader(
        {"template": TEMPLATE_BODY}))
    TEMPLATE = env.get_template("template")

    print "setup project template"
    with exe.cd('sample_blog'):
        exe.mkdir('template')
        exe.write('template/templ.html', TEMPLATE_BODY)
        out = exe.go('info --template template/templ.html')
    USER_UPDATED == out

    print "info of filled project"
    with exe.cd('sample_blog'):
        out = exe.go('info')
    USER_INFO(email=email, blogid=blogid,
              dir='template', file='templ.html') == out

    print ("generate html with template without title and slug, "
           "slug derived from name")
    with exe.cd('sample_blog'):
        out = exe.go('html article.rst --always')
        inner = exe.read('article.inner.html')
        INNER_HTML == inner
        TEMPLATE.render(title='', inner=inner,
                        slug='article', labels=[]) == exe.read('article.html')
    HTML(name='article') == out

    #########################
    print "******* TEMPLATED HTML WITH METAINFO **********"

    TXT2 = Q("""\
        Title: Post Title
        Slug: second-post
        Labels: sample, other

        Text of second article
        """)
    INNER_HTML2 = '<p>Text of second article</p>'

    print "add second post in subfolder"
    exe.mkdir('sample_blog/sub')
    with exe.cd('sample_blog/sub'):
        exe.write('second.rst', TXT2)
        out = exe.go('add second.rst --show-traceback')
    ADD(name='sub/second', file='sub/second.rst') == out

    print "generate html with template with full metadata"
    with exe.cd('sample_blog/sub'):
        out = exe.go('html second --force', 0)
        inner = exe.read('second.inner.html')
        INNER_HTML == inner
        TEMPLATE.render(title='Post Title', inner=inner,
                        slug='second-post',
                        labels='other, sample') == exe.read('second.html')
    HTML(name='sub/second') == out

    #########################
    print "******** LABELS ***********"

    LABEL = Q('INFO Labels for post {name!q}: {labels}')
    LABEL_UPDATE = Q('INFO Updated labels for post {name!q}: {labels}')

    print "show empty labels for article.rst"
    with exe.cd('sample_blog'):
        out = exe.go('label article')
    LABEL(name='article', labels=None) == out

    print "show empty labels for article.rst from sub folder"
    with exe.cd('sample_blog/sub'):
        out = exe.go('label ../article')
    LABEL(name='article', labels=None) == out

    print "show labels for sub/second.rst"
    with exe.cd('sample_blog'):
        out = exe.go('label sub/second')
    LABEL(name='sub/second', labels='other, sample') == out

    print "show labels for sub/second.rst from sub folder"
    with exe.cd('sample_blog/sub'):
        out = exe.go('label second')
    LABEL(name='sub/second', labels='other, sample') == out

    print "add label for article.rst"
    with exe.cd('sample_blog'):
        out = exe.go('label article --add "a, b"')
    LABEL_UPDATE(name='article', labels='a, b') == out

    print "...check"
    with exe.cd('sample_blog'):
        out = exe.go('label article')
    LABEL(name='article', labels='a, b') == out

    print "remove label from article.rst"
    with exe.cd('sample_blog'):
        out = exe.go('label article --rm "a"')
    LABEL_UPDATE(name='article', labels='b') == out

    print "...check"
    with exe.cd('sample_blog'):
        out = exe.go('label article')
    LABEL(name='article', labels='b') == out

    print "set label for article.rst"
    with exe.cd('sample_blog'):
        out = exe.go('label article --set a')
    LABEL_UPDATE(name='article', labels='a') == out

    print "...check"
    with exe.cd('sample_blog'):
        out = exe.go('label article')
    LABEL(name='article', labels='a') == out

    #################################
    print "*********** POST **************"

    POST_SHOW = Q("""\
        INFO Post {changed}{name!q}
            title: {title}
            link: {link}
            slug: {slug}
            labels: {labels}
            postid: {postid}
            published: {published}
            updated: {updated}
            localstamp: now
    """)
    LOCALSTAMP = "(?P<localstamp>.+?)$"
    POST_UPDATE = Q('INFO Post {name} updated.')
    POST_UPDATE_WARNING = Q("WARNING Skip title modification for {name}")

    print 'show post article'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='',
              changed='[*]',  # screen * regexp spec symbol
              link='',
              slug='article',
              labels='a',
              postid='').match(out)

    print 'set title for post article'
    with exe.cd('sample_blog'):
        out = exe.go('post article --title "New Title" --show-traceback')
    POST_UPDATE(name='article') == out

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='New Title',
              changed='[*]',  # screen * regexp spec symbol
              link='',
              slug='article',
              labels='a',
              postid='').match(out)

    print 'cannot change existing title for post article'
    with exe.cd('sample_blog'):
        out = exe.go('post article --title "New Title 2"')
    POST_UPDATE_WARNING(name='article') == out

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='New Title',
              changed='[*]',  # screen * regexp spec symbol
              link='',
              slug='article',
              labels='a',
              postid='').match(out)

    print 'change existing title for post article with --force'
    with exe.cd('sample_blog'):
        out = exe.go('post article --title "New Title 2" --force')
    POST_UPDATE(name='article') == out

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='New Title 2',
              changed='[*]',  # screen * regexp spec symbol
              link='',
              slug='article',
              labels='a',
              postid='').match(out)

    #################################
    print "************ LS *************"

    print "ls of project root"
    with exe.cd('sample_blog'):
        out = exe.go('ls')
    Q("""\
        INFO Posts:
        *article
        *sub/second
        """) == out

    print "ls of sample/sub"
    with exe.cd('sample_blog/sub'):
        out = exe.go('ls')
    Q("""\
        INFO Posts:
        *sub/second
        """) == out

    ###############################
    PUBLISH = Q("INFO Post {name!q} published as (?P<link>.+) "
                r"[[](?P<postid>\d+)]")

    print "*********** publish ************"
    print "publish article"
    with exe.cd('sample_blog'):
        out = exe.go('publish article')
    ret = PUBLISH(name='article').match(out)
    link1 = ret['link']
    postid1 = ret['postid']
    slug1 = os.path.splitext(os.path.basename(link1))[0]

    print "...check"
    with exe.cd('sample_blog'):
        out = exe.go('ls')
    Q("""\
        INFO Posts:
        article
        *sub/second
        """) == out

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='New Title 2',
              changed='',
              link=link1,
              slug=slug1,
              labels='a',
              published='now',
              updated='now',
              postid=postid1).match(out)

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('rls  --show-traceback')
    tst = Q("{title!q} -> {link}")(title="New Title 2", link=link1)
    last_record = out.splitlines()[2].strip()
    tst == last_record

    ####
    print "publish sub/second"
    with exe.cd('sample_blog/sub'):
        out = exe.go('publish second')
    ret = PUBLISH(name='sub/second').match(out)
    link2 = ret['link']
    postid2 = ret['postid']
    slug2 = os.path.splitext(os.path.basename(link2))[0]

    print "...check"
    with exe.cd('sample_blog'):
        out = exe.go('ls')
    Q("""\
        INFO Posts:
        article
        sub/second
        """) == out

    print '...check'
    with exe.cd('sample_blog/sub'):
        out = exe.go('post second')
    POST_SHOW(name='sub/second',
              title='Post Title',
              changed='',
              link=link2,
              slug=slug2,
              labels='other, sample',
              published='now',
              updated='now',
              postid=postid2).match(out)

    print '...check'
    with exe.cd('sample_blog/sub'):
        out = exe.go('rls  --show-traceback')
    tst = Q("{title!q} -> {link}")(title="Post Title", link=link2)
    last_record = out.splitlines()[2].strip()
    tst == last_record

    ######################
    print "************ RM *****************"

    RM = Q("INFO Remove {name!q}")

    print 'rm article and sub/second'
    with exe.cd('sample_blog/sub'):
        out = exe.go('rm ../article')
        RM(name='article') == out

        out = exe.go('rm second')
        RM(name='sub/second') == out

    with exe.cd('sample_blog'):
        out = exe.go('ls')
    Q("INFO No posts") == out

    ######################
    print "************ LINK *****************"

    LINK = Q("INFO Post {name!q} connected to {link}")

    published = r"(?P<published>now|\d+ minutes ago)"

    print 'add removed files'
    with exe.cd('sample_blog/sub'):
        exe.go('add ../article.rst')
        exe.go('add second.rst')

    print 'link article'
    with exe.cd('sample_blog/sub'):
        out = exe.go('link ../article %s' % link1)
        LINK(name='article', link=link1) == out

    print '...check'
    with exe.cd('sample_blog'):
        out = exe.go('post article')
    POST_SHOW(name='article',
              title='New Title 2',
              changed='',
              link=link1,
              slug=slug1,
              labels='a',
              published=published,
              updated='now',
              postid=postid1).match(out)

    print 'link sub/second'
    with exe.cd('sample_blog/sub'):
        out = exe.go('link second %s' % link2)
        LINK(name='sub/second', link=link2) == out

    print '...check'
    with exe.cd('sample_blog/sub'):
        out = exe.go('post second')
    POST_SHOW(name='sub/second',
              title='Post Title',
              changed='',
              link=link2,
              slug=slug2,
              labels='other, sample',
              published=published,
              updated='now',
              postid=postid2).match(out)

    print "**************** DIFF and PUSH **************"

    TXT3 = Q("""\
        Title: Post Title
        Slug: {slug}
        Labels: sample, other

        Text of second article.
        Modified version.
        """)(slug=slug2)

    DIFF = Q("""\
        INFO Generate html for sub/second
        INFO Difference:
        --- {link}

        +++ {inner}

        @@ -1,1 +1,2 @@

        -<p>Text of second article</p>
        +<p>Text of second article.
        +Modified version.</p>
        """)

    PUSH = Q("INFO Post {name!q} updated")

    print "modify and diff"
    with exe.cd('sample_blog/sub'):
        exe.write('second.rst', TXT3)
        out = exe.go('diff second --force')
    DIFF(link=link2 + ' ', inner='sub/second.inner.html ') == out

    print "push"
    with exe.cd('sample_blog/sub'):
        out = exe.go('push second')
    PUSH(name='sub/second') == out

    print "check diff again"
    with exe.cd('sample_blog/sub'):
        out = exe.go('diff second')
    Q("INFO No differences") == out
