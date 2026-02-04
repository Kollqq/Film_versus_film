from rest_framework import serializers
from .models import Room, Participant, Movie, Match, Vote


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'code', 'is_started', 'created_at']


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'room', 'name', 'joined_at']


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'room', 'external_id', 'title', 'year', 'poster_url', 'added_by']


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'room', 'movie_a', 'movie_b', 'winner', 'created_at', 'resolved_at']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'match', 'participant', 'movie']