from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


test_urls = [ 
			'http://molecularcasestudies.cshlp.org/content/early/2016/02/09/mcs.a000786.abstract',
		 	'http://molecularcasestudies.cshlp.org/content/2/2/a000703.abstract',
		 	'http://molecularcasestudies.cshlp.org/content/2/2/a000620.abstract'
		 	]


class PhenopacketScraperTests(APITestCase):
	
	def test_api(self):

		url= '/api/test/'
		data = {'arg' : 'OK'}
		response = self.client.get(url, data, format='json')
		print (response.data)

		assert response.data['arg'] == 'OK'
		assert response.status_code == 200

	
	def test_scraper(self):

		url = '/api/scrape/'

		for testurl in test_urls:
			data = { 'url' : str(testurl)}
			response = self.client.get(url, data, format='json')

			self.assertEqual(response.status_code, 200, msg=None)
			self.assertEqual(response.data['response'], 'OK')
			self.assertNotEqual(response.data['Abstract'], 'Not Found')
			self.assertNotEqual(response.data['HPO Terms'], 'Not Found')

	def test_annotator(self):
		url = '/api/annotate/'

		for testurl in test_urls:
			data = { 'url' : str(testurl)}
			response = self.client.get(url, data, format='json')

			self.assertEqual(response.status_code, 200, msg=None)
			self.assertEqual(response.data['response'], 'OK')
			self.assertNotEqual(response.data['Annotated Abstract'], '')
			self.assertNotEqual(response.data['Annotated HPO Terms'], [])

	def test_phenopacket(self):
		url = '/api/phenopacket/'

		for testurl in test_urls:
			data = { 'url' : str(testurl)}
			response = self.client.get(url, data, format='json')

			self.assertEqual(response.status_code, 200, msg=None)
			self.assertEqual(response.data['response'], 'OK')
			self.assertTrue(response.data['phenopacket'])


