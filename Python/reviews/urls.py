from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'reviews'


urlpatterns = [

    re_path(r'review-texts-list/$',ReviewTextsList,name="review_texts_list"),
    re_path(r'add-review-text/$',AddReviewText,name="add_review_text"),
    re_path(r'get-editreview-data/$',GetEditReviewData,name="get_editreview_data"),
    re_path(r'edit-review-text/$',EditReviewText,name="edit_review_text"),
    re_path(r'delete-review-text/(?P<id>[-\w]+)/$',DeleteReviewText,name="delete_review_text"),

]
