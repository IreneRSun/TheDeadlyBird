# Utility file to factor out the large inbox view in views.py
import requests
from django.http import HttpRequest
from rest_framework.response import Response
from .models import Author, InboxMessage
from following.models import Following, FollowingRequest 
from identity.util import check_authors_exist
from deadlybird.settings import SITE_HOST_URL
from nodes.util import get_auth_from_host
from django.urls import reverse
import json
import os
from deadlybird.util import resolve_remote_route
  

def handle_follow_inbox(request: HttpRequest):
    """
    scenario 1) to_author is on a remote node.
        - use python requests to forward payload.

    scenario 2) to_author is on a local node.
        - save inbox message Object locally.
    """  
    to_author = request.data.get('object')
    from_author = request.data.get('actor')
    
    if not check_authors_exist(to_author["id"], from_author["id"]):
      return Response({
        "error": True,
        "message": "An author provided does not exist"
      }, status=404)

    from_author = Author.objects.get(id=from_author["id"])
    to_author = Author.objects.get(id=to_author["id"])

    if Following.objects.filter(author__id=from_author.id,
                                target_author__id=to_author.id).exists(): 
        return Response({
            "error": True,
            "message": "Conflict: Author is already following"
        }, status=409)
    elif FollowingRequest.objects.filter(author__id=from_author.id, 
        target_author__id=to_author.id).exists():
            return Response({
                "error": True,
                "message": "Conflict: Outstanding request in existence"
            }, status=409) 
    try:
      receiving_host = to_author.host
      if SITE_HOST_URL not in receiving_host:
        # Remote Following Request

        url = resolve_remote_route(receiving_host, "inbox", {
           "author_id": to_author.id
        })

        auth = get_auth_from_host(receiving_host)
        if auth is not None and url is not None: 
          print("auth: ", auth, "url: ", url, "data:", json.dumps(request.data))
          res = requests.post(
            url=url,
            headers={'Content-Type': 'application/json'}, 
            data=json.dumps(request.data), 
            auth=auth
          )
          if res.status_code == 201:
            return Response("Successfuly sent remote follow request", status=201) 
          else:
            return Response({"error": True, "message": "Remote post Failed"}, status=res.status_code)
        else:
           return Response("Failed to retrieve authentication and form url", status=500) 

      else:
        # Local Following Request
        follow_req = FollowingRequest.objects.create(
            target_author_id=to_author.id,
            author_id=from_author.id
        )
        InboxMessage.objects.create(
            author_id=to_author.id,
            content_id=follow_req.id,
            content_type=InboxMessage.ContentType.FOLLOW
        ) 
      return Response({
        "error": False,
        "message": "Successfuly created follow request and inbox message."
      }, status=201)   
    except:
      return Response({
          "error": True,
          "message": "Failed to create FollowRequest or InboxMessage"
      }, status=500) 
      