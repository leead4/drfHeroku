from django.db import models


class Deck(models.Model):
	name = models.CharField(max_length=400, blank=True)
	
class Card(models.Model):
	front = models.CharField(max_length=400, blank=True)
	back = models.CharField(max_length=400, blank=True)
	deck = models.ForeignKey(Deck, null=True, on_delete=models.CASCADE)

	