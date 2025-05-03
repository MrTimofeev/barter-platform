from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal

class APITestCaseBasic(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Ноутбук',
            description='Игровой',
            category='electronics',
            condition='used'
        )

    def test_get_ads(self):
        response = self.client.get('/api/ads/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_ad(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/ads/', {
            'title': 'Новый товар',
            'description': 'Описание',
            'category': 'books',
            'condition': 'new',
            'user': self.user.id,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ad.objects.count(), 2)

    def test_create_proposal(self):
        ad2 = Ad.objects.create(
            user=User.objects.create_user(username='another', password='pass'),
            title='Книга', description='...', category='books', condition='new'
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/proposals/', {
            'ad_sender': self.ad.id,
            'ad_receiver': ad2.id,
            'comment': 'Хочу обмен',
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ExchangeProposal.objects.count(), 1)

    def test_update_ad(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/ads/{self.ad.id}/', {'title': 'Обновлено'})
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Обновлено')

    def test_delete_ad(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/ads/{self.ad.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Ad.objects.count(), 0)
