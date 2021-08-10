from django.utils.timezone import now
from datetime import datetime
from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Модель профиля пользователя"""
    MAN = "Мужчина"
    WOMAN = "Женщина"

    GENDER = (
        (MAN, 'Мужчина'),
        (WOMAN, "Женщина")
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, blank=True, null=True)
    gender = models.CharField(max_length=7, blank=True, null=True, choices=GENDER)
    birthday = models.DateField(blank=True, null=True)
    firstname = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'account'

    def __str__(self):
        if self.birthday:
            date_of_birt_str = f'дата рождения: {self.birthday.day}.{self.birthday.month}.{self.birthday.year}, ' \
                               f'возраст: {self.get_age()} лет'
        else:
            date_of_birt_str = f'дата рождения: не указана '

        return f'{self.user.email}, ' \
               f'{self.phone}, ' \
               f'{self.gender}, ' \
               f'{date_of_birt_str}'

    def get_age(self):

        if not self.birthday:
            return None

        today = datetime.date(now())
        born = self.birthday
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age
