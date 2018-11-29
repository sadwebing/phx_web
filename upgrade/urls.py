from django.conf.urls import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url('^operate$', views.Operate, name='Operate'),
    url('^get_svn_customer$', views.GetSvnCustomer, name='GetSvnCustomer'),
    url('^get_svn_records$', views.GetSvnRecords, name='GetSvnRecords'),
    url('^get_svn_lock_records$', views.GetSvnLockRecords, name='GetSvnLockRecords'),
    url('^get_svn_master$', views.GetSvnMaster, name='GetSvnMaster'),
]