from accounts.decorators import *
from accounts.utils import get_pagination
from .models import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse


@admins_only
@check_permissions('reviews.review_texts_list')
def ReviewTextsList(request):
    review_texts = ReviewText.objects.all().order_by('-created_on')
    if request.GET.get('review'):
        review_texts = review_texts.filter(review__icontains=request.GET.get('review'))
    if request.GET.get('created_on'):
        review_texts = review_texts.filter(created_on__date=request.GET.get('created_on'))
    if request.GET and not review_texts:
        messages.error(request, 'No Data Found')
    return render(request, 'review-texts/texts-list.html', {
        "review_texts":get_pagination(request, review_texts),
        "head_title":"Review Texts Management",
        "review":request.GET.get('review') if request.GET.get('review') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else ""
    })


@admins_only
@check_permissions('reviews.add_review_text')
def AddReviewText(request):
    if request.method == 'POST':
        if ReviewText.objects.filter(review=request.POST.get('review').strip()):
            messages.error(request, 'Review Text already exist')
        else:
            ReviewText.objects.create(review=request.POST.get('review').strip(),created_by=request.user)
            messages.success(request, 'Review Text Added Successfully!')
        return redirect('reviews:review_texts_list')


@admins_only
@check_permissions('reviews.delete_review_text')
def DeleteReviewText(request,id):
    ReviewText.objects.get(id=id).delete()
    messages.success(request, "Review Text Deleted Successfully!")
    return redirect('reviews:review_texts_list')


@admins_only
def GetEditReviewData(request):
    if request.is_ajax():
        review = ReviewText.objects.get(id=request.GET.get('text_id'))
        return JsonResponse({"text":review.review})


@admins_only
@check_permissions('reviews.edit_review_text')
def EditReviewText(request):
    if request.method == 'POST':
        review_text = ReviewText.objects.get(id=request.POST.get('text_id'))
        if ReviewText.objects.filter(review=request.POST.get('review').strip()).exclude(id=review_text.id):
            messages.error(request, 'Review Text already exist')
        else:
            review_text.review=request.POST.get('review').strip()
            review_text.save()
            messages.success(request, 'Review Text Updated Successfully!')
        return redirect('reviews:review_texts_list')