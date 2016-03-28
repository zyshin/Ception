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
from ception.activities.models import Activity
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime
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
            article.description = markdown.markdown(form.cleaned_data.get('description'))
            status = form.cleaned_data.get('status')
            if status in [Article.PUBLISHED, Article.DRAFT]:
                article.status = form.cleaned_data.get('status')
            article.save()
            tags = form.cleaned_data.get('tags')
            article.create_tags(tags)
            return redirect('/articles/')
    else:
        form = ArticleForm()
    try:
        return render(request, 'articles/write.html', {'form': form})
    except Exception, e:
        print e
        return HttpResponseBadRequest()


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
def drafts(request):
    drafts = Article.objects.filter(create_user=request.user, status=Article.DRAFT)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


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


# ========================== Editing View ==================================


def get_origin_info(version):
    origin_dict, origin_edit, origin_delete = ContentParser.get_info(version.origin.content)
    editing_info_dict = origin_dict["sentence"]
    origin_count = origin_dict["counter"]
    for d in editing_info_dict:
        d["edit"] = 0
        d["delete"] = 0
        if len(d['content']) > 45:
            d['content'] = d['content'][:42] + "..."
    return editing_info_dict, origin_count


def process_sentences(sentences, origin_count, v_edit):
    size = len(sentences)
    for i in xrange(size):
        s = sentences[i]
        s["edited"] = v_edit[s["id"]]
        s["added"] = False
        if s["id"] >= origin_count:
            s["id"] = -8080
            s["added"] = True
            s["content"] = s["content"].replace("<ins >", "")

    for i in xrange(size):
        s = sentences[i]
        if s["added"]:
            continue
        if i > 0 and sentences[i - 1]["added"]:
            s["edited"] = True
            index = i - 1
            while index >= 0 and sentences[index]["added"]:
                s["content"] = "<add>" + sentences[index]["content"] + "</add>" + s["content"]
                index -= 1
        if i < size - 1 and sentences[i + 1]["added"]:
            s["edited"] = True
            index = i + 1
            while index < size and sentences[index]["added"]:
                s["content"] += "<add>" + sentences[index]["content"] + "</add>"
                index += 1


authors = ["scyue", "ZYShin", "shawn"]


def init_edit_page(request, id, compare=False):
    article = get_object_or_404(Article, pk=id)
    version = article.get_or_create_version_by_user(request.user)
    editing_info_dict, origin_count = get_origin_info(version)
    form = VersionForm(instance=version)
    versions = ArticleVersion.get_versions(version.origin)
    this_dict, this_edit, this_delete = ContentParser.get_info(version.content)
    version_jsons = []
    authors = []
    version_array = []
    for v in versions:
        if v.edit_user == request.user:
            continue
        # if v.edit_user.username not in authors:
        #     continue
        v_dict, v_edit, v_delete = ContentParser.get_info(v.content)
        for i in xrange(origin_count):
            editing_info_dict[i]["edit"] += v_edit[i]
            editing_info_dict[i]["delete"] += v_delete[i]
        process_sentences(v_dict['sentence'], origin_count, v_edit)
        v_dict['author'] = str(v.edit_user)
        v_dict['id'] = v.pk
        v_dict['time'] = naturaltime(v.edit_date)
        authors.append(v.edit_user)
        version_jsons.append(json.dumps(v_dict))
        version_array.append(v)

    pass_data = {
        'json': version_jsons,
        'authors': authors,
        'counter': this_dict["counter"],
        'origin_count': origin_count,
        'editing_info': [json.dumps(d) for d in editing_info_dict],
        'versions': version_array
    }
    if not compare:
        return render(request, 'articles/edit.html', {'form': form, 'data': pass_data})
    else:
        return render(request, 'articles/edit_compare.html', {'form': form, 'data': pass_data})


@login_required
def edit(request, id):
    try:
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "save":
                return HttpResponse("Not Implemented")
            elif action == "commit":
                version = get_object_or_404(ArticleVersion, pk=id)
                form = VersionForm(request.POST, instance=version)
                if form.is_valid():
                    form.save()
                return HttpResponse("Success")
        else:
            return init_edit_page(request, id)
    except Exception, e:
        print "Exception-Edit: ", e
        return HttpResponseBadRequest()


@login_required
def edit_compare(request, id):
    try:
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "save":
                return HttpResponse("Not Implemented")
            elif action == "commit":
                version = get_object_or_404(ArticleVersion, pk=id)
                form = VersionForm(request.POST, instance=version)
                if form.is_valid():
                    form.save()
                return HttpResponse("Success")
        else:
            return init_edit_page(request, id, True)
    except Exception, e:
        print "Exception-EditCompare: ", e
        return HttpResponseBadRequest()


@login_required
@ajax_required
def sentence_comments(request):
    try:
        if request.method == 'POST':
            version_id = int(request.POST.get('version_id'))
            sentence_id = int(request.POST.get('sentence_id'))
            version = ArticleVersion.objects.get(pk=version_id)
            if request.POST.has_key('sentence-comment'):
                comment = request.POST.get('sentence-comment').strip()
                if len(comment) > 0:
                    sentence_comment = ArticleSentenceComment(parent=version, sentence_id=sentence_id,
                                                              user=request.user, comment=comment)
                    sentence_comment.save()
            html = u''
            for comment in ArticleSentenceComment.objects.filter(parent=version, sentence_id=sentence_id):
                html = u"{0}{1}".format(html, render_to_string('articles/partial_sentence_comment.html',
                                                               {'comment': comment}))
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except Exception, e:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def sentence_vote(request):
    try:
        if request.method == 'POST':
            version_id = request.POST.get('version_id')
            sentence_id = request.POST.get('sentence_id')
            version = ArticleVersion.objects.get(pk=version_id)
            user = request.user
            activity = Activity.objects.filter(Q(activity_type=Activity.UP_VOTE) | Q(activity_type=Activity.DOWN_VOTE),
                                               user=user, sentence_id=sentence_id, version_id=version_id)
            user_state = "N"
            if request.POST.has_key('vote'):
                vote = request.POST['vote']
                if activity:
                    activity.delete()
                if vote in [Activity.UP_VOTE, Activity.DOWN_VOTE]:
                    activity = Activity(activity_type=vote, user=user, sentence_id=sentence_id, version_id=version_id)
                    activity.save()
                return HttpResponse(version.get_votes(sentence_id))
            else:
                if activity:
                    user_state = activity.first().activity_type
                return HttpResponse(json.dumps({'count': version.get_votes(sentence_id), 'state': user_state}))
        else:
            return HttpResponseBadRequest()
    except:
        return HttpResponseBadRequest()
