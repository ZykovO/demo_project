from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg import openapi

class JWTScheme(SwaggerAutoSchema):
    def get_security_definitions(self):
        return {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT authorization header using the Bearer scheme. Example: "Bearer {token}"'
            }
        }

    def get_security_requirements(self):
        if getattr(self.view, 'swagger_require_auth', True):
            return [{'Bearer': []}]
        return []