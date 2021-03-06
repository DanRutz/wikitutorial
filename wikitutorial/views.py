from docutils.core import publish_parts
import re

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config # <- ALREADY THERE

from wikitutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='.models.Wiki')
def view_wiki(context, request):
    return HTTPFound(location=request.resource_url(context, 'FrontPage'))

@view_config(context='.models.Page', renderer='templates/view.pt')
def view_page(context, request):
    wiki = context.__parent__

    def check(match):
        word = match.group(1)
        if word in wiki:
            page = wiki[word]
            view_url = request.resource_url(page)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.application_url + '/add_page/' + word
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(
        context.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    bodz = context.datb
    edit_url = request.resource_url(context, 'edit_page')
    return dict(page=context, content=content, bodz=bodz, edit_url=edit_url)

@view_config(name='edit_page', context='.models.Page',
             renderer='templates/edit.pt')
def edit_page(context, request):
    # f = open(r'C:\2\request.txt', 'a')
    # f.write('\n\n\n\n%s\n' % 'dir(request       ).__str__()')
    # f.write(                  dir(request       ).__str__() )
    # f.write('\n\n\n\n%s\n' % 'dir(request.method).__str__()')
    # f.write(                  dir(request.method).__str__() )
    # f.write('\n\n\n\n%s\n' % '    request.method           ')
    # f.write(                      request.method            )
    # f.close()
    if 'form.submitted' in request.params and request.method == "POST":
        context.data = request.params['body']
        context.datb = request.params['bodz']
        return HTTPFound(location = request.resource_url(context))

    return dict(page=context,
                save_url=request.resource_url(context, 'edit_page'))

@view_config(name='add_page', context='.models.Wiki',
             renderer='templates/edit.pt')
def add_page(context, request):
    pagename = request.subpath[0]
    if 'form.submitted' in request.params and request.method == "POST":
        body = request.params['body']
        bodz = request.params['bodz']
        page = Page(body, bodz)
        page.__name__ = pagename
        page.__parent__ = context
        context[pagename] = page
        return HTTPFound(location = request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', pagename)
    page = Page('', '')
    page.__name__ = pagename
    page.__parent__ = context
    return dict(page=page, save_url=save_url)

# from .models import MyModel
# 
# 
# @view_config(context=MyModel, renderer='templates/mytemplate.pt')
# def my_view(request):
#     return {'project': 'wikitutorial'}
