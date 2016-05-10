import json

import markdown
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from ception.activities.models import Activity
from ception.articles.forms import ArticleForm, VersionForm
from ception.articles.merge import summary_edit
from ception.articles.models import Article, Tag, ArticleComment, ArticleVersion, ArticleSentenceComment
from ception.articles.utils import convert_period_to_pd
from ception.decorators import ajax_required
from diff_parser import DiffParser
from merge import merge_edit
from simple_parser import CleanParser, FormalParser
from utils import stadardlize_text


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
            article.content = form.cleaned_data.get('content').replace('\n', '').replace("\r", "")
            article.content, article.sentence_count = convert_period_to_pd(article.content)
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
                html = u'{0}{1}'.format(html, render_to_string('articles/partial/partial_article_comment.html',
                                                               {'comment': comment}))
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()
    except Exception, e:
        return HttpResponseBadRequest()


# ========================== Editing View ==================================

origin_authors = ["scyue", "ZYShin", "shawn"]

def init_edit_page(request, id, compare=False):
    article = get_object_or_404(Article, pk=id)
    version = article.get_or_create_version_by_user(request.user)
    form = VersionForm(instance=version)
    versions = ArticleVersion.get_versions(version.origin)
    version_jsons = []
    authors = []
    version_array = []
    current_version_dict = {}
    for v in versions:
        dict_data = {
            'comments': v.get_sentence_comments(),
            'vote': v.get_sentence_vote(request.user),
            'info': v.info_array_json,
            'author': v.edit_user.profile.get_screen_name(),
            'id': v.pk,
            'time': naturaltime(v.edit_date)
        }
        if v.edit_user == request.user:
            current_version_dict = dict_data
        else:
            v_dict = dict_data
            authors.append(v.edit_user)
            version_jsons.append(json.dumps(v_dict))
            version_array.append(v)

    pass_data = {
        'json': version_jsons,
        'authors': authors,
        'versions': version_array,
        'current_version_json': json.dumps(current_version_dict),
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
                html = u"{0}{1}".format(html, render_to_string('articles/partial/partial_sentence_comment.html',
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


@login_required
@ajax_required
def merge_api(request):
    if request.method == 'POST':
        try:
            user_sen = request.POST['sen_A']
            other_sen = request.POST['sen_B']
            sentence_id = int(request.POST['sen_id'])
            version_id = int(request.POST['ver_id'])
            if version_id >= 0:
                version = get_object_or_404(ArticleVersion, pk=version_id)
                origin_sentences = version.origin.get_sentences()
                origin_clean = origin_sentences[sentence_id]
            else:
                origin_clean = "This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.\n"
            user_clean = CleanParser.get_clean_text(user_sen)
            other_clean = CleanParser.get_clean_text(other_sen)
            html_str, data, conflicted = merge_edit(origin_clean, user_clean, other_clean)
            result_json = {
                'str': html_str,
                'data': data,
                'conflicted': conflicted
            }
            return HttpResponse(json.dumps(result_json))
        except Exception, e:
            print repr(e)
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def merge_second_stage(request):
    if request.method == 'POST':
        content = request.POST['content']
        sentence = request.POST['sentence']
        sid = int(request.POST['sen_id'])
        start_pos = 0
        if sid > 1:
            start_flag = content.find('sid="' + str(sid - 1))
            start_pos = content.find('</pd>', start_flag) + 5
        print start_pos
        end_flag = content.find('sid="' + str(sid))
        end_pos = content.rfind('<pd', None, end_flag)
        formal_sentence = FormalParser.get_formal_text(sentence)
        merged_content = content[:start_pos] + formal_sentence + content[end_pos:]
        return HttpResponse(json.dumps({'content': merged_content, 'formal': formal_sentence}))
    else:
        return HttpResponseBadRequest()


@login_required
def diff_test(request):
    test_str = "This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin."
    if request.method == 'POST':
        cp = CleanParser()
        cp.feed(stadardlize_text(request.POST["content"][:-1]))
        result = DiffParser.diff(test_str, cp.clean_sentence)
        return HttpResponse(result)
    else:
        return render(request, 'articles/tests/diff_view.html', {'content': test_str})


@login_required
def summary_test(request):
    if request.method == 'POST':
        sentence_list = json.loads(request.POST['sen_list'])
        article_pk = request.POST['art_id']
        sentence_id = request.POST['sen_id']
        print sentence_list
        html_str, data, conflicted = summary_edit(sentence_list)
        result_json = {
            'str': html_str,
            'data': data,
            'conflicted': conflicted
        }
        return HttpResponse(json.dumps(result_json))
    else:
        article_array = []
        for a in Article.objects.all():
            version_array = []
            # print '======================='
            for v in ArticleVersion.objects.filter(origin=a).order_by('edit_user__username'):
                # print v.edit_user
                version_array.append(v.info_array_json)
            article_array.append(version_array)
        return render(request, 'articles/tests/summary_view.html', {'data': json.dumps(article_array)})
