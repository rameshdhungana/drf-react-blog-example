from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from .serializers import *
from .models import Question


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer

    # HTTP GET /question/
    # HTTP GET /question/?search=
    def get_queryset(self):
        search = self.request.query_params.get('search', '')
        tag = self.request.query_params.get('tag', '')

        if search:
            criteria = (
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
            )
        else:
            criteria = Q()
            # criteria = (Q(user_id=self.request.user.id))

        if tag:
            queryset = Question.objects.filter(criteria, Q(tags__name__exact=tag)).order_by('-registered_date')
        else:
            queryset = Question.objects.filter(criteria).order_by('-registered_date')

        return queryset

    # HTTP GET /question/last/
    @action(detail=False)
    def last(self, request):
        """
            Most recent question written by request user
        """
        queryset = self.get_queryset().filter(user=self.request.user).order_by('-registered_date').first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    # HTTP GET /question/latest/
    @action(detail=False)
    def latest(self, request):
        """
            Single latest registered question
        """
        # queryset = self.get_queryset().order_by('-registered_date')[:1]
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    # HTTP GET /question/latest/
    @action(detail=False)
    def latest(self, request):
        """
            Single latest registered question
        """
        # queryset = self.get_queryset().order_by('-registered_date')[:1]
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    # HTTP GET /tag/question/
    @action(detail=False)
    def recent(self, request):
        """
            Multiple questions ordered by registered date
        """
        queryset = self.get_queryset().order_by('-registered_date')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = QuestionSummarySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = QuestionSummarySerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)
