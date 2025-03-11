import graphene
from .queries import Query
from .mutations import Mutation
from .auth import AuthMutation

class RootMutation(AuthMutation, Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=RootMutation)
