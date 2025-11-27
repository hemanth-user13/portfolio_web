import random
import string
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .models import *
from rest_framework import status
from .serialzers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from oauth2_provider.models import Application
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta
from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
from rest_framework.parsers import MultiPartParser, FormParser
## basic way of creating an api
# class UserDetailsView(viewsets.ModelViewSet):
#     queryset=UserDetails.objects.all()
#     serializer_class=UserDetailsSerialzers


class UserDetailsView(APIView):
    def get(self, request):
        users = UserDetails.objects.all()
        serializer = UserDetailsSerialzers(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserDetailsSerialzers(data=request.data, context={"action": "create"})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterUserApi(APIView):
    serializer_class = UserDetailsSerialzers
    def post(self, request):
        try:
            serializer = UserDetailsSerialzers(data=request.data)
            serializer.is_valid(raise_exception=True)
            print("serilaizer data is",serializer)
            serializer.save()
            return Response({
            "message": "User registered successfully",
            "data": serializer.data
            },status=201)
        except ValidationError as ve:
            return Response({
                "message":"validation error",
                "error":ve.detail
            },status=400)
        except Exception as e:
            return Response({
                "message":"An Exception has been ouccured",
                "error":str(e)
            },status=500)

    
# class GetUserApiView(APIView):
#     def get(self,request,id):
#         try:
#             user=get_object_or_404(UserDetails,id=id)
#         except UserDetails.DoesNotExist:
#             return Response({
#                 "status":"error",
#                 "message":"No user found with the given id"
#             },status=status.HTTP_404_NOT_FOUND)
#         serialzer=UserDetailsSerialzers(user)
#         return Response({"data":serialzer.data},status=status.HTTP_200_OK)
class GetUserApiView(APIView):
    authentication_classes=[]
    permission_classes=[]
    def get(self, request, id):
        try:
           
            user = UserDetails.objects.get(id=id)
        except UserDetails.DoesNotExist:
            return Response({
                "status": "error",
                "message": "No user found with the given id"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserDetailsSerialzers(user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({
            "status":"error",
            "error":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

    
class GetentireUserList(APIView):
    def get(self,request):
        users = UserDetails.objects.all()
        serializer = UserDetailsSerialzers(users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


### email via query_params sending the email through link
class GetUserdatabyEmail(APIView):
    def get(self,request):
        print("request",request)
        email = request.query_params.get('email')
        print("email is",email)
        if not email:
            return Response({"error":"Email is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            user=UserDetails.objects.get(email=email)
            serializer=UserDetailsSerialzers(user)
            return Response(serializer.data)
        except UserDetails.DoesNotExist:
            return Response({"error":"User not found"},status=status.HTTP_404_NOT_FOUND)
        

class GetUseremaildata(APIView):
    def post(self,request):
        email=request.data.get('email')
        print("email",request.data)
        if not email:
            return Response({"error":"Email is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            user=UserDetails.objects.get(email=email)
            print("user",user)
            serilizer=UserDetailsSerialzers(user)
            return Response(serilizer.data,status=status.HTTP_200_OK)
        except UserDetails.DoesNotExist:
            return Response({"error":"User not found"},status=status.HTTP_404_NOT_FOUND)
   
#### getting the client id and sceret 
class GetClientDetails(APIView):
    def get(self, request, *args, **kwargs):
        try:
            result_str = "".join(random.choice(string.ascii_lowercase) for i in range(64))
            if Application.objects.filter(name = "projectk").exists():
                token_object = Application.objects.get(name = "projectk")
                
 
            else:
                Application.objects.create(
                    name = "projectk",
                    client_type = "confidential",
                    authorization_grant_type = "password",
                    client_secret = result_str,
                    hash_client_secret = False
                )
               
                token_object = Application.objects.get(name = "projectk")
 
 
            response_data = {
                "client_id":token_object.client_id,
                "client_secret":token_object.client_secret,
            }
            return Response({"clientDetails": response_data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserLoginApi(APIView):
    def post(self,request):
        # print(request.data)
        email=request.data.get('email')
        password=request.data.get('password')
        client_id=request.data.get('client_id')
        client_secret=request.data.get('client_secret')
        print('data is',client_id,client_secret,email,password)
        print("UserDetails",UserDetails)
        if not all([email,password,client_id,client_secret]):
            return Response({"error":"all feilds are required"},status=400)
        try:
            user=UserDetails.objects.get(email=email)
        except UserDetails.DoesNotExist:
            return Response({'error':"invaild credentials"},status=400)
        
        if not check_password(password,user.password):
            return Response({'error':'invalid credentials'},status=400)
        
        try:
            app=Application.objects.get(client_id=client_id,client_secret=client_secret)
        except Application.DoesNotExist:
            return Response({
                "error":"Invaild Credentials"
            },status=400)
        expires=timezone.now()+timedelta(minutes=15)
        access_token=AccessToken.objects.create(
            user=user,
            application=app,
            token=generate_token(),
            expires=expires,
            scope="read write"
        )
       
        refresh_token=RefreshToken.objects.create(
            user=user,
            token=generate_token(),
            application=app,
            access_token=access_token
        )
        userdata=UserDetailsSerialzers(user,partial=True, context={"request": request})
        return Response({
            "tokenDetails": {
                'access_token': access_token.token,
                'expires_in': 900,
                'refresh_token': refresh_token.token,
                'token_type': 'Bearer',
                'scope': access_token.scope,
            },
            "userDetails":userdata.data ,
            "status": "Success",
            "message": "Welcome to the project"
        })


class RefreshTokenView(APIView):
    def post(self,request):
        refresh_token_str=request.data.get("refresh_token")
        if not refresh_token_str:
            return Response({"error":"Refresh token is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh_token=RefreshToken.objects.get(token=refresh_token_str)
        except RefreshToken.DoesNotExist:
            return Response({"error":"invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)
        user=refresh_token.user
        application=refresh_token.application

        if refresh_token.access_token:
            refresh_token.access_token.delete()

        new_access_token=AccessToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            expires=timezone.now()+timedelta(minutes=15)
            
        )

        if True:
            refresh_token.delete()
            new_refresh_token=RefreshToken.objects.create(
                user=user,
                token=generate_token(),
                application=application,
                access_token=new_access_token
            )
            refresh_token_str=new_refresh_token.token

        return Response({
            "access_token":new_access_token.token,
            "refresh_token":refresh_token_str,
            "expires_in": 900,
            "token_type": "Bearer",
            # "scope": new_access_token.scope
        },status=status.HTTP_201_CREATED)
    
class GetEntireUserdata(APIView):
    authentication_classes=[OAuth2Authentication]
    permission_classes=[IsAuthenticated]
    def post(self,request):
        userdata=UserDetails.objects.all()
        serialized=UserDetailsSerialzers(userdata,many=True,partial=True,context={"request": request})
        return Response(
            {"userdata":serialized.data}
        ,status=status.HTTP_200_OK)
    

class LogoutApiView(APIView):
    authentication_classes=[OAuth2Authentication]
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            token_str=auth_header.split()[1] if 'Bearer' in auth_header else None
            if not token_str:
                return Response({"error":"Access token is not provided"},status=400)
            token =AccessToken.objects.get(token=token_str)
            RefreshToken.objects.filter(access_token=token).delete()
            token.delete()
            return Response({"message":"Logout successfull, tokens are revoked"},status=200)
        except AccessToken.DoesNotExist:
            return Response({"error":'Invalid tokens'},status=400)
        except Exception as e:
            return Response({"error":str(e)},status=500)

    

# class AdminOnlyView(APIView):
#     permission_classes=[IsAuthenticated]
#     print(permission_classes)
#     def get(self,request):
#         if request.user.role!='admin':
#             return Response({"error":"only Admin allowed"},status=403)
#         return Response({"message":"Welocome Admin"})
    
# class SuperAdminOnlyView(APIView):
#     permission_classes=[IsAuthenticated]
#     def get(self,request):
#         if request.user.role != "superadmin":
#             return Response({"error":"only super admins are allowed"},status=403)
#         return Response({"message":"Welcome, Super admin"})

class GetSalutations(APIView):
    authentication_classes=[]
    permission_classes=[]

    #  def get(self, request):
    #     salutations = Salutations.objects.all()
    #     serializer = SalutationsSerailzer(salutations, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    def get(self,request):
        salutations=Salutations.objects.all()
        Serailazer=SalutationsSerailzer(salutations,many=True)
        return Response({"status":"Successs","data":Serailazer.data},status=200)
    
    def post(self,request):
        serializer=SalutationsSerailzer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"Success","data":serializer.data},status=200)
        return Response({
            "status":"error",
            "error":serializer.errors
        },status=400)
      
class GetTitledata(APIView):
    authentication_classes=[]
    permission_classes=[]
    def get(self,request):
        titlesdata=Titles.objects.all()
        print(titlesdata)
        titleSerializserdata=TitleSerialzer(titlesdata,many=True)
        return Response({"status":"Success","data":titleSerializserdata.data},status=200)
    
    def post(self,request):
        serialzer=TitleSerialzer(data=request.data)
        print("data is",serialzer)
        if serialzer.is_valid():
            serialzer.save()
            return Response({"status":"Success","data":serialzer.data},status=200)
        return Response({
            "status":"error",
            "error":serialzer.errors
        },status=400)

class RemoveUser(APIView):
    def delete(self, request, user_id):
        try:
            if len(UserDetails.objects.all())==1:
                return Response({
                    "status":"error",
                    "message":"Atleast one user is required for the project"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if user_id:
                user = UserDetails.objects.get(id=user_id)
                user.delete()
                return Response({
                    "status": "Success",
                    "message": "User removed successfully!"
                }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "An error occurred while deleting the user",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Multipledelete(APIView):
    def post(self,request):
        try:
            user_ids = [value for key, value in request.POST.items() if key.startswith('user_ids[')]
            print(user_ids)
            if not user_ids:
                return Response(
                    {
                        'status':"errror",
                        "message":"no user Id are provided"
                    },status=status.HTTP_400_BAD_REQUEST
                )
            if UserDetails.objects.count()-len(user_ids)<1:
                return Response(
                    {
                        "status":"error",
                        "message":"At least one User must be remain in the system"
                    },status=status.HTTP_400_BAD_REQUEST
                )
            deleted=0
            for UserId in user_ids:
                try:
                    user=UserDetails.objects.get(id=UserId)
                    user.delete()
                except ObjectDoesNotExist:
                    continue
            return Response({
                "status":"Success",
                "message":f"{deleted} users deleted Successfully!"
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status":"error",
                "message":f"{str(e)}"

            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditUserDetails(APIView):
    def patch(self,request,user_id):
        try:
            if user_id:
                user=UserDetails.objects.get(id=user_id)
        except UserDetails.DoesNotExist:
            return Response({
                "status":"error",
                "message":"User not found"
            },status=status.HTTP_404_NOT_FOUND)
        
        serailzerdata=UserDetailsSerialzers(user,data=request.data,partial=True,context={"action": "update"})
        print("seralizer data",serailzerdata)
        ## partial is true means you can send only the fields you want to update
        if serailzerdata.is_valid():
            serailzerdata.save()
            return Response({
                "status":"Success",
                "message":"User details has been updated successfully",
                "data":serailzerdata.data
            },status=status.HTTP_200_OK)
        return Response({
            "status":"error",
            "message":"Invalid data",
            "error":serailzerdata.errors
        },status=status.HTTP_404_NOT_FOUND)
    


# class fakeProductApis(APIView):
#     def get(self,request):
#         urls="https://fakestoreapi.com/products"
#         headers={'accept':"application/json"}
#         response=requests.get(urls,headers=headers)
#         data=response.json()
#         # print("data",)

#         saved_data=[]
#         errors = []
#         for item in data:
#             serializer=FakeProductDataSerailzer(data=data,many=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 saved_data.append(serializer.data)
#             else:
#                 errors.append(serializer.errors)
#         return Response(
#             {"saved": saved_data, "errors": errors},
#             status=status.HTTP_201_CREATED if saved_data else status.HTTP_400_BAD_REQUEST
#         )

class FakeProductApis(APIView):
    def get(self,request):
        urls="https://fakestoreapi.com/products"
        headers={'accept':"application/json"}
        response=requests.get(urls,headers=headers)
        data=response.json()

        api_data=[]
        for item in data:
            try:
                obj,created=FakeProductsData.objects.update_or_create(
                    id=item["id"],
                    defaults={
                        "title":item["title"],
                        "price":item["price"],
                        "description":item["description"],
                        "category":item["category"],
                        "image":item["image"],
                        "rating":item["rating"]
                    }
                )
                api_data.append({
                    "id":obj.id,
                    "title":obj.title,
                    "price":obj.price,
                    "description":obj.description,
                    "category":obj.category,
                    "image":obj.image,
                    "rating":obj.rating                    
                })
            except Exception as e:
                return Response({
                    "error":e,
                    "status":"error"
                },status=status.HTTP_204_NO_CONTENT)
        return Response({
            "data":api_data,
            
        },status=status.HTTP_200_OK if api_data else status
        .HTTP_500_INTERNAL_SERVER_ERROR)


class GetProductsList(APIView):
    authentication_classes=[OAuth2Authentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        url="https://api.escuelajs.co/api/v1/products"
        header={'accept':"application/json"}
        reponse=requests.get(url=url,headers=header)
        data=reponse.json()
        initial_data=[]
        for items in data:
            try:
                obj,created=Products.objects.update_or_create(
                    id=items["id"],
                    defaults={
                        "title": items["title"],
                        "price": items["price"],
                        "description": items["description"],
                        "images": json.dumps(items["images"]),
                        "created_at": items["creationAt"],
                        "updated_at": items["updatedAt"]
                    }
                )
                initial_data.append({
                    "id": obj.id,
                    "title": obj.title,
                    "price": obj.price,
                    "description": obj.description,
                    "images": json.loads(obj.images),
                    "created_at": obj.created_at,
                    "updated_at": obj.updated_at
                })
            except Exception as e:
                return Response({
                    "status":"error",
                    "error":str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    
                )
        
        return Response({
            "status":"success",
            "data":initial_data
        },status=status.HTTP_200_OK if initial_data else status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# class GetProductsList(APIView):
#     def get(self,request):
#         url="https://api.escuelajs.co/api/v1/products"
#         header={'accept':"application/json"}
#         reponse=requests.get(url=url,headers=header)
#         data=reponse.json()
#         initial_data=[]
#         for items in data:
#             try:
#                 obj,created=Products.objects.update_or_create(
#                     id=items["id"],
#                     defaults={
#                         "title": items["title"],
#                         "price": items["price"],
#                         "description": items["description"],
#                         "images": json.dumps(items["images"]),
#                         "created_at": items["creationAt"],
#                         "updated_at": items["updatedAt"]
#                     }
#                 )
#                 initial_data.append({
#                     "id": obj.id,
#                     "title": obj.title,
#                     "price": obj.price,
#                     "description": obj.description,
#                     "images": json.loads(obj.images),
#                     "created_at": obj.created_at,
#                     "updated_at": obj.updated_at
#                 })
#                 productsdata=Products.objects.all()
#                 serilazer=ProductsSerilazers(productsdata,many=True)
#                 print("products",serilazer)
#                 return Response({
#                     "status":"success",
#                     "data":serilazer.data
#                 },status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({
#                     "status":"error",
#                     "error":str(e)
#                 },status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    
#                 )
    
# class MoviesDataApi(APIView):
#     def get(self, request):
#         movies = Movies.objects.all()
#         serializer = MovieSerialzer(movies, many=True)   
#         return Response({
#             "status": "success",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = MovieSerialzer(data=request.data)  
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "status": "success",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "status": "error",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
class MoviesDataApi(APIView):
    def get(self, request, pk=None):  
        if pk:
            movie = Movies.objects.get(pk=pk)
            serializer = MovieSerialzer(movie)
            return Response(serializer.data)
        else:
            movies = Movies.objects.all()
            serializer = MovieSerialzer(movies, many=True)
            return Response(serializer.data)

# class UpdateUserDetailsApi(APIView):
#     def post(self,request,pk):
#         data=UserDetails.objects.get(pk=pk)
#         response=UserDetailsSerialzers(data, data=request.data, partial=True, context={"action": "update"})
#         try:
#             if response.data:
#                 obj,created=UserDetails.objects.update_or_create(data=request.data)
#                 return Response({
#                     "status":"success",
#                     "message":"The user data has been updated sucessfully!",
#                     "data":obj
#                 })
#         except Exception as e:
#             return Response({
#                 "status":"error",
#                 "message":str(e)
#             })
class UpdateUserDetailsApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes=[OAuth2Authentication]
    permission_classes=[IsAuthenticated]
    def post(self,request,pk):
    
        try:
            data=UserDetails.objects.get(pk=pk)
        except UserDetails.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
        print(request.data)
        serializer=UserDetailsSerialzers(data, data=request.data, partial=True, context={"request": request} )
        if serializer.is_valid():
                updated_data=serializer.validated_data
               
                # has_changes=any(
                #     getattr(data,field)!=value
                #     for field, value in updated_data.items()
                # )
                # if not has_changes:
                #     return Response({
                #         "status": "info",
                #         "message": "No changes detected. The data is the same as existing."
                #     }, status=status.HTTP_200_OK)

                serializer.save()
                print("demo",str(serializer.data))
                return Response({
                    "status":"success",
                    "message":"The user data has been updated sucessfully!",
                    "data":serializer.data
                },status=status.HTTP_200_OK)
        return Response({
            "status":"error",
            "error":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)
       


# class GetPartnersDataList(APIView):
#     def get(self, request):
#         try:
#             data = Partners.objects.all()
#             serializer = PartnerSerailzer(data, many=True) 
#             print('serializer',serializer.data)
#             return Response({
#                 "status": "success",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 "status": "error",
#                 "message": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPartnersDataList(APIView):
    # parser_classes = (MultiPartParser, FormParser)
    def get(self,request):
        try:
            data=Partners.objects.all()
            response_data=[]
            for partners in data:
                user=partners.created_user_id
                user_data=None
                if user:
                    user_data={
                        "id":user.id,
                        "first_name":user.first_name,
                        "last_name":user.last_name,
                        "email":user.email,
                        # "profile_image":user.profile_image
                    }
                response_data.append({
                    "id": partners.id,
                    "name": partners.name,
                    "address": partners.address,
                    "zip_code": partners.zip_code,
                    "is_active":partners.is_active,
                    "mobile_number": partners.mobile_number,
                    "created_user_id":user.id,
                    "created_user": user_data
                })
            return Response({
                "status":"success",
                "data":response_data
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)

            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class CreatePartnerAccount(APIView):
    def post(self, request):
        serializer = PartnerSerailzer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Partner has been created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as ve:
            return Response(
                {
                    "status": "error",
                    "message": "Validation failed",
                    "errors": ve.detail  
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RemovePartner(APIView):
    def delete(self,request,Partner_id):
        try:
            if Partner_id:
                partner=Partners.objects.get(id=Partner_id)
                partner.delete()
                return Response({
                    "status":"success",
                    "message":"Partner has been deleted sucessfully"
                },status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "status":"error",
                "message":"Partner not found"
            },status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
