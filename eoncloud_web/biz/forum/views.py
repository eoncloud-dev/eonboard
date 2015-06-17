from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import simplejson
import logging
from .serializer import ForumReplySerializer, ForumSerializer
from .models import Forum, ForumReply
from django.utils.translation import ugettext_lazy as _
LOG = logging.getLogger(__name__)


@api_view(['POST', 'GET'])
def forum_list_view(request, **kwargs):
    forum_set = Forum.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"]).order_by("-create_date")
    serializer = ForumSerializer(forum_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def forum_create_view(request, **kwargs):
    serializer = ForumSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        forums = serializer.save()
        serializer_ob = ForumSerializer(forums)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Creating Forum error'), "data": serializer_ob.data}, status=status.HTTP_201_CREATED)
    return Response({"OPERATION_STATUS": 0, "MSG": _('Creating Forum error')}, status=status.HTTP_201_CREATED)


@api_view(['GET','POST'])
def forum_reply_list_view(request, **kwargs):
    data = request.data
    forum_reply_set = ForumReply.objects.filter(forum=data.get("forum_id"),deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = ForumReplySerializer(forum_reply_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def forum_reply_create_view(request, **kwargs):
    serializer = ForumReplySerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"OPERATION_STATUS": 1, "MSG": _('Creating Forum reply success')}, status=status.HTTP_201_CREATED)
    return Response({"OPERATION_STATUS": 0, "MSG": _('Creating Forum reply error')}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def forum_close_forum_view(request, **kwargs):
    data = request.data
    try:
        if data.get('id') is not None:
            forum = Forum.objects.get(pk=data.get('id'))
            forum.status = True
            forum.save()
            serializer_ob = ForumSerializer(forum)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Close forum success'), "data": serializer_ob.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"OPERATION_STATUS": 0, "MSG": _('No selected forum')}, status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Close forum error,msg: %s" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Close Forum error')}, status=status.HTTP_201_CREATED)


