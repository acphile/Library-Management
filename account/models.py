from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
# Create your models here.

class Account(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    sex=models.BooleanField(default=True)
    telephone=models.CharField(max_length=18,blank=True,default="")
    address=models.CharField(max_length=50,blank=True,default="")
    CommentNum=models.PositiveIntegerField(default=1)
    RecordNum=models.PositiveIntegerField(default=1)
    BookNum=models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.user.username

    class Meta:
        db_table='account'
        verbose_name='用户信息'
        verbose_name_plural='用户信息'
        ordering=['user__username']
        
class AccountAdmin(admin.ModelAdmin):
    list_display =('user',)

class Books(models.Model):
    isbn=models.CharField(max_length=13)
    bookname=models.CharField(max_length=40)
    date=models.DateField() 
    category=models.CharField(max_length=7,default="")
    publisher=models.CharField(max_length=20)
    author=models.CharField(max_length=20)
    description=models.TextField(max_length=300,blank=True,default="")
    totnum=models.PositiveIntegerField(default=1)
    pict=models.ImageField(upload_to='image/%Y/%m/%d/',default="image/index.jpg")
    
    def __str__(self):
        return self.isbn

    class Meta:
        db_table='books'
        verbose_name='书籍信息'
        verbose_name_plural='书籍信息'
        ordering=['isbn']
        
class BooksAdmin(admin.ModelAdmin):
    list_display=('isbn','bookname','category','date')

class Loan_record(models.Model):
    Lbook=models.ForeignKey(Books,on_delete=models.CASCADE)
    borrower=models.ForeignKey(User,on_delete=models.CASCADE)
    loandate=models.DateTimeField(auto_now_add=True)
    returndate=models.DateTimeField(null=True,blank=True)
    extended=models.BooleanField(default=False)
    
    def __str__(self):
        return u'%s %s'%(self.Lbook.isbn,self.borrower.username)

    class Meta:
        db_table='loan_record'
        verbose_name='借阅记录'
        verbose_name_plural='借阅记录'
        ordering=['loandate']
        
class LRecordAdmin(admin.ModelAdmin):
    list_display=('Lbook','borrower','loandate','extended','returndate')    

class Comments(models.Model):
    Rbook=models.ForeignKey(Books,on_delete=models.CASCADE)
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    senddate=models.DateTimeField(auto_now_add=True)
    content=models.TextField(max_length=300,default="")    
    score=models.DecimalField(max_digits=2,decimal_places=1,default=3.0)
    
    def __str__(self):
        return '%d %s %s'%(self.id,self.Rbook.isbn,self.sender.username)

    class Meta:
        db_table='Comments'
        verbose_name='评论记录'
        verbose_name_plural='评论记录'
        ordering=['senddate']

class CommentsAdmin(admin.ModelAdmin):
    list_display=('Rbook','sender','senddate')
    
class ComAttitude(models.Model):
    Rcomment=models.ForeignKey(Comments,on_delete=models.CASCADE)
    judger=models.ForeignKey(User,on_delete=models.CASCADE)
    attitude=models.IntegerField(default=0)    
    
    def __str__(self):
        return '%s %s'%(self.Rcomment,self.judger)

    class Meta:
        db_table='ComAttitude'
        verbose_name='评论态度'
        verbose_name_plural='评论态度'

class ComAttitudeAdmin(admin.ModelAdmin):
    list_display=('Rcomment','judger','attitude')
    
admin.site.register(Books,BooksAdmin)
admin.site.register(Account,AccountAdmin)
admin.site.register(Loan_record,LRecordAdmin)
admin.site.register(Comments,CommentsAdmin)
admin.site.register(ComAttitude,ComAttitudeAdmin)