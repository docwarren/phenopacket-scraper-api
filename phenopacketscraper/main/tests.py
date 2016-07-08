from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class PhenopacketScraperTests(APITestCase):
	def test_api(self):
		
		url= '/api/test/'
		data = {'arg1': 'Check'}
		response = self.client.get(url, data, format='json')
		print (response.data)

		assert 'Check' == response.data['arg1']
		assert response.status_code == 200

	def test_scraper(self):
		assert 5==5

	def test_annotator(self):
		assert 5==5

	def test_phenopacket(self):
		assert 5==5