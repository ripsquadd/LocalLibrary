from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
]
urlpatterns += [
    url(r'^$', views.index, name='index'),
    url(r'^books/$', views.BookListView.as_view(), name='books'),
]
urlpatterns += [
    url(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
]
urlpatterns += [
    url(r'^author/$', views.AuthorListView.as_view(), name='authors'),
    url(r'^author/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name='author-detail'),
]
urlpatterns += [
    url(r'^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]
