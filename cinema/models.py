from django.db import models


class Theatre(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    language = models.CharField(max_length=50, blank=True)
    rating = models.CharField(max_length=10, blank=True)  # U, UA, A
    poster = models.ImageField(upload_to="posters/", blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Screen(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, related_name="screens")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.theatre.name} - {self.name}"


class Seat(models.Model):
    class SeatType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        PREMIUM = "PREMIUM", "Premium"

    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name="seats")
    row_label = models.CharField(max_length=2)
    number = models.PositiveSmallIntegerField()
    seat_type = models.CharField(max_length=10, choices=SeatType.choices, default=SeatType.STANDARD)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["screen", "row_label", "number"], name="unique_seat_in_screen"
            )
        ]
        ordering = ["row_label", "number"]

    def __str__(self):
        return f"{self.row_label}{self.number}"


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name="showtimes")
    starts_at = models.DateTimeField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.movie.title} @ {self.starts_at:%d %b %H:%M}"