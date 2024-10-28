import jdatetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from article_module.models import Article, ArticleCategory, ArticleComment


class ArticlesListView(ListView):
    model = Article
    paginate_by = 6
    template_name = 'article_module/article.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArticlesListView, self).get_context_data(*args, **kwargs)
        context['latest_articles'] = self.get_queryset()[:3]
        articles_with_comments = []
        for article in context['object_list']:
            article.comment_count = ArticleComment.objects.filter(article=article).count()
            articles_with_comments.append(article)
        context['object_list'] = articles_with_comments
        return context

    def get_queryset(self):
        query = super(ArticlesListView, self).get_queryset()

        query = query.filter(is_active=True)
        category_name = self.kwargs.get('category')
        if category_name is not None:
            query = query.filter(selected_categories__url_title__iexact=category_name)
        return query


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_module/article_detail.html'

    def get_queryset(self):
        query = super(ArticleDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data()
        article: Article = kwargs.get('object')
        comments = ArticleComment.objects.filter(article_id=article.id, parent=None).order_by(
            '-create_date').prefetch_related('articlecomment_set')
        for comment in comments:
            date_persian = comment.create_date
            formatted_datetime = jdatetime.datetime.fromgregorian(datetime=date_persian).strftime('%H:%M  %Y/%m/%d')
            comment.formatted_datetime = formatted_datetime

        context['comments'] = comments
        context['comments_count'] = ArticleComment.objects.filter(article_id=article.id).count()
        latest_articles = Article.objects.filter(is_active=True).order_by('-create_date')

        for article in latest_articles:
            # Convert the Gregorian date to Jalali
            gregorian_date = article.create_date
            jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
            print(jalali_date)
            article.formatted_date = jalali_date.strftime('%d %B %Y')
            persian_months = {
                'Farvardin': 'فروردین',
                'Ordibehesht': 'اردیبهشت',
                'Khordad': 'خرداد',
                'Tir': 'تیر',
                'Mordad': 'مرداد',
                'Shahrivar': 'شهریور',
                'Mehr': 'مهر',
                'Aban': 'آبان',
                'Azar': 'آذر',
                'Dey': 'دی',
                'Bahman': 'بهمن',
                'Esfand': 'اسفند'
            }
            for eng, persian in persian_months.items():
                article.formatted_date = article.formatted_date.replace(eng, persian)
                print('read', latest_articles)
        context['latest_articles'] = latest_articles
        context['article_main_categories'] = ArticleCategory.objects.prefetch_related('articlecategory_set').filter(
            is_active=True,
            parent_id=None)
        return context


# def article_categories_component(request: HttpRequest):
#     article_main_categories = ArticleCategory.objects.prefetch_related('articlecategory_set').filter(is_active=True, parent_id=None)
#
#     context = {
#         'main_categories': article_main_categories
#     }
#     return render(request, 'article_module/components/article_categories_component.html', context)


def add_article_comment(request: HttpRequest):
    # if request.user.is_authenticated:
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        article_comment = request.POST.get('article_comment')
        parent_id = request.POST.get('parent_id')
        email = request.POST.get('email')
        name = request.POST.get('name')

        # ثبت نظر جدید
        new_comment = ArticleComment(article_id=article_id, text=article_comment, email=email,
                                     parent_id=parent_id,name=name)
        new_comment.save()

        # پس از ذخیره نظر، کاربر را به صفحه‌ی مقاله هدایت کنید
        return redirect('articles_detail', pk=article_id)  # باید به جای article_id از pk استفاده کنید

        # در غیر این صورت، اگر درخواست POST نباشد، صفحه‌ی قبلی نمایش داده می‌شود
    return render(request, 'article_module/article_detail.html')
