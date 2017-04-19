from django.conf.urls import url

from . import views

app_name = 'iva'
urlpatterns = [url(r'^index.html*', views.index, name='index'),
               url(r'^assign_cpe.html*', views.assign_cpe, name='assign_cpe'),
               url(r'^search_cves.html*', views.search_cves, name='search_cves'),
               url(r'^cve_matches.html*', views.cve_matches, name='cve_matches'),
               url(r'^new_software', views.new_software, name='new_software'),
               url(r'^sw_products_with_cpe', views.sw_products_with_cpe, name='sw_products_with_cpe'),
               url(r'^alerts', views.alerts, name='alerts'),
               url(r'^cpe_wfn.html*', views.cpe_wfn, name='cpe_wfn'),
               url(r'^alert_log.html*', views.alert_log, name='log'),
               url(r'^alert_notes.html*', views.alert_notes, name='alert_notes'),
               url(r'^alert_status.html*', views.alert_status, name='alert_status'),
               url(r'^compare_cpe.html*', views.compare_cpe, name='compare_cpe'),
               url(r'^modify_cpe.html*', views.modify_cpe, name='modify_cpe'),
               url(r'^sign_in.html*', views.sign_in, name='sign_in'),
               url(r'^users.html*', views.users, name='users'),
               url(r'^add_user.html*', views.add_user, name='add_user'),
               url(r'^change_user_pwd.html*', views.change_user_pwd, name='change_user_pwd'),
               url(r'^modify_user.html*', views.modify_user, name='modify_user'),
               url(r'^local_repositories.html*', views.local_repositories, name='local_repositories'),
               url(r'^change_daily_db_update_time.html*', views.change_daily_db_update_time, name='change_daily_db_update_time'),
               url(r'^grouped_cve_matches.html*', views.grouped_cve_matches, name='grouped_cve_matches')]
