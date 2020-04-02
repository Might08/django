from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from sign.models import Event, Guest


class ModelTests (TestCase):
    def setUp(self):
        Event.objects.create(id=1, name="oneplus 3 event", status=True, limit=2000, address="shenzhen", start_time="2016-08-31 02:18:22")
        Guest.objects.create(id=1, event_id=1, realname="alen", phone='13711001101',email="alen@mail.com", sign=False)

    def test_event_models(self):
        result = Event.objects.get(name="oneplus 3 event")
        self.assertEqual(result.address, "shenzhen")
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(phone="13711001101")
        self.assertEqual(result.realname, "alen")
        self.assertFalse(result.sign)

class IndexPageTest(TestCase):
    def test_index_page_renders_index_template(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

class LoginActionTest(TestCase):
    '''测试登录动作'''

    def setUp(self):                                     # 初始化，调用User.objects.create_user创建登录用户数据
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')

    def test_add_admin(self):
        '''测试添加的用户数据是否正确'''
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@mail.com')    # 注意这里书中有误，user表里的字段是email而不是mail，否则会报错

    def test_login_action_username_password_null(self):
        '''测试用户名密码为空'''
        test_data = {'username':'', 'password': ''}
        response = self.client.post('/login_action/', data=test_data)    # 通过post()方法请求'/login_aciton/'路径测试登录功能
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)   # assertIn()方法断言返回的HTML页面中是否包含指定的提示字符串

    def test_login_action_username_password_error(self):
        '''测试用户名密码错误'''
        test_data = {'username':'abc', 'password':'123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_success(self):
        '''测试登录成功'''
        test_data = {'username':'admin', 'password':'admin123456'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)    # 这里为什么断言的是302，是因为登录成功后，通过HttpResponseRedirect()跳转到了'/event_manage/'路径，这是一个重定向

class EventManageTest(TestCase):
    """测试发布会管理"""

    def setUp(self):
        '''初始化测试数据，包括登录用户数据，发布会数据'''
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(name='xiaomi5', limit=2000, address='beijing', status=1, start_time='2017-08-10 12:30:00')
        self.login_user = {'username':'admin', 'password':'admin123456'}    # 定义登录变量

    def test_event_manage_success(self):
        '''测试发布会：xiaomi5'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)

    def test_event_manage_search_success(self):
        '''测试发布会搜索'''
        # 这里自己给自己挖了个坑，post登录请求的时候少写了一个/，当时写成了'/login_action'，我擦一执行测试就返回302，排查了好半天才发现，哎，需要认真仔细啊
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/search_name/', {'name':'xiaomi5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)

class GuestManageTest(TestCase):
    """测试嘉宾管理"""

    def setUp(self):
        '''还是使用setUp初始化一些测试数据'''
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing', status=1, start_time='2017-08-10 12:30:00')
        Guest.objects.create(realname='alen', phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        self.login_user = {'username':'admin', 'password':'admin123456'}

    def test_event_manage_success(self):
        '''测试嘉宾信息：alen'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'18611001100', response.content)

class SignIndexActionTest(TestCase):
    """测试发布会签到"""

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1, start_time='2017-8-10 12:30:00')
        Event.objects.create(id=2, name="oneplus4", limit=2000, address='shenzhen', status=1, start_time='2017-6-10 12:30:00')
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname="una", phone=18611011101, email='una@mail.com', sign=1, event_id=2)
        self.login_user = {'username':'admin', 'password':'admin123456'}

    def test_event_models(self):
        '''测试添加的发布会数据'''
        result1 = Event.objects.get(name='xiaomi5')
        self.assertEqual(result1.address, 'beijing')
        self.assertTrue(result1.status)
        result2 = Event.objects.get(name='oneplus4')
        self.assertEqual(result2.address, 'shenzhen')
        self.assertTrue(result2.status)

    def test_guest_models(self):
        '''测试添加的嘉宾数据'''
        result = Guest.objects.get(realname='alen')
        self.assertEqual(result.phone, '18611001100')
        self.assertEqual(result.event_id, 1)
        self.assertFalse(result.sign)

    def test_sign_index_action_phone_null(self):
        '''测试手机号为空'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {"phone":""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"phone error.", response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        '''测试手机号或发布会id错误'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {"phone":"18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"event id or phone error.", response.content)

    def test_sign_index_action_user_sign_has(self):
        '''测试嘉宾已签到'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {"phone":"18611011101"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"user has sign in.", response.content)

    def test_sign_index_action_sign_success(self):
        '''测试嘉宾签到成功'''
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {"phone":"18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"sign in success!", response.content)