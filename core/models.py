from django.db import models

class Room(models.Model):
    code = models.CharField(max_length=12, unique=True)
    is_started = models.BooleanField(default=False)
    current_round = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Participant(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)

class Movie(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='movies')
    external_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    year = models.CharField(max_length=10, blank=True)
    poster_url = models.URLField(blank=True)
    added_by = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('room', 'external_id')

class Match(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='matches')
    round = models.PositiveIntegerField(default=1)
    movie_a = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='match_as_a')
    movie_b = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='match_as_b', null=True, blank=True)
    winner = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True, related_name='wins')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class Vote(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='votes')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('match', 'participant')