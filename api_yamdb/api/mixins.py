from rest_framework import mixins, viewsets


class CreateListDestroy(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    pass
