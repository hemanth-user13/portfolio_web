from django.test import TestCase

# Create your tests here.
class GetPartnersDataList(APIView):
    def get(self, request):
        try:
            data = Partners.objects.all()
            response_data = []

            for partner in data:
                # prepare created_user data (subset of fields)
                user = partner.created_user_id  # ForeignKey relation (UserDetails object)
                user_data = None
                if user:
                    user_data = {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                    }

                response_data.append({
                    "id": partner.id,
                    "name": partner.name,
                    "address": partner.address,
                    "zip_code": partner.zip_code,
                    "mobile_number": partner.mobile_number,
                    "created_user": user_data
                })

            return Response({
                "status": "success",
                "data": response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
