from accounts.decorators import *
from accounts.utils import get_pagination
from .models import *
from django.contrib import messages
from django.shortcuts import redirect, render


@admins_only
@check_permissions('page.pages_list')
def PagesListView(request):
    pages = Pages.objects.all().order_by('-updated_on')
    if request.GET.get('id'):
        pages = pages.filter(id=request.GET.get('id'))
    if request.GET.get('title'):
        pages = pages.filter(title__icontains=request.GET.get('title'))
    if request.GET.get('content'):
        pages = pages.filter(content__icontains=request.GET.get('content'))
    if request.GET.get('type_id'):
        pages = pages.filter(type_id=request.GET.get('type_id'))
    if request.GET.get('created_on'):
        pages = pages.filter(created_on__date=request.GET.get('created_on'))

    if request.GET and not pages:
        messages.error(request, 'No Data Found')
    return render(request, 'StaticPages/pages-list.html',{
        "pages":get_pagination(request,pages),
        "head_title":"Pages",
        "id":request.GET.get('id') if request.GET.get('id') else "",
        "title":request.GET.get('title') if request.GET.get('title') else "",
        "content":request.GET.get('content') if request.GET.get('content') else "",
        "type_id":request.GET.get('type_id') if request.GET.get('type_id') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('page.add_page')
def AddPageView(request):
    if request.method == 'POST':
        if Pages.objects.filter(type_id = request.POST.get("type_id")):
            messages.error(request, 'Page Already Exists!')
            return render(request, 'StaticPages/add-page.html',{"title":request.POST.get("title"),"content":request.POST.get("content"),"type_id":request.POST.get("type_id"),"head_title":"Pages"})
        page = Pages.objects.create(
            title=request.POST.get("title"),
            type_id=request.POST.get("type_id"),
            content=request.POST.get("content").strip()
        )
        messages.error(request, 'Page Add Successfully!')
        return redirect('page:view_page',id=page.id)
    return render(request, 'StaticPages/add-page.html',{"head_title":"Pages"})


@admins_only
@check_permissions('page.delete_page')
def DeletePage(request,id):
    Pages.objects.get(id=id).delete()
    messages.error(request, 'Page Deleted Successfully!')
    return redirect('page:pages_list')


@admins_only
@check_permissions('page.view_page')
def ViewPage(request,id):
    page = Pages.objects.get(id=id)
    return render(request, 'StaticPages/view-page.html',{"page":page,"head_title":"Pages"})


@admins_only
@check_permissions('page.edit_page')
def EditPage(request,id):
    page = Pages.objects.get(id=id)
    if request.method == 'POST':
        if request.POST.get("title"):
            page.title = request.POST.get("title")
        if request.POST.get("content"):
            page.content = request.POST.get("content").strip()
        page.save()
        messages.error(request, 'Page Updated Successfully!')
        return redirect('page:view_page',id=page.id)
    return render(request, 'StaticPages/edit-page.html',{"head_title":"Pages","page":page})