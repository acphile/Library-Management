from django.shortcuts import render
import django 
# Create your views here.
from django.contrib.auth import authenticate
from django.contrib import auth
from django import forms
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import request,response
from django.urls import reverse
from django.http.response import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from account.models import Account,Books,Loan_record,Comments,ComAttitude
import re
import datetime

loan_days=30
extend_days=15
Default_Bnum=20
Default_Cnum=20
Default_Rnum=50

def staff_check(user):
    if user.is_authenticated:return user.is_staff
    else:return False

def super_check(user):
    if user.is_authenticated:return user.is_superuser
    else:return False
    
def check_locked(user):
    borrow_list=Loan_record.objects.filter(borrower=user,returndate__isnull=True)
    for record in borrow_list:
        due=record.loandate+datetime.timedelta(days=loan_days+record.extended*extend_days)
        if due<django.utils.timezone.now():
            return True
    return False

def is_positive_num(num):
    try:
        num=int(num)
        if isinstance(num,int):
            return num>0
        else: return False
    except:
        return False
        
def borrow_limit(user):
    borrow=Loan_record.objects.filter(borrower=user,returndate__isnull=True).count()
    if borrow==4: return True
    else: return False
    
def paginate(page,out_list,num):
    paginator=Paginator(out_list,num)
    try:
        out_list=paginator.page(page)
    except PageNotAnInteger:
        out_list=paginator.page(1)
    except EmptyPage:
        out_list=paginator.page(paginator.num_pages)
    return out_list
    
def index(request):
    if request.user.is_authenticated: user=request.user
    else: user=None
    content={'active_menu':'index','user':user}
    return render(request,'index.html',content)
    
    
def regist(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    state=None
    if request.method=='POST':
        username=request.POST.get('username','')
        password1=request.POST.get('password','')
        password2=request.POST.get('repeat_password','')
        email=request.POST.get('email','')
        sex=request.POST.get('sex','M')
        sex=True if sex=="M" else False
        address=request.POST.get('address','')
        telephone=request.POST.get('tel','')
        if password1!=password2:
            state='repeat_error'
        else:
            username=request.POST.get('username','')
            ck_email=User.objects.filter(email=email).count()
            if User.objects.filter(username=username):
                state='user_exist'
            elif ck_email>0:
                assert(ck_email==1)
                state='email_exist'
            else :
                user=User.objects.create_user(username,email,password1)
                user.save()
                new_account=Account(user=user,telephone=telephone,address=address,sex=sex)
                new_account.save()
                state='success'
                
    content={'active_menu':'index','state':state,'user':None}
    return render(request,'regist.html',content)

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    state=None
    if request.method=='POST':
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            request.session['username']=username
            next_p=request.GET.get('next','/')
            return HttpResponseRedirect(next_p)
        else:
            state='not_exist_or_password_error'
            
    content={'active_menu':'index','state':state,'user':None}
    return render(request,'login.html',content)

@login_required
def set_password(request):
    user=request.user
    state=None
    if request.method=='POST':
        old_password=request.POST.get('old_password','')
        new_password=request.POST.get('new_password','')
        repeat_password=request.POST.get('repeat_password','')
        if user.check_password(old_password):
            if not new_password:
                state='empty'
            elif new_password!=repeat_password:
                state='repeat_error'
            else:
                user.set_password(new_password)
                user.save()
                state='success'
        else:
            state='password_error'
    content={'active_menu':'index','state':state,'user':user}
    return render(request,'set_password.html',content)    
       
def logout(request):
    auth.logout(request)
    ret=request.GET.get('ret',"/")
    #print(ret)
    if ret!="":
        return HttpResponseRedirect(ret)
    else : return HttpResponseRedirect(reverse("index"))

def person(request):
    user=request.user if request.user.is_authenticated else None
    Cnum=Account.objects.get(user=user).CommentNum if user else Default_Cnum
    person_id=request.GET.get('id','')
    if person_id=='':
        return HttpResponseRedirect(reverse('ranklist'))
    try:
        person=User.objects.get(pk=person_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('ranklist'))
    
    if person==user: return HttpResponseRedirect(reverse('personal_center'))
    
    state=None 
    borrownum=Loan_record.objects.filter(borrower=person,returndate__isnull=True).count()
    account=Account.objects.get(user=person)
    
    if user and request.method=="POST":   
        if user.is_superuser or (user.is_staff and not person.is_staff):
            del_id=request.POST.get('del_id',"")
            if del_id!="":
                Comments.objects.get(pk=del_id).delete()
                return HttpResponseRedirect(request.get_full_path())
            
        if user.is_superuser:
            status=request.POST.get("status","")
            if status!="":
                if status=="up":
                    person.is_staff=True
                    person.save()
                elif status=="down":
                    person.is_staff=False
                    person.save()
                return HttpResponseRedirect(request.get_full_path())    
                
        support_id=request.POST.get('support_id',"")
        oppose_id=request.POST.get('oppose_id',"")
        cor_id=""
        if support_id!="": 
            cor_id=support_id
            cor_atti=1
        else :
            cor_atti=-1
            cor_id=oppose_id
            
        if cor_id!="":
            correspond=Comments.objects.get(pk=cor_id)
            sup=ComAttitude.objects.filter(Rcomment=correspond,judger=user)
            if sup.exists():
                what=sup[0]
                if what.attitude == 0: what.attitude=cor_atti
                elif what.attitude == cor_atti: what.attitude=0;
                what.save()
            else :
                new_Atti=ComAttitude(
                    Rcomment=correspond,
                    judger=user,
                    attitude=cor_atti,
                )
                new_Atti.save()            
            state='attitude'
            return HttpResponseRedirect(request.get_full_path()+"#comment"+cor_id)
    
    comments_list=Comments.objects.filter(sender=person).order_by("-senddate")
    comments_num=comments_list.count()
    totalB=Loan_record.objects.filter(borrower=person).count()
    support_num=0
    oppose_num=0
    for comment in comments_list:
        cur=calc_comment(comment,user)
        support_num+=cur[1]
        oppose_num+=cur[2]
        
    comments_list=paginate(request.GET.get('com_pg'),comments_list,Cnum)
    out_list=[] 
    for comment in comments_list:
        out_list.append(calc_comment(comment,user))
        
    content = {
        'user': user,
        'active_menu': 'person',
        'state': state,
        'person':person,
        'account':account,
        'totalB':totalB,
        'borrownum':borrownum,
        'comments_num':comments_num,
        'support_num':support_num,
        'oppose_num':oppose_num,
        'comments_list':comments_list,
        'out_list':out_list,
    }
    return render(request,'person.html', content)
    
@login_required    
def personal_center(request):
    user=request.user
    state=None
    borrow_num=Loan_record.objects.filter(borrower=user,returndate__isnull=True).count()
    history_num=Loan_record.objects.filter(borrower=user,returndate__isnull=False).count()
    
    comments_list=Comments.objects.filter(sender=user)
    comment_num=comments_list.count()
    support_num=0
    oppose_num=0
    for comment in comments_list:
        cur=calc_comment(comment,user)
        support_num+=cur[1]
        oppose_num+=cur[2]
    
    user_state=None
    if check_locked(user):
        user_state="overdue"
    
    account=Account.objects.get(user=user)
    if request.method=="POST":
        sex=request.POST.get('sex','M')
        sex=True if sex=="M" else False
        address=request.POST.get('address','')
        telephone=request.POST.get('tel','')
        BookNum=min(50,int(request.POST.get('Bnum','1')))
        RecordNum=min(100,int(request.POST.get('Rnum','1')))
        CommentNum=min(50,int(request.POST.get('Cnum','1')))
        account.sex=sex
        account.address=address
        account.telephone=telephone
        account.BookNum=BookNum
        account.RecordNum=RecordNum
        account.CommentNum=CommentNum
        account.save()
        return HttpResponseRedirect(reverse('personal_center'))
    
    content = {
        'user':user,
        'active_menu': 'personal_center',
        'account':account,
        'borrow_num': borrow_num,
        'history_num': history_num,
        'comment_num':comment_num,
        'support_num':support_num,
        'user_state':user_state,
        'oppose_num':oppose_num,
    }
    return render(request, 'personal_center.html', content)
    
@login_required
def borrow_record(request):
    user=request.user
    state=None
    if request.method=="POST":
        extend_list=request.POST.getlist("extend",[])
        for id in extend_list:
            record=Loan_record.objects.get(pk=int(id))
            record.extended=True
            record.save()
            state="extend_success"
        
    record_list=Loan_record.objects.filter(borrower=user,returndate__isnull=True).order_by('-loandate')
    record_list=[(record,record.loandate+datetime.timedelta(days=loan_days+record.extended*extend_days)) for record in record_list]
    content = {
        'user':user,
        'active_menu': 'borrow_record',
        'record_list':record_list,
        'state':state,
    }
    return render(request, 'borrow_record.html', content)

@login_required
def history_record(request):
    user=request.user
    Rnum=Account.objects.get(user=user).RecordNum
    history_list=Loan_record.objects.filter(borrower=user,returndate__isnull=False).order_by('-loandate')
    
    history_list=paginate(request.GET.get('page'),history_list,Rnum)
        
    content = {
        'user':user,
        'active_menu': 'history_record',
        'history_list':history_list,
    }
    return render(request, 'history_record.html', content)

@login_required    
def my_comments(request):
    user=request.user
    Cnum=Account.objects.get(user=user).CommentNum
    state=None
    comments_list=Comments.objects.filter(sender=user).order_by("-senddate")        
    comments_list=paginate(request.GET.get('pg'),comments_list,Cnum)
    out_list=[] 
    for comment in comments_list:
        out_list.append(calc_comment(comment,user))
            
    content = {
        'user': user,
        'active_menu': 'my_comments',
        'state': state,
        'comments_list':comments_list,
        'out_list':out_list,
    }
    return render(request,'my_comments.html', content)
    
def book_score(book):
    comments_list=Comments.objects.filter(Rbook=book)
    if comments_list.exists():
        s=0.0
        for comment in comments_list:
            s+=float(comment.score)
        return round(s/comments_list.count(),1)            
    else: return -1
    
def deal_query(kind,cons,key,choice):
    if key=="": return ""
    s="and" if choice!="" else ""
    if key.count("\'")>0:
        key=key.replace("\'","\'\'")
        
    if cons=='contain':
        key=key.replace("/", "//");  
        key=key.replace("[", "/[");  
        key=key.replace("]", "/]");  
        key=key.replace("%", "/%");  
        key=key.replace("&","/&");  
        key=key.replace("_", "/_");  
        key=key.replace("(", "/(");  
        key=key.replace(")", "/)");  
            
    if cons=="exact": 
        if choice=="and" or choice=="": s+=" {0}='{1}' ".format(kind,key)
        else : s+=" {0}!='{1}' ".format(kind,key)
    elif cons=="contain": 
        if choice=="and" or choice=="": s+=" {0} LIKE '%{1}%' ".format(kind,key)
        else : s+=" {0} NOT LIKE '%{1}%' ".format(kind,key)
        
    return s
    
def search(request):
    user=request.user if request.user.is_authenticated else None   
    state=None
    result=None
    out_list=[]
    what=['bookname','category','author','publisher']
    constrain=['exact','exact','exact','exact']
    keyword=['','','','']
    choose=['and','and','and']
    from_date=""
    end_date=""
    remain="no"
    if request.method == "POST":
        what=request.POST.getlist('what',[])
        constrain=request.POST.getlist('constrain',[])
        keyword=request.POST.getlist('keyword',[])
        choose=request.POST.getlist('choose',[])
        query="SELECT * FROM books where"
        query+=deal_query(what[0],constrain[0],keyword[0],"")
        for kind,con,key,how in zip(what[1:],constrain[1:],keyword[1:],choose):    
            query+=deal_query(kind,con,key,how)
                
        from_date=request.POST.get('from_date','')
        end_date=request.POST.get('end_date','')
        if from_date!="": query+="and date>='{0}'".format(from_date)
        if end_date!="": query+="and date<='{0}'".format(end_date)
        remain=request.POST.get('remain','no')
        print(query)
        result=Books.objects.raw(query)
        out_list=[]
        for book in result:
            lendnum=Loan_record.objects.filter(Lbook=book,returndate__isnull=True).count()
            if remain=="no" or lendnum<book.totnum:
                out_list.append((book,lendnum))
        state="success"        
    content = {
        'user':user,
        'active_menu': 'search',
        'state':state,
        'out_list':out_list,
        'what':what,
        'constrain':constrain,
        'keyword':keyword,
        'choose':choose,
        'from_date':from_date,
        'end_date':end_date,
        'remain':remain,
    }
    return render(request, 'search.html', content)
    
def url_search_books(category,what,key):
    s='/view_books?category={0}'.format(category)
    if key!='':
        s+='&kind={0}&key={1}'.format(what,key)
    return s
    
def view_books(request):
    user=request.user if request.user.is_authenticated else None
    Bnum=Account.objects.get(user=user).BookNum if user else Default_Bnum
    
    category_list=Books.objects.values_list('category',flat=True).order_by('category').distinct()
    state=None
    
    query_category=request.GET.get('category', 'all')
    if not query_category or query_category=='all':
        query_category='all'
        book_list=Books.objects.all()
    else: book_list=Books.objects.filter(category=query_category)
    keyword=request.GET.get('key','')
    what=request.GET.get('kind','name')
    
    if request.method=='POST':
        which=0
        if user:
            if user.is_superuser:
                del_id=request.POST.get('delete',"")
                if del_id!="":
                    which=1
                    Books.objects.filter(pk=del_id).delete()
                    return HttpResponseRedirect(reverse('view_books'))         
            else :
                borrow_id=request.POST.get('borrow',"")
                if borrow_id!="":
                    which=2
                    book=Books.objects.get(pk=borrow_id)
                    state=borrow(user,book)
                    
        if which==0:        
            keyword=request.POST.get('keyword', '')
            what=request.POST.get('what','name')
            return HttpResponseRedirect(url_search_books(query_category,what,keyword))
        
    if what=='name': book_list=book_list.filter(bookname__contains=keyword)
    else: book_list=book_list.filter(isbn__contains=keyword)
                
    book_list=paginate(request.GET.get('page'),book_list,Bnum)    
    out_list=[(book,Loan_record.objects.filter(Lbook=book,returndate__isnull=True).count(),book_score(book)) for book in book_list]
    content = {
        'user':user,
        'active_menu': 'view_books',
        'state':state,
        'category_list':category_list,
        'query_category':query_category,
        'keyword':keyword,
        'whatkind': what,
        'book_list':book_list,
        'out_list':out_list,
    }
    return render(request, 'view_books.html', content)
    
@user_passes_test(super_check)
def add_book(request):
    user=request.user
    state=None
    if request.method == 'POST':
        isbn=request.POST.get('isbn', '')
        bookname=request.POST.get('name', '')
        author=request.POST.get('author', '')
        category=request.POST.get('category', '')
        publisher=request.POST.get('publisher','')
        date=request.POST.get('pubdate', '')
        totnum=request.POST.get('num',1)
        pict=request.FILES.get('img','image/index.jpg')
        description=request.POST.get('describe','')
        if Books.objects.filter(isbn=isbn):
            state='existed'
        elif is_positive_num(totnum)==False:
            state='wrong number'
        else :
            new_book=Books(
                isbn=isbn,
                bookname=bookname,
                author=author,
                category=category,
                publisher=publisher,
                date=date,
                pict=pict,
                totnum=int(totnum),
                description=description
            )
            new_book.save()
            state='success'
        
    content = {
        'user': user,
        'active_menu': 'add_book',
        'state': state,
    }
    return render(request, 'add_book.html', content)    
    
def borrow(user,book):
    if check_locked(user): return 'user_locked'
    if borrow_limit(user): return 'limited'
    
    lendnum=Loan_record.objects.filter(Lbook=book,returndate__isnull=True).count()
    if lendnum==book.totnum: return 'none'
    
    have=Loan_record.objects.filter(Lbook=book,borrower=user,returndate__isnull=True).count()
    if have>0:
        assert(have==1)
        return 'borrowed'
    
    new_record=Loan_record(
        Lbook=book,
        borrower=user,
        extended=False,
    )
    new_record.save()
    return 'borrow-success'  
    
def calc_comment(comment,user):
    atti=ComAttitude.objects.filter(Rcomment=comment)
    if atti.count()==0:
        if user: return (comment,0,0,0)
        else: return (comment,0,0,-2)
    else :
        if user:
            try:
                tmp=atti.filter(judger=user)[0]
                user_atti=tmp.attitude
            except:
                user_atti=0                
        else: user_atti=-2
        return (comment,atti.filter(attitude=1).count(),atti.filter(attitude=-1).count(),user_atti)

def edit_comment(user_mark,book,user,content,score):
    if user_mark:
        user_mark.content=content
        user_mark.senddate=django.utils.timezone.now()
        user_mark.score=score
        user_mark.save()
        return user_mark
    else:
        new_comment=Comments(
            Rbook=book,
            sender=user,
            content=content,
            score=score,
        )
        new_comment.save()
        return new_comment
    
def book_detail(request):
    user=request.user if request.user.is_authenticated else None
    Cnum=Account.objects.get(user=user).CommentNum if user else Default_Cnum
    book_id=request.GET.get('id', '')
    if book_id=='':
        return HttpResponseRedirect(reverse('view_books'))
    try:
        book=Books.objects.get(pk=book_id)
    except Books.DoesNotExist:
        return HttpResponseRedirect(reverse('view_books'))
    
    state=None 
    user_mark=None    
    if user:
        user_list=Comments.objects.filter(Rbook=book,sender=user)
        if user_list.exists():
            user_mark=user_list[0]
            
        if user.is_superuser:
            choice=request.POST.get('delete',"")
            if choice == "删除该书":
                Books.objects.filter(pk=book_id).delete()
                return HttpResponseRedirect(reverse('view_books'))
                
        else :
            choice=request.POST.get('borrow',"")
            if choice == "借阅此书":
                state=borrow(user,book)
                #print(state)
           
    if user and request.method=="POST":
        score=request.POST.get('score',"")
        content=request.POST.get('content',"")
        if content!="" and score!="":
            user_mark=edit_comment(user_mark,book,user,content,float(score))
            state="comment_success"
        
        del_id=request.POST.get('del_id',"")
        if del_id!="":
            del_comment=Comments.objects.get(pk=del_id)
            person=del_comment.sender
            if user.is_superuser or (user.is_staff and not person.is_staff):
                del_comment.delete()
                user_list=Comments.objects.filter(Rbook=book,sender=user)
                if user_list.exists(): user_mark=user_list[0]
                else: user_mark=None
                return HttpResponseRedirect(request.get_full_path())
        
        drop=request.POST.get('drop',"")
        if drop!="":
            user_mark.delete()
            user_mark=None
            return HttpResponseRedirect(request.get_full_path())
            
        support_id=request.POST.get('support_id',"")
        oppose_id=request.POST.get('oppose_id',"")
        cor_id=""
        if support_id!="": 
            cor_id=support_id
            cor_atti=1
        else :
            cor_atti=-1
            cor_id=oppose_id
            
        if cor_id!="":
            correspond=Comments.objects.get(pk=cor_id)
            sup=ComAttitude.objects.filter(Rcomment=correspond,judger=user)
            if sup.exists():
                what=sup[0]
                if what.attitude == 0: what.attitude=cor_atti
                elif what.attitude == cor_atti: what.attitude=0;
                what.save()
            else :
                new_Atti=ComAttitude(
                    Rcomment=correspond,
                    judger=user,
                    attitude=cor_atti,
                )
                new_Atti.save()            
            state='attitude'
            return HttpResponseRedirect(request.get_full_path()+"#comment"+cor_id)
            
    comments_list=Comments.objects.filter(Rbook=book).order_by("-senddate")        
    
    comments_list=paginate(request.GET.get('com_pg'),comments_list,Cnum)
    out_list=[] 
    for comment in comments_list:
        out_list.append(calc_comment(comment,user))
    score=book_score(book)      
    lendnum=Loan_record.objects.filter(Lbook=book,returndate__isnull=True).count()
    
    content = {
        'user': user,
        'active_menu': 'book_detail',
        'state': state,
        'book': book,
        'lendnum':lendnum,
        'score':score,
        'comments_list':comments_list,
        'out_list':out_list,
        'user_mark':user_mark,
    }
    return render(request,'book_detail.html', content)
    
@user_passes_test(super_check)
def edit_book(request):
    user=request.user
    book_id=request.GET.get('id', '')
    if book_id=='':
        return HttpResponseRedirect(reverse('view_books'))
    try:
        book=Books.objects.get(pk=book_id)
    except Books.DoesNotExist:
        return HttpResponseRedirect(reverse('view_books'))
    state=None
    
    if request.method == 'POST':
        #print(request.POST.items(),type(request.POST))
        isbn=request.POST.get('isbn','')
        bookname=request.POST.get('name', '')
        author=request.POST.get('author', '')
        category=request.POST.get('category', '')
        publisher=request.POST.get('publisher','')
        date=request.POST.get('pubdate', '')
        totnum=request.POST.get('num',1)
        description=request.POST.get('describe','')
        pict=request.FILES.get('img','')
        cBook=Books.objects.filter(isbn=isbn)
        checkbook=cBook[0] if cBook.exists() else book
        if checkbook!=book:
            state='existed'
        elif is_positive_num(totnum)==False:
            state='wrong number'
        else :
            if pict!='':
                book.pict=pict
                book.save()
                
            Books.objects.filter(pk=book_id).update(
                isbn=isbn,
                bookname=bookname,
                author=author,
                category=category,
                publisher=publisher,
                date=date,
                totnum=int(totnum),
                description=description
            )
            state='success'
            
        book=Books.objects.get(pk=book_id)      
                
    content = {
        'user': user,
        'active_menu': 'edit_book',
        'state': state,
        'book': book,
    }
    return render(request,'edit_book.html', content)

def url_search_loans(borrower,isbn):
    s='/manage_loan'
    ff=0
    if borrower!='':
        s+='?borrower={0}'.format(borrower)
        ff=1
    if isbn!='':
        s+='?' if ff==0 else '&'
        s+='isbn={0}'.format(isbn)
        ff=1
        
    return s
    
@user_passes_test(staff_check)
def manage_loan(request):
    user=request.user   
    Rnum=Account.objects.get(user=user).RecordNum    
    state=None
    loan_list=Loan_record.objects.filter(returndate__isnull=True).order_by("loandate")

    borrower=request.GET.get('borrower',"")
    isbn=request.GET.get('isbn',"")
    
    if request.method=="POST":
        #print(request.POST)
        if request.POST.get('return',False)=='确认还书':
            return_list=request.POST.getlist("record",[])
            for id in return_list:
                loan=Loan_record.objects.get(pk=int(id))
                loan.returndate=django.utils.timezone.now()
                loan.save()
                state='return_success'
            loan_list=Loan_record.objects.filter(returndate__isnull=True).order_by("loandate")
            return HttpResponseRedirect(request.get_full_path())
            
        if request.POST.get('filter_loan',False)=='搜索':
            borrower=request.POST.get('borrower',"")
            isbn=request.POST.get('isbn',"")
            return HttpResponseRedirect(url_search_loans(borrower,isbn))
            
    if borrower!="": loan_list=loan_list.filter(borrower__username=borrower)
    if isbn!="": loan_list=loan_list.filter(Lbook__isbn=isbn)
    loan_list=paginate(request.GET.get('page'),loan_list,Rnum)
    
    out_list=[(record,record.loandate+datetime.timedelta(days=loan_days+record.extended*extend_days)) for record in loan_list]    
    content = {
        'user':user,
        'active_menu': 'manage_loan',
        'loan_list':loan_list,
        'out_list':out_list,
        'borrower':borrower,
        'isbn':isbn,
        'state':state,
    }
    return render(request, 'manage_loan.html', content)
    
def url_search_user(who,key):
    s='/ranklist'
    ff=0
    if who!='':
        s+='?who={0}'.format(who)
        ff=1
    s+="&" if ff==1 else "?"
    s+="?key={0}".format(key)
    return s
    
def ranklist(request):
    user=request.user if request.user.is_authenticated else None 
    Rnum=Account.objects.get(user=user).RecordNum if user else Default_Rnum    
    state=None
    who=request.GET.get('who',"")
    key=request.GET.get('key',"0")
    if key not in ["0","1","2"]: key="0"
    
    if request.method=="POST":
        who=request.POST.get('who',"")
        return HttpResponseRedirect(url_search_user(who,key))
        
    user_list=User.objects.filter(username__contains=who)        
    #user_list=paginate(request.GET.get("page","1"),user_list,2)
    
    out_list=[]
    for person in user_list:
        numB=Loan_record.objects.filter(borrower=person).count()
        comments_list=Comments.objects.filter(sender=person)
        numC=comments_list.count()
        numS=0
        for comment in comments_list:
            numS+=ComAttitude.objects.filter(Rcomment=comment,attitude=1).count()
        out_list.append((person,numB,numC,numS))
    out_list=sorted(out_list,key=lambda x:x[int(key)+1],reverse=True)
    out_list=paginate(request.GET.get("page","1"),out_list,Rnum)    
    content = {
        'user':user,
        'active_menu': 'ranklist',
        'user_list':user_list,
        'out_list':out_list,
        'key':key,
        'who':who,
        'state':state,
    }
    return render(request, 'ranklist.html', content)