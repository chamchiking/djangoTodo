from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
# from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from django.urls import resolve

from todos.serializers import UserSerializer

CREATE_USER_URL = reverse('user-list')
TOKEN_URL = reverse('login')
ME_URL = reverse('user-me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 유저 한명 미리 생성
        payload = {
            'email': 'test@test.com',
            'username': 'testme',
            'password': 'ckalscjf11',
        }
        create_user(**payload)
    
    def test_create_valid_user_success(self):
        # 새로운 유저 생성 제대로 이루어지는지, token은 만들어지는지 테스트
        payload = {
            'email': 'test1@test.com',
            'username': 'testme1',
            'password': 'ckalscjf11',
            're_password': 'ckalscjf11',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        # ----------------------------------
        self.assertIn('auth_token', res.data)
        # login_res = self.client.post(ME_URL)
    
    def test_user_exists(self):
        # 존재하는 유저 다시 생성안되는지 테스트
        payload = {
            'email': 'test@test.com',
            'username': 'testme',
            'password': 'ckalscjf11',
            're_password': 'ckalscjf11',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # password가 너무 짧은것 실패하는지 확인
        payload = {
            'email': 'test2@test.com',
            'username': 'testme2',
            'password': '12',
            're_password': '12',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # 유저에게 토큰이 발급됐는지 테스트
        payload = {'username': 'testme', 'password': 'ckalscjf11',}
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('auth_token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # 잘못된 유저에게 토큰이 발급되지 않는 것 테스트
        payload = {'username': 'testme', 'password': '123123123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('auth_token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        # 인증이 안된 경우 me를 호출했을 때 오류 발생
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 유저 한명 미리 생성
        self.user = create_user(
            email = 'test@test.com',
            username = 'testme',
            password = 'ckalscjf11',
        )
        self.client.force_authenticate(user = self.user)

    def test_retrieve_user_authorized(self):
        user_payload = UserSerializer(self.user)
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,user_payload.data)