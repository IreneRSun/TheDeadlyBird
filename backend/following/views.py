from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers
from .models import Following, FollowingRequest
from .serializers import FollowRequestSerializer, FollowingSerializer
from identity.models import Author, InboxMessage
from deadlybird.permissions import RemoteOrSessionAuthenticated, SessionAuthenticated, IsGetRequest, IsPutRequest, IsPostRequest, IsDeleteRequest
from deadlybird.pagination import Pagination, generate_pagination_query_schema
from deadlybird.serializers import GenericErrorSerializer, GenericSuccessSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from deadlybird.settings import SITE_HOST_URL
from nodes.util import get_auth_from_host
import requests

@extend_schema(
    parameters=[
        OpenApiParameter("author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Author id to check for following"),
        OpenApiParameter("target_author_ids", type=str, location=OpenApiParameter.QUERY, description="Reduced subset of author ids to search from"),
        *generate_pagination_query_schema()
    ],
    responses=FollowingSerializer
)
@api_view(["GET"])
@permission_classes([RemoteOrSessionAuthenticated])
def following(request, author_id: str):
    """
    URL: ://service/authors/{AUTHOR_ID}/following
    GET [local, remote]: get a list of authors who AUTHOR_ID is following 
    query parameters:
        - target_author_ids: string[], a reduced subset of author_id's to search from.
    """
    # Get target author ids if target_author_ids parameter is present
    include_author_ids = []
    include_author_ids_str = request.query_params.get('include_author_ids', None)
    if include_author_ids_str:
        include_author_ids = list(map(int, include_author_ids_str.split(',')))

    # Search a subset of author ids if target_author_ids parameter is present
    if include_author_ids: 
        queryset = Following.objects.filter(
            target_author_id__in=include_author_ids, author_id=author_id
        ).select_related('author')\
         .order_by('id')
    # Otherwise search author ids
    else:
        queryset = Following.objects.filter(target_author_id=author_id)\
            .select_related('author')\
            .order_by('id')

    # Paginate results
    paginator = Pagination("following")
    page = paginator.paginate_queryset(queryset, request)
    
    # Return serialized results
    #TODO: refactor this
    if page is not None:
        authors = [following.author for following in page]
        serializer = FollowingSerializer(authors)
        return paginator.get_paginated_response(serializer.data)
    else:
        authors = [following.author for following in queryset]
        serializer = FollowingSerializer(authors)
        return Response(serializer.data)

@extend_schema(
    operation_id="api_authors_followers_retrieve_all",
    parameters=[
        OpenApiParameter("author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Author id to check for followers"),
        *generate_pagination_query_schema()
    ],
    responses=FollowingSerializer
)
@api_view(["GET"])
@permission_classes([RemoteOrSessionAuthenticated])
def followers(request, author_id: str):
    """
    URL: ://service/authors/{AUTHOR_ID}/followers
    GET [local, remote]: get a list of authors who are AUTHOR_ID's followers       
    """
    # Get authors who are following author id
    queryset = Following.objects.filter(target_author_id=author_id)\
        .select_related('author')\
        .order_by('id')

    # Paginate results
    paginator = Pagination("followers")
    page = paginator.paginate_queryset(queryset, request)
    
    # Return serialized results
    if page is not None:
        authors = [following.author for following in page]
        serializer = FollowingSerializer(authors)
        return paginator.get_paginated_response(serializer.data)
    else:
        authors = [following.author for following in queryset]
        serializer = FollowingSerializer(authors)
        return Response(serializer.data)  

@extend_schema(
    parameters=[
        OpenApiParameter("author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Author id to interact with"),
        OpenApiParameter("foreign_author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Foreign author id to interact with in relation to author id"),
    ]
)
@extend_schema(
    methods=["GET"],
    responses={
        400: GenericErrorSerializer,
        404: GenericErrorSerializer,
        200: FollowingSerializer
    }
)
@extend_schema(
    methods=["DELETE"],
    responses={
        400: GenericErrorSerializer,
        404: GenericErrorSerializer,
        204: GenericSuccessSerializer
    }
)
@extend_schema(
    methods=["PUT"],
    request=None,
    responses={
        400: GenericErrorSerializer,
        409: GenericErrorSerializer,
        201: GenericSuccessSerializer
    }
)

@api_view(['DELETE', 'PUT', 'GET'])
@permission_classes([(IsGetRequest & RemoteOrSessionAuthenticated) | ((IsDeleteRequest | IsPutRequest) & SessionAuthenticated)])
def modify_follower(request, author_id: str, foreign_author_id: str): 
    """ 
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    DELETE [local]: remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
    PUT [local]: Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID (must be authenticated)
    GET [local, remote] check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
    """
    # Check that request is not to self
    if author_id == foreign_author_id:
        return Response({
            "error": True,
            "message": "Can not request to self"
        }, status=400)

    following_author = Author.objects.filter(id=foreign_author_id).first()
    followed_author = Author.objects.filter(id=author_id).first()

    if not following_author or not followed_author:
        return Response({
            "error": True,
            "message": "Can not indentify one or both provided authors"
        }, status=404)
    
    remote_request = True if SITE_HOST_URL not in str(following_author.host) else False
    if remote_request:
        remote_host = following_author.host
        base_host = remote_host.split('/api')[0]
        url = base_host + reverse("modify_follower", kwargs={
            "author_id": author_id,
            "foreign_author_id": foreign_author_id 
        }) 
        auth = get_auth_from_host(remote_host) 
        
    if request.method == "DELETE":
        obj = get_object_or_404(Following, author_id=foreign_author_id, target_author_id=author_id)
        obj.delete()
        if remote_request: 
            remote_res = requests.delete(url=url, auth=auth) 
            if remote_res.status_code == 200:
                print("success! unfollowed remote author: ", following_author.display_name)
            else:
                print("failed to unfollow remote author")

        return Response({"error": False, "message": "Follower removed successfully."}, status=204)

    elif request.method == "PUT": 
        Following.objects.get_or_create(
            author_id=foreign_author_id,
            target_author_id=author_id
        )
        follow_req = FollowingRequest.objects.filter(
            author_id=foreign_author_id, 
            target_author_id=author_id
        ).first()

        if follow_req:
            inbox_msg = InboxMessage.objects.filter(content_id=follow_req.id).first()
            if inbox_msg:
                inbox_msg.delete()
            follow_req.delete()

        if remote_request:
            # duplicate PUT on remote server
            remote_res = requests.put(url=url, auth=auth)
            if remote_res.status_code == 200:
                print("sucess! local author now following remote author: ", following_author.display_name)
            else:
                print("failed to put remote author")

        return Response({"error": False, "message": "Follower added successfully."}, status=201)
    
    elif request.method == 'GET':
        obj = get_object_or_404(Following, author_id=foreign_author_id, target_author_id=author_id)
        serializer = FollowingSerializer(obj)
        return Response(serializer.data)
    
@extend_schema(
    parameters=[
        OpenApiParameter("local_author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Author id to interact with"),
        OpenApiParameter("foreign_author_id", type=str, location=OpenApiParameter.PATH, required=True, description="Foreign author id to interact with in relation to author id")
    ]
)
@extend_schema(
    methods=["POST"],
    request=None,
    responses={
        400: GenericErrorSerializer,
        403: GenericErrorSerializer,
        404: GenericErrorSerializer,
        409: GenericErrorSerializer,
        201: GenericSuccessSerializer,
        500: GenericErrorSerializer
    }
)
@extend_schema(
    methods=["GET"],
    responses={
        404: GenericErrorSerializer,
        200: FollowRequestSerializer
    }
)
@api_view(["POST", "GET"])
@permission_classes([RemoteOrSessionAuthenticated])
def request_follower(request: HttpRequest, local_author_id: str, foreign_author_id: str):
    """
    Request a follower on local or foreign host.
    URL: None specified
    """

    if request.method == "GET":
        # Get serialized following relation
        follow_req = get_object_or_404(FollowingRequest, 
                                       author_id=local_author_id, 
                                       target_author_id=foreign_author_id)
        serializer = FollowRequestSerializer(follow_req)
        return Response(serializer.data) 