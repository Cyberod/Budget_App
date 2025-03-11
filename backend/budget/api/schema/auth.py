import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from .types import UserType

class Register(graphene.Mutation):
    class Arguments:
        username = graphene.String(required =True)
        password = graphene.String(required =True)
        email = graphene.String(required =True)

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    def mutate(self, info, username, password, email):
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise Exception("Username already exists")
        
        if User.objects.filter(email=email).exists():
            raise Exception("Email already exists")
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        return(
            Register(
                success =True,
                message = "User registerd successfully",
                user=user
            )
        )





class AuthMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    register = Register.Field()


