# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class Vocabulary(models.Model):
    """
    This model stores a single vocabulary word, its meanings, and its
    frequency rank.
    """
    word = models.CharField(max_length=255, unique=True, db_index=True)
    meanings = models.JSONField(default=list) # Stores a list of strings
    frequency_rank = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['frequency_rank']
        verbose_name_plural = "Vocabularies"


class User(AbstractUser):
    """
    Extends Django's built-in User model to add relationships for
    known and learning words.
    """
    name = models.CharField(max_length=255, blank=True)

    motherLanguage = models.CharField(max_length=100, blank=True)
    targetLanguage = models.CharField(max_length=100, blank=True)
    fluencyLevel = models.CharField(max_length=50, blank=True)

    known_words = models.ManyToManyField(
        Vocabulary,
        related_name="known_by_users",
        blank=True
    )

    unknown_words = models.ManyToManyField(
        Vocabulary,
        related_name="unknown_by_users",
        blank=True
    )
    # The 'learning_words' field will be implicitly created by the model below.

    # We are overriding the default 'email' field to make it unique,
    # which is best practice for authentication.
    email = models.EmailField(unique=True)

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # 'username' is still required by default for admin


class UserLearningWord(models.Model):
    """
    This model tracks the words a user is actively learning using a
    Spaced Repetition System (SRS) based on the Ebbinghaus curve.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    
    srs_level = models.PositiveIntegerField(default=0)
    next_review_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'word')
        ordering = ['next_review_at']

    def __str__(self):
        return f"{self.user.email} learning '{self.word.word}' (Level: {self.srs_level})"

    def update_review_schedule(self, correctly_answered: bool):
        """
        Updates the srs_level and next_review_at based on user performance.
        """
        if correctly_answered:
            self.srs_level += 1
        else:
            self.srs_level = 0
        
        self.last_reviewed_at = timezone.now()

        # Consistent SRS interval schedule using timedelta
        # We can approximate a month as 30 days.
        srs_intervals = {
            0: timedelta(hours=4),
            1: timedelta(hours=8),
            2: timedelta(days=1),
            3: timedelta(days=3),
            4: timedelta(weeks=1),
            5: timedelta(weeks=2),
            6: timedelta(weeks=4),
            7: timedelta(days=120), # ~4 months
        }
        
        # Get the interval, defaulting to the max interval if the level is higher
        interval = srs_intervals.get(self.srs_level, timedelta(days=120))
        
        self.next_review_at = timezone.now() + interval
        self.save() # Corrected save call

