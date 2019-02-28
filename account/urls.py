from django.urls import path
import account.views as views
urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('regist/',views.regist,name='regist'),
    path('set_password/',views.set_password,name='set_password'),
    path('view_books',views.view_books,name='view_books'),
    path('borrow_record',views.borrow_record,name='borrow_record'),
    path('add_book',views.add_book,name='add_book'),
    path('book_detail',views.book_detail,name='book_detail'),
    path('edit_book',views.edit_book,name='edit_book'),
    path('history_record',views.history_record,name='history_record'),
    path('personal_center',views.personal_center,name='personal_center'),
    path('manage_loan',views.manage_loan,name='manage_loan'),
    path('my_comments',views.my_comments,name='my_comments'),
    path('person',views.person,name='person'),
    path('search',views.search,name='search'),
    path('ranklist',views.ranklist,name='ranklist'),
]