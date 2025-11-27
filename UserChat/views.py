from django.shortcuts import render
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from .profile import profile


from .models import *
from .serializers import *
from .services import *
# Create your views here.
class UserChat(APIView):
    def post(self,request):
        print(request.data)
        user_input=request.data.get("user_input")
        if not user_input:
            return Response({
                "error":"user input is required"
            },status=400)
        
        api_response=ask_agent(user_input)
        print(api_response)
        chat=UserChatMessage.objects.create(
            user_input=user_input,
            api_response=api_response
        )
        return Response({
            "status":"success",
            "data":{ "user_input": chat.user_input,
            "ai_response": chat.api_response,
            "created_at": chat.created_at},

        },status=201)



client = OpenAI(api_key=settings.SECRET_API_KEY)


class Ask(APIView):
    def post(self, request):
        question = request.data.get("question")

        prompt = f"""
You are an AI agent who knows everything about Hemanth.

Here is the profile:
{profile}

Answer the question: {question}
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = completion.choices[0].message.content

        return Response({"answer": answer})
