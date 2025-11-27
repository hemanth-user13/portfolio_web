from django.urls import path
from .views import *

urlpatterns = [
    path('users/', UserDetailsView.as_view(), name='user-list-create'),
    path('register',RegisterUserApi.as_view(),name="User_register_api"),
    path('users/<int:id>', GetUserApiView.as_view(), name='user-detail'),
    path('users/list',GetentireUserList.as_view(),name="users_list"),
    path('useremail/',GetUserdatabyEmail.as_view(),name="User_data_by_email"),
    path('userdataemail/',GetUseremaildata.as_view(),name="get_user_data_email"),
    path('clientdetails',GetClientDetails.as_view(),name="get_client_details"),
    path('login',UserLoginApi.as_view(),name="user_login"),
    path('refresh-token', RefreshTokenView.as_view(), name='refresh_token'),
    path('userlist',GetEntireUserdata.as_view(),name="user_list"),
    path('logout',LogoutApiView.as_view(),name="user_logout_api"),
    path('salutations',GetSalutations.as_view(),name="Salutations"),
    path("Titles",GetTitledata.as_view(),name="titles_api"),
    path('deleteuser/<int:user_id>',RemoveUser.as_view(),name="remove_user"),
    path('multipledelete',Multipledelete.as_view(),name='Multiple delete'),
    path('users/edit/<int:user_id>',EditUserDetails.as_view(),name="edit_user_details"),
    path('fakeproducts',FakeProductApis.as_view(),name="fake_products"),
    path('products',GetProductsList.as_view(),name="products_list"),
    path("movies",MoviesDataApi.as_view(),name="Moviesdata"),
    path("movies/<int:pk>",MoviesDataApi.as_view(),name="movies"),
    path("user/update/<int:pk>",UpdateUserDetailsApi.as_view(),name="update_userdetails"),
    path('partners',GetPartnersDataList.as_view(),name="partner_list"),
    path('create/partner', CreatePartnerAccount.as_view(),name="create_partner"),
    path('remove/partner/<int:Partner_id>',RemovePartner.as_view(),name="remove_partner")

]
