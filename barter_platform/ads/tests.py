from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal

class AdsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Книга',
            description='Хорошая книга',
            category='books',
            condition='new'
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Телефон',
            description='Смартфон',
            category='electronics',
            condition='used'
        )

    def test_ad_creation(self):
        self.assertEqual(Ad.objects.count(), 2)
        self.assertEqual(str(self.ad1), 'Книга')

    def test_exchange_proposal_creation(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Обменяемся?',
        )
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(str(proposal), f'Предложение #{proposal.id} (pending)')

    def test_only_author_can_edit(self):
        self.client.login(username='user2', password='pass')
        url = reverse('ad_edit', kwargs={'pk': self.ad1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # доступ запрещён

    def test_delete_ad(self):
        self.client.login(username='user1', password='pass')
        url = reverse('ad_delete', kwargs={'pk': self.ad1.pk})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('ad_list'))
        self.assertFalse(Ad.objects.filter(pk=self.ad1.pk).exists())

    def test_search_ads(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('ad_list') + '?q=Книга')
        self.assertContains(response, 'Книга')

    def test_create_proposal(self):
        self.client.login(username='user1', password='pass')
        my_ad = self.ad1
        target_ad = self.ad2
        url = reverse('propose_exchange', kwargs={'sender_pk': my_ad.pk, 'receiver_pk': target_ad.pk})
        response = self.client.post(url, {'comment': 'Меняемся!'}, follow=True)
        self.assertContains(response, 'Предложение успешно отправлено!')
        self.assertEqual(ExchangeProposal.objects.count(), 1)

    def test_cannot_propose_to_self(self):
        self.client.login(username='user1', password='pass')
        url = reverse('propose_exchange', kwargs={'sender_pk': self.ad1.pk, 'receiver_pk': self.ad1.pk})
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Нельзя предлагать обмен на свой же товар')

    def test_cannot_duplicate_proposal(self):
        ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='...')
        self.client.login(username='user1', password='pass')
        url = reverse('propose_exchange', kwargs={'sender_pk': self.ad1.pk, 'receiver_pk': self.ad2.pk})
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Вы уже отправляли предложение')

    def test_accept_proposal(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='...')
        self.client.login(username='user2', password='pass')
        url = reverse('proposal_accept', kwargs={'pk': proposal.pk})
        response = self.client.post(url, follow=True)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')
        self.assertFalse(proposal.ad_sender.is_active)
        self.assertFalse(proposal.ad_receiver.is_active)

    def test_reject_proposal(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='...')
        self.client.login(username='user2', password='pass')
        url = reverse('proposal_reject', kwargs={'pk': proposal.pk})
        response = self.client.post(url, follow=True)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')
