from django.shortcuts import render
from rest_framework.views import APIView

from management.serializers import AddBorrowBookSerializer, BookSerializer, BorrowSerializer, ListBorrowBookSerializer, UserCreateSerializer
from .models import *
import json
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.http import HttpResponse
from rest_framework.response import Response
from django.contrib.auth.models import User
import math, random
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView
from datetime import datetime
from datetime import timedelta



class Login(APIView):
	permission_classes = (AllowAny, )
	def post(self, request):
		password = request.data.get("password")
		username= request.data.get("username")
		if username is None or password is None:
			return Response({'error': 'Please provide both username and password'},
							status=HTTP_400_BAD_REQUEST)
		user = authenticate(username=username, password=password)
		if not user:
			returnMessage = {'error': 'Invalid Credentials'}
			return HttpResponse(
			json.dumps(returnMessage),
			content_type = 'application/javascript; charset=utf8'
		)

		#this method create token or if exists in model it get token
		token, _ = Token.objects.get_or_create(user=user)
		returnToken = {'token':token.key}
		return HttpResponse(
			json.dumps(returnToken),
			content_type = 'application/javascript; charset=utf8'
		)



class SignUp(APIView):
	permission_classes = (AllowAny, )
	def post(self, request):
		serializer = UserCreateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message':'account has been successfully Created'},status=HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)




class BookList(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookSerializer
    def get_queryset(self):
        return Book.objects.all()


class BorrowBook(APIView):
	permission_classes = [IsAuthenticated]

	#This method is Borrowing Book for Student
	def post(self, request):
		serializer = BorrowSerializer(data=request.data,context={"request":request})
		if serializer.is_valid():
			serializer.save()
			return Response({'message':'You have Borrow the book successfully'},status=HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


	#This is for viewing Borrowed book
	def get(self, request):
		is_return = request.GET.get("is_return",None)
		if is_return == True:
			bro = Borrow.objects.filter(user=request.user,Is_return=True).order_by("-Issue_date")
		elif is_return == False:
			bro = Borrow.objects.filter(user=request.user,Is_return=False).order_by("-Issue_date")
		else:
			bro = Borrow.objects.filter(user=request.user).order_by("-Issue_date")
		serializer = ListBorrowBookSerializer(bro,many=True)
		return Response(serializer.data, status=HTTP_200_OK)


	#This is for renewing the book for 30 days
	def put(self, request):
		context={}
		borrow_id = request.data.get("borrow_id")
		if Borrow.objects.filter(pk=borrow_id).exists():
			b = Borrow.objects.get(pk=borrow_id)
			if b.Is_return == False and b.renewed == 0:
				b.renewed+=1
				b.Return_date = b.Return_date+timedelta(days=30)
				b.save()
				context['message']="Book has been Renewed"
				return Response(context, status=HTTP_200_OK)
			else:
				context['message']="Book connot be renewed"
				return Response(context,status=HTTP_400_BAD_REQUEST)
		else:
			context['message']="Borrow id is not exists"		
			return Response(context,status=HTTP_400_BAD_REQUEST)


	#This method is returning for book
	def patch(self, request):
		context={}
		borrow_id = request.data.get("borrow_id")
		if Borrow.objects.filter(pk=borrow_id).exists():
			b = Borrow.objects.get(pk=borrow_id)
			if b.Is_return == False :
				b.Is_return=True
				b.save()
				context['message']="Book has been Return"
				return Response(context, status=HTTP_200_OK)
			else:
				context['message']="Book connot be renewed"
				return Response(context,status=HTTP_400_BAD_REQUEST)
		else:
			context['message']="Borrow id is not exists"		
			return Response(context,status=HTTP_400_BAD_REQUEST)

					
					

class BorrowHistory(APIView):
	serializer_class = ListBorrowBookSerializer
	permission_classes = [IsAuthenticated]

	# In this method Librarian can see the history of borrow book

	def get(self,request):
		user_id=request.GET.get("user_id",None)
		if Account.objects.get(user=request.user).Account_type == 2:
			try:
				if user_id:
					user = User.objects.get(pk=user_id)
					serializer = ListBorrowBookSerializer(Borrow.objects.filter(user=user),many=True)
				else:
					serializer = ListBorrowBookSerializer(Borrow.objects.all(),many=True)
				return Response(serializer.data, status=HTTP_200_OK)
			except Exception as e:
				return Response({"message":str(e)},status=HTTP_400_BAD_REQUEST)			
		else:
			return Response({"message":"You do not have permission to view history."},status=HTTP_400_BAD_REQUEST)	

	#This will Book to Student
	def post(self, request):
		if Account.objects.get(user=request.user).Account_type == 2:
			serializer = AddBorrowBookSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({'message':'book has been borrow successfully'},status=HTTP_200_OK)
			return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

		else:
			return Response({"message":"You do not have permission to view history."},status=HTTP_400_BAD_REQUEST)	

		
	def put(self, request):
		context={}
		borrow_id = request.data.get("borrow_id")
		if Borrow.objects.filter(pk=borrow_id).exists():
			b = Borrow.objects.get(pk=borrow_id)
			if b.Is_return == False and b.renewed == 0:
				b.renewed+=1
				b.Return_date = b.Return_date+timedelta(days=30)
				b.save()
				context['message']="Book has been Renewed"
				return Response(context, status=HTTP_200_OK)
			else:
				context['message']="Book connot be renewed"
				return Response(context,status=HTTP_400_BAD_REQUEST)
		else:
			context['message']="Borrow id is not exists"		
			return Response(context,status=HTTP_400_BAD_REQUEST)


	#This method is returning for book
	def patch(self, request):
		context={}
		borrow_id = request.data.get("borrow_id")
		if Borrow.objects.filter(pk=borrow_id).exists():
			b = Borrow.objects.get(pk=borrow_id)
			if b.Is_return == False :
				b.Is_return=True
				b.save()
				context['message']="Book has been Return"
				return Response(context, status=HTTP_200_OK)
			else:
				context['message']="Book connot be renewed"
				return Response(context,status=HTTP_400_BAD_REQUEST)
		else:
			context['message']="Borrow id is not exists"		
			return Response(context,status=HTTP_400_BAD_REQUEST)

					

