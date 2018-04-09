from django.contrib.auth.models import User
from api.models import * 
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('name')

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Document
		fields = ('description', 'document', 'uploaded_at')



class DeckSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.IntegerField(read_only = True)
	class Meta:

		model = Deck
		fields = ['name', 'id']

class CardSerializer(serializers.HyperlinkedModelSerializer):
	deck = serializers.CharField(source="deck.id")

	id = serializers.IntegerField(read_only = True)
	class Meta:
		model = Card
		fields = ('id', 'front', 'back', 'deck')

	def update(self, instance, validated_data):
		try:
			deck_data = validated_data.pop('deck')
			decks = (instance.deck).all()
			decks = list(decks)

			instance.front = validated_data.get('front', instance.front)
			instance.back = validated_data.get('back', instance.back)
			instance.save()

			for the_deck_data in deck_data:
			    deck = decks.pop(0)
			    deck.name = deck_data.name('name',deck.name)
			    deck.save()
			return instance
		except:
			
			deck_data = validated_data.get('deck', instance.deck)
			instance.front = validated_data.get('front', instance.front)
			instance.back = validated_data.get('back', instance.back)
			deck_data.save()

			return instance

