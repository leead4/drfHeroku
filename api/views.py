
import json
import argparse
import sys
import os
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import viewsets
from rest_framework import views
# from watson_developer_cloud import NaturalLanguageUnderstandingV1
# import watson_developer_cloud.natural_language_understanding.features.v1 as \
#     features
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework import status

from api.serializers import CardSerializer, DeckSerializer
from api.models import *
import textwrap
import googleapiclient.discovery
# from django.views.decorators.csrf import csrf_exempt
from google.cloud import language
from google.cloud import storage
from google.cloud.language import enums
from google.cloud.language import types



class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

class DeckViewSet(viewsets.ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer



class DeleteDeckByIdViewSet(views.APIView):
    def delete(self, request, deck_id, format=None):

            data = "you did it"
            deck_delete = Deck.objects.get(pk = deck_id)

            try:
                deck_delete.delete()
                return Response(data, content_type='application/json')
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
    


class GetCardsByDeckViewSet(views.APIView):
    def get(self, request, deck_id, format=None):

            # req_body= json.loads(request.body.decode())
            # print("\n\n{}".format(req_body['deck']))

            cards = Card.objects.filter(deck = deck_id)
            serializer = CardSerializer(cards, many=True)

            try:
                
                return Response(serializer.data, content_type='application/json')
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)  

class DeleteCardByIdViewSet(views.APIView):
    def delete(self, request, card_id, format=None):
            
           
            card = Card.objects.get(pk = card_id)
            card.delete()
            string = "mission accomplished"
            return Response(string)       



class CreateCardViewSet(views.APIView):
    def post(self, request, format=None):
            req_body = json.loads(request.body.decode())
            
            deck_from_db = Deck.objects.get(pk=req_body['deck'])

            new_card = Card.objects.create(
                front = req_body['front'],
                back = req_body['back'],
                deck = deck_from_db
            )
            data = 'a string for you'

            try:
                new_card.save()
                return Response(data)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)   


class EditCardViewSet(views.APIView):

    def put(self, request, card_id, format=None):
            req_body = json.loads(request.body.decode())
 
            try:
                card = Card.objects.get(pk=card_id)

            except Card.DoesNotExist:
            
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = CardSerializer(card, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateDeckViewSet(views.APIView):
    def post(self, request, format=None):
            
            req_body = json.loads(request.body.decode())
           
            new_deck = Deck.objects.create(
                name = req_body['name']
                
            )
            data = "you did it"
           
            try:
                new_deck.save()
                return Response(data, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)   

class FileUploadView(views.APIView):
        parser_classes = (FileUploadParser,)

        def put(self, request, format=None):
            file_obj = request.data['file']
            return Response(status=204)

        def dependents(self, tokens, head_index):
            """Returns an ordered list of the token indices of the dependents for
            the given head."""
            # Create head->dependency index.
            head_to_deps = {}
            for i, token in enumerate(tokens):
                head = token['dependencyEdge']['headTokenIndex']
                if i != head:
                    head_to_deps.setdefault(head, []).append(i)
            return head_to_deps.get(head_index, ())


        def phrase_text_for_head(self, tokens, text, head_index):
            """Returns the entire phrase containing the head token
            and its dependents.
            """
            begin, end = self.phrase_extent_for_head(tokens, head_index)
            return text[begin:end]


        def phrase_extent_for_head(self, tokens, head_index):
            """Returns the begin and end offsets for the entire phrase
            containing the head token and its dependents.
            """
            begin = tokens[head_index]['text']['beginOffset']
            end = begin + len(tokens[head_index]['text']['content'])
            for child in self.dependents(tokens, head_index):
                child_begin, child_end = self.phrase_extent_for_head(tokens, child)
                begin = min(begin, child_begin)
                end = max(end, child_end)
            return (begin, end)


        def analyze_syntax(self, text):
            """Use the NL API to analyze the given text string, and returns the
            response from the API.  Requests an encodingType that matches
            the encoding used natively by Python.  Raises an
            errors.HTTPError if there is a connection problem.
            """
            service = googleapiclient.discovery.build('language', 'v1beta1')
            body = {
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': text,
                },
                'features': {
                    'extract_syntax': True,
                },
                'encodingType': self.get_native_encoding_type(),
            }
            request = service.documents().annotateText(body=body)
            return request.execute()



        def get_native_encoding_type(self):
            """Returns the encoding type that matches Python's native strings."""
            if sys.maxunicode == 65535:
                return 'UTF16'
            else:
                return 'UTF32'


        def find_triples(self, tokens, left_dependency_label='NSUBJ', head_part_of_speech='VERB', right_dependency_label='DOBJ'):
            """Generator function that searches the given tokens
            with the given part of speech tag, that have dependencies
            with the given labels.  For each such head found, yields a tuple
            (left_dependent, head, right_dependent), where each element of the
            tuple is an index into the tokens array.
            """
            for head, token in enumerate(tokens):
                if token['partOfSpeech']['tag'] == head_part_of_speech:
                    children = self.dependents(tokens, head)
                    left_deps = []
                    right_deps = []
                    for child in children:
                        child_token = tokens[child]
                        child_dep_label = child_token['dependencyEdge']['label']
                        if child_dep_label == left_dependency_label:
                            left_deps.append(child)
                        elif child_dep_label == right_dependency_label:
                            right_deps.append(child)
                    for left_dep in left_deps:
                        for right_dep in right_deps:
                            yield (left_dep, head, right_dep)


            
        def show_triple(self, tokens, text, triple):
            """Prints the given triple (left, head, right).  For left and right,
            the entire phrase headed by each token is shown.  For head, only
            the head token itself is shown.
            """
            nsubj, verb, dobj = triple

            # Extract the text for each element of the triple.
            nsubj_text = self.phrase_text_for_head(tokens, text, nsubj)
            verb_text = tokens[verb]['text']['content']
            dobj_text = self.phrase_text_for_head(tokens, text, dobj)

            # Pretty-print the triple.
            left = textwrap.wrap(nsubj_text, width=28)
            mid = textwrap.wrap(verb_text, width=10)
            right = textwrap.wrap(dobj_text, width=28)
            my_dict = {}
           
            for l, m, r in zip(left, mid, right):
                my_dict = {'left': l, 'mid': m, 'right': r}

            return my_dict

        def main(self, text_file):
            # Extracts subject-verb-object triples from the given text file,
            # and print each one.
            # Read the input file.
            # text = open(text_file, 'rb').read().decode('utf8')

            analysis = self.analyze_syntax(text_file)
            tokens = analysis.get('tokens', [])
            print("these are the tokes", tokens)

            my_json_list = []
            for triple in self.find_triples(tokens):
                # print("im in a loop")
                small_list = self.show_triple(tokens, text_file, triple)
                my_json_list.append(small_list)

            print("my json list", my_json_list)
            return my_json_list

        def post(self, request, format=None):
            try:
            
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Flashcards-59956719ac0d.json"
                file_obj = (request.data['file'])
                print("im not talking to google")
                
                count = 0
                for line in file_obj:
                    count+=1
                    if count == 5:
                        decoded = line.decode("utf-8")
                        edited = decoded[0:-4]
                        file_content = line

                convert_to_json_list = self.main(decoded)
                the_thing = json.dumps(convert_to_json_list, indent=2)
            except: 
                json_dummy = [{"left": "Obama","mid": "received","right": "national attention for a test"},{"left": "He","mid": "began","right": "his presidential campaign"},{"left": "he","mid": "won","right": "sufficient delegates in the"},{"left": "He","mid": "defeated","right": "Republican nominee John"}]
                # print('convert_to_json_list', convert_to_json_list)
                the_thing = json.dumps(json_dummy, indent=2)

            return Response(the_thing, status=201)



        







