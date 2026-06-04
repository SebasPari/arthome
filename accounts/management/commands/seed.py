from django.core.management.base import BaseCommand
from accounts.models import CustomUser, ArtistProfile
from offerings.models import Offering


ARTISTS = [
    {
        'email': 'maya@example.com',
        'full_name': 'Maya Leclerc',
        'discipline': 'Illustration',  # already French
        'bio': 'Ink and watercolour illustrator specialising in botanical and portrait work.',
        'location': 'Montreal, QC',
        'offerings': [
            {
                'title': 'Botanical Illustration Class',
                'description': 'Learn to draw and paint plants from life using traditional ink and watercolour techniques. All levels welcome.',
                'category': 'class',
                'price': 65,
                'price_type': 'fixed',
                'location': 'Studio 4B, Montreal',
            },
            {
                'title': 'Custom Portrait Commission',
                'description': 'A hand-drawn portrait in my signature ink-wash style. Delivered as a high-res scan + original.',
                'category': 'commission',
                'price': 220,
                'price_type': 'fixed',
            },
        ],
    },
    {
        'email': 'oscar@example.com',
        'full_name': 'Oscar Villanueva',
        'discipline': 'Musique',
        'bio': 'Jazz guitarist and composer available for live performances, private lessons, and event bookings.',
        'location': 'Toronto, ON',
        'offerings': [
            {
                'title': 'Private Guitar Lessons',
                'description': 'One-on-one jazz guitar lessons tailored to your level. Focus on improvisation, chord theory, and repertoire.',
                'category': 'class',
                'price': 80,
                'price_type': 'hourly',
            },
            {
                'title': 'Live Jazz Trio — Events',
                'description': 'Book my trio for dinners, gallery openings, weddings, and private events. 2–4 hour sets.',
                'category': 'performance',
                'price': None,
                'price_type': 'contact',
            },
        ],
    },
    {
        'email': 'seren@example.com',
        'full_name': 'Seren Aydin',
        'discipline': 'Danse',
        'bio': 'Contemporary dancer and choreographer offering classes, workshops, and improvisation nights.',
        'location': 'Vancouver, BC',
        'offerings': [
            {
                'title': 'Contemporary Dance Workshop',
                'description': 'A 3-hour movement workshop exploring somatic awareness and improvisation. No prior dance experience needed.',
                'category': 'event',
                'price': 45,
                'price_type': 'fixed',
                'location': 'The Cultch, Vancouver',
            },
            {
                'title': 'Monthly Improvisation Night',
                'description': 'Open-floor improv session — dancers, movers, and curious bodies welcome. Facilitated jams every last Friday.',
                'category': 'event',
                'price': 15,
                'price_type': 'fixed',
                'location': 'Roundhouse Community Centre',
            },
        ],
    },
    {
        'email': 'felix@example.com',
        'full_name': 'Félix Tremblay',
        'discipline': 'Photographie',
        'bio': 'Documentary and portrait photographer. Available for editorial, event, and personal projects.',
        'location': 'Quebec City, QC',
        'offerings': [
            {
                'title': 'Portrait Session',
                'description': 'A 90-minute outdoor or studio portrait session. Includes 20 edited images delivered within one week.',
                'category': 'commission',
                'price': 350,
                'price_type': 'fixed',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample artists and offerings'

    def handle(self, *args, **kwargs):
        for data in ARTISTS:
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['email'],
                    'full_name': data['full_name'],
                    'role': CustomUser.ROLE_ARTIST,
                },
            )
            if created:
                user.set_password('demo1234')
                user.save()
                self.stdout.write(f'  Created user: {user.full_name}')
            else:
                self.stdout.write(f'  Skipped (exists): {user.full_name}')

            profile, _ = ArtistProfile.objects.get_or_create(
                user=user,
                defaults={
                    'discipline': data['discipline'],
                    'bio': data['bio'],
                    'location': data.get('location', ''),
                },
            )

            for o in data['offerings']:
                Offering.objects.get_or_create(
                    artist=user,
                    title=o['title'],
                    defaults={
                        'description': o['description'],
                        'category': o['category'],
                        'price': o.get('price'),
                        'price_type': o['price_type'],
                        'location': o.get('location', ''),
                    },
                )

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
