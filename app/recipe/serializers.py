from rest_framework import serializersfrom core.models import Tagclass TagSerializer(serializers.HyperlinkedModelSerializer):    class Meta:        model = Tag        fields = ('name', 'id')        read_only_fields = ('id',)