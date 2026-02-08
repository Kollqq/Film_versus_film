import random

import os
import requests

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import Room, Participant, Movie, Match, Vote
from core.serializers import RoomSerializer, ParticipantSerializer, MovieSerializer, MatchSerializer, \
    MatchDetailSerializer

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w500"


def generate_code(length=6):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(alphabet) for _ in range(length))


@api_view(['GET'])
def search_movies(request):
    query = request.query_params.get('query', '').strip()
    if not query:
        return Response({'results': []})

    api_key = os.environ.get('TMDB_API_KEY')
    if not api_key:
        return Response({'error': 'TMDB_API_KEY not set'}, status=500)

    resp = requests.get(
        f"{TMDB_BASE_URL}/search/movie",
        params={"api_key": api_key, "query": query, "language": "en-US"},
        timeout=10,
    )
    if resp.status_code != 200:
        return Response({"error": "tmdb error"}, status=502)

    data = resp.json()
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "id": str(item.get("id")),
            "title": item.get("title") or "",
            "year": (item.get("release_date") or "")[:4],
            "poster_url": f"{TMDB_POSTER_BASE}{poster_path}" if poster_path else "",
        })

    return Response({"results": results})


@api_view(['POST'])
def create_room(request):
    code = generate_code()
    while Room.objects.filter(code=code).exists():
        code = generate_code()
    room = Room.objects.create(code=code)
    return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def join_room(request, code):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'name required'}, status=400)

    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)

    if room.participants.count() >= 2:
        return Response({'error': 'room full'}, status=400)

    participant = Participant.objects.create(room=room, name=name)
    return Response(ParticipantSerializer(participant).data, status=201)


@api_view(['POST'])
def add_movie(request, code):
    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)
    if room.is_started:
        return Response({'error': 'tournament already started'}, status=400)

    external_id = request.data.get('external_id')
    title = request.data.get('title')
    year = request.data.get('year', '')
    poster_url = request.data.get('poster_url', '')
    added_by_id = request.data.get('added_by')

    if not external_id or not title:
        return Response({'error': 'external_id and title required'}, status=400)

    added_by = None
    if added_by_id:
        added_by = Participant.objects.filter(id=added_by_id, room=room).first()

    movie, created = Movie.objects.get_or_create(
        room=room,
        external_id=external_id,
        defaults={'title': title, 'year': year, 'poster_url': poster_url, 'added_by': added_by},
    )
    if not created:
        return Response({'error': 'movie already added'}, status=400)

    return Response(MovieSerializer(movie).data, status=201)


def create_round(room, movies, round_num):
    random.shuffle(movies)
    i = 0
    while i < len(movies):
        if i == len(movies) - 1:
            Match.objects.create(
                room=room,
                round=round_num,
                movie_a=movies[i],
                movie_b=None,
                winner=movies[i],
                resolved_at=timezone.now(),
            )
            i += 1
            continue
        Match.objects.create(room=room, round=round_num, movie_a=movies[i], movie_b=movies[i + 1])
        i += 2


@api_view(['POST'])
def start_tournament(request, code):
    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)

    if room.is_started:
        return Response({'error': 'tournament already started'}, status=400)

    if room.participants.count() < 2:
        return Response({'error': 'need 2 participants'}, status=400)

    movies = list(room.movies.all())
    if len(movies) < 2:
        return Response({'error': 'need at least 2 movies'}, status=400)

    room.is_started = True
    room.current_round = 1
    room.save()

    create_round(room, movies, round_num=1)

    return Response({'status': 'started'})


@api_view(['GET'])
def current_match(request, code):
    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)

    match = room.matches.filter(winner__isnull=True).order_by('created_at').first()
    if not match:
        return Response({'message': 'no active match'}, status=200)

    return Response(MatchDetailSerializer(match).data, status=200)

def advance_tournament(room):
    if room.matches.filter(round=room.current_round, winner__isnull=True).exists():
        return

    winners = list(
        room.matches.filter(round=room.current_round)
        .exclude(winner__isnull=True)
        .values_list('winner_id', flat=True)
    )

    if len(winners) <= 1:
        return

    winner_movies = list(Movie.objects.filter(id__in=winners))
    room.current_round += 1
    room.save()
    create_round(room, winner_movies, round_num=room.current_round)


@api_view(['POST'])
def vote(request, code):
    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)

    match_id = request.data.get('match')
    participant_id = request.data.get('participant')
    movie_id = request.data.get('movie')

    match = Match.objects.filter(id=match_id, room=room).first()
    participant = Participant.objects.filter(id=participant_id, room=room).first()
    movie = Movie.objects.filter(id=movie_id, room=room).first()

    if not match or not participant or not movie:
        return Response({'error': 'invalid match/participant/movie'}, status=400)

    vote, created = Vote.objects.get_or_create(
        match=match,
        participant=participant,
        defaults={'movie': movie},
    )
    if not created:
        return Response({'error': 'vote already exists'}, status=400)

    if match.votes.count() >= 2:
        votes = list(match.votes.all())
        if votes[0].movie_id == votes[1].movie_id:
            winner = votes[0].movie
        else:
            winner = random.choice([match.movie_a, match.movie_b])
        match.winner = winner
        match.resolved_at = timezone.now()
        match.save()

        if match.winner:
            advance_tournament(room)

    return Response({'status': 'ok'})


@api_view(['GET'])
def winner(request, code):
    room = Room.objects.filter(code=code).first()
    if not room:
        return Response({'error': 'room not found'}, status=404)

    last_match = (
        room.matches.exclude(winner__isnull=True)
        .order_by('-round', '-resolved_at', '-id')
        .first()
    )
    if not last_match:
        return Response({'winner': None})

    return Response({
        'winner': {
            'id': last_match.winner.id,
            'title': last_match.winner.title,
            'year': last_match.winner.year,
            'poster_url': last_match.winner.poster_url,
        }
    })