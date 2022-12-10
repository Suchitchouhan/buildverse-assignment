from rest_framework.serializers import *
from django.contrib.auth.models import User
from .models import Account,Book, Borrow
from datetime import datetime
from datetime import timedelta


class UserCreateSerializer(Serializer):
    username = CharField(error_messages={"required":"username key is required","blank":"username is required"})
    first_name = CharField(error_messages={"required":"first_name key is required","blank":"first_name is required"})
    last_name = CharField(error_messages={"required":"last_name key is required","blank":"last_name is required"})
    email = CharField(error_messages={"required":"email key is required","blank":"email is required"})
    password = CharField(error_messages={"required":"password key is required","blank":"password is required"})
    def validate(self,attr):
        username=attr['username']
        email=attr['email']
        if User.objects.filter(email=email).exists():
            raise  ValidationError("Email is already exists")
        if User.objects.filter(username=username).exists(): 
            raise ValidationError("Username is already exists")
        return attr
        
    def create(self,validate_data):
        username = self.validate_data['username']
        first_name = self.validate_data['first_name']          
        last_name = self.validate_data['last_name']          
        email = self.validate_data['email']          
        password = self.validate_data['password']
        user = User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password)
        user.save()
        account = Account.objects.create(user=user)
        account.Account_type=1
        account.save()
        return validate_data


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'



class BorrowSerializer(Serializer):
    book_id = IntegerField(error_messages={"required":"book_id key is required","blank":"book_id is required"})
    def validate(self, attrs):
        book_id = attrs['book_id']
        request = self.context['request']
        try:
            b=Book.objects.get(pk=book_id)
            if b.Availablecopies == 0:
                brow = Borrow.objects.filter(Book=b,Is_return=False).order_by("-Return_date").last()
                raise ValidationError(f"Zero Copy is available. It will return by {str(brow.Return_date)}")
        except Exception as e:
            raise ValidationError(str(e))   
        try:
            Account.objects.get(user=request.user,Account_type=1)
        except Exception as e:
            raise ValidationError(str(e))
        b = Book.objects.get(pk=book_id)
        if Borrow.objects.filter(Book=b,user=request.user,Is_return=False).exists():
            raise ValidationError("You already Issued the book .Please return according to time")
        return super().validate(attrs)
    def create(self,validate_data):
        book_id = self.validated_data['book_id']
        request = self.context['request']
        b = Book.objects.get(pk=book_id)
        brow = Borrow.objects.create(Book=b,user=request.user)
        brow.Return_date=datetime.now()+timedelta(days=30)
        brow.save()
        b.Availablecopies-=1
        b.save()
        return validate_data


class ListBorrowBookSerializer(ModelSerializer):
    class Meta:
        model = Borrow
        fields = '__all__'




class AddBorrowBookSerializer(Serializer):
    book_id = IntegerField(error_messages={"required":"book_id key is required","blank":"book_id is required"})
    user_id = IntegerField(error_messages={"required":"user_id key is required","blank":"user_id is required"})
    def validate(self, attrs):
        book_id = attrs['book_id']
        user_id = attrs['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            raise ValidationError(str(e))    
        try:
            b=Book.objects.get(pk=book_id)
            if b.Availablecopies == 0:
                brow = Borrow.objects.filter(Book=b,Is_return=False).order_by("-Return_date").last()
                raise ValidationError(f"Zero Copy is available. It will return by {str(brow.Return_date)}")
        except Exception as e:
            raise ValidationError(str(e))   
        try:
            Account.objects.get(user=user,Account_type=1)
        except Exception as e:
            raise ValidationError(str(e))
        b = Book.objects.get(pk=book_id)
        if Borrow.objects.filter(Book=b,user=user,Is_return=False).exists():
            raise ValidationError("You already Issued the book .")
        return super().validate(attrs)
    def create(self,validate_data):
        book_id = self.validated_data['book_id']
        user_id = self.validated_data['user_id']
        user = User.objects.get(pk=user_id)
        b = Book.objects.get(pk=book_id)
        brow = Borrow.objects.create(Book=b,user=user)
        brow.Return_date=datetime.now()+timedelta(days=30)
        brow.save()
        b.Availablecopies-=1
        b.save()
        return validate_data


# class RenewBookSerializer(Serializer):
#     book_id = IntegerField(error_messages={"required":"book_id key is required","blank":"book_id is required"})
#     def validate(self, attrs):
#         book_id = attrs['book_id']
#         request = self.context['request']
#         try:
#             Account.objects.get(user=request.user,Account_type=1)
#         except Exception as e:
#             raise ValidationError(str(e))
#         b = Book.objects.get(pk=book_id)
#         if Borrow.objects.filter(Book=b,user=request.user,Is_return=False,renewed=1).exists():            
#             raise ValidationError("You already Issued the book .Please return according to time")
#         return super().validate(attrs)


#     def update(self,instance,validate_data):
#         book_id = self.validated_data['book_id']
#         request = self.context['request']
#         b = Book.objects.get(pk=book_id)
#         brow = Borrow.objects.get(Book=b,user=request.user,Is_return=False)
#         brow.Return_date=brow.Return_date+timedelta(days=30)
#         brow.renewed+=1
#         brow.save()
#         return validate_data        




# class ReturnBookSerializer(Serializer):
#     book_id = IntegerField(error_messages={"required":"book_id key is required","blank":"book_id is required"})
#     def validate(self, attrs):
#         book_id = attrs['book_id']
#         request = self.context['request']
#         try:
#             Account.objects.get(user=request.user,Account_type=1)
#         except Exception as e:
#             raise ValidationError(str(e))
#         b = Book.objects.get(pk=book_id)
#         if Borrow.objects.filter(Book=b,user=request.user,Is_return=False).exists() == False:            
#             raise ValidationError("Please Issue the book")
#         return super().validate(attrs)

#     def create(self,validate_data):
#         book_id = self.validated_data['book_id']
#         request = self.context['request']
#         b = Book.objects.get(pk=book_id)
#         brow = Borrow.objects.get(Book=b,user=request.user,Is_return=False)
#         brow.Return_date=brow.Return_date+timedelta(days=30)
#         brow.renewed+=1
#         brow.save()
#         return validate_data     



