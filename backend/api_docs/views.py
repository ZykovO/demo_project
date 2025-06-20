from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from api_docs.custom_scheme import JWTScheme


class SchemaView(APIView):
    swagger_schema = JWTScheme

    @swagger_auto_schema(
        operation_description="API documentation",
        responses={200: "OK"}
    )
    def get(self, request):
        pass