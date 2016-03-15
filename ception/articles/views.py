from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, Http404
from ception.articles.models import Article, Tag, ArticleComment, ArticleVersion, ArticleSentenceComment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ception.articles.forms import ArticleForm, VersionForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from ception.decorators import ajax_required
import markdown
from django.template.loader import render_to_string
from ception.articles.utils import ContentParser, convert_period_to_pd
import json

def _articles(request, articles):
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    popular_tags = Tag.get_popular_tags()
    return render(request, 'articles/articles.html', {
        'articles': articles,
        'popular_tags': popular_tags
    })

@login_required
def articles(request):
    all_articles = Article.get_published()
    return _articles(request, all_articles)

@login_required
def article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    versions = ArticleVersion.get_versions(article)
    return render(request, 'articles/article.html', {'article': article, 'versions': versions})

@login_required
def tag(request, tag_name):
    tags = Tag.objects.filter(tag=tag_name)
    articles = []
    for tag in tags:
        if tag.article.status == Article.PUBLISHED:
            articles.append(tag.article)
    return _articles(request, articles)

@login_required
def write(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = Article()
            article.create_user = request.user
            article.title = form.cleaned_data.get('title')
            article.content = form.cleaned_data.get('content').replace('\n', '').replace("'", "\\'").replace("\r", "")
            article.content = convert_period_to_pd(article.content)
            status = form.cleaned_data.get('status')
            if status in [Article.PUBLISHED, Article.DRAFT]:
                article.status = form.cleaned_data.get('status')
            article.save()
            tags = form.cleaned_data.get('tags')
            article.create_tags(tags)
            return redirect('/articles/')
    else:
        form = ArticleForm()
    return render(request, 'articles/write.html', {'form': form})

@login_required
def drafts(request):
    drafts = Article.objects.filter(create_user=request.user, status=Article.DRAFT)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


def edit_logic(request, version):
    print "This is edit logic"
    if request.POST:
        form = VersionForm(request.POST, instance=version)
        if form.is_valid():
            form.save()
    else:
        form = VersionForm(instance=version)
    print "1"

    versions = ArticleVersion.get_versions(version.origin)
    version_jsons = []
    authors = []
    this_dict = ContentParser.getJSON(version.content.replace("&nbsp;", " "))
    print "2"
    for v in versions:
        if v.edit_user == request.user:
            continue
        v_dict = ContentParser.getJSON(v.content.replace("&nbsp;", " "))
        v_dict['author'] = str(v.edit_user)
        v_dict['id'] = v.pk
        authors.append(str(v.edit_user))
        version_jsons.append(json.dumps(v_dict))
        # print v_dict
        # print v.content
        # print "*************************************"
    print "3"
    pass_data = {
        'json': version_jsons,
        'authors': authors,
        'counter': this_dict["counter"],
    }
    return render(request, 'articles/edit.html', {'form': form, 'data': pass_data})


@login_required
def edit(request, id):
    print "This is edit"

    if id:
        article = get_object_or_404(Article, pk=id)
    else:
        return HttpResponseBadRequest(request)
    version_set = ArticleVersion.objects.filter(edit_user=request.user, origin=article)
    if len(version_set) == 0:
        version = ArticleVersion()
        version.edit_user = request.user
        version.content = article.content
        version.origin = article
        version.save()
    else:
        version = version_set[0]
    print "-2"
    return edit_logic(request, version)



@login_required
def edit_version(request, id):
    print "This is edit version"
    if id:
        version = get_object_or_404(ArticleVersion, pk=id)
    else:
        return HttpResponseBadRequest(request)
    return edit_logic(request, version)


@login_required
@ajax_required
def preview(request):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            html = 'Nothing to display :('
            if len(content.strip()) > 0:
                html = markdown.markdown(content, safe_mode='escape')
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except Exception, e:
        return HttpResponseBadRequest()

@login_required
@ajax_required
def comment(request):
    try:
        if request.method == 'POST':
            article_id = request.POST.get('article')
            article = Article.objects.get(pk=article_id)
            comment = request.POST.get('comment')
            comment = comment.strip()
            if len(comment) > 0:
                article_comment = ArticleComment(user=request.user, article=article, comment=comment)
                article_comment.save()
            html = u''
            for comment in article.get_comments():
                html = u'{0}{1}'.format(html, render_to_string('articles/partial_article_comment.html', {'comment': comment}))
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except Exception, e:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def sentence_return(request):
    try:
        if request.method == 'GET':
            version_id = request.GET.get('version_id')
            version = ArticleVersion.objects.get(pk=version_id)
            sentence_id = request.GET.get('sentence_id')
            # print "GET:", version, sentence_id
            html = u''
            # for v in ArticleSentenceComment.objects.all():
            #     print v.parent, v.sentence_id
            # print ArticleSentenceComment.objects.filter(parent=version, sentence_id=sentence_id)
            for comment in ArticleSentenceComment.objects.filter(parent=version, sentence_id=sentence_id):
                html = u'{0}{1}'.format(html, render_to_string('articles/partial_article_comment.html', {'comment': comment}))
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except:
        return HttpResponseBadRequest()

@login_required
@ajax_required
def sentence_comment(request):
    try:
        if request.method == 'POST':

            version_id = request.POST.get('version_id')
            version = ArticleVersion.objects.get(pk=version_id)
            sentence_id = request.POST.get('sentence_id')

            comment = request.POST.get('sentence-comment').strip()
            print "=*=*=*=*"
            if len(comment) > 0:
                sentence_comment = ArticleSentenceComment(parent=version, sentence_id=sentence_id, user=request.user, comment=comment)
                print sentence_comment
                sentence_comment.save()
            html = u''
            for comment in ArticleSentenceComment.objects.filter(parent=version, sentence_id=sentence_id):
                html = u'{0}{1}'.format(html, render_to_string('articles/partial_article_comment.html', {'comment': comment}))
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except Exception, e:
        print e
        return HttpResponseBadRequest()


