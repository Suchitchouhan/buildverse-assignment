from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Account(models.Model):
	User_type = (
		(1, 'Student'),
		(2, 'Librarian')
	)
	
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	Account_type= models.IntegerField(choices=User_type, default=1)
	def __str__(self):
		return self.user.username




class Book(models.Model):
	title = models.CharField(default="",max_length=1000)
	publisher = models.CharField(default="",max_length=500)
	When_add = models.DateTimeField(auto_now=True)
	Availablecopies = models.IntegerField(default=0)
	def __str__(self):
		return self.title




class Borrow(models.Model):
	Book = models.ForeignKey(Book,on_delete=models.PROTECT)
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	Issue_date = models.DateTimeField(auto_now=True)
	Is_return = models.BooleanField(default=False)
	renewed = models.IntegerField(default=0)
	Return_date =  models.DateTimeField(null=True)
	def __str__(self):
		return self.user.username+" -- "+self.Book.title

