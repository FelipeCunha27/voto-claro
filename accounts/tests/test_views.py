from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestesDeViewsAutenticacao(TestCase):
    def setUp(self):
        # Cria um usuário de teste para usarmos no login e logout
        self.senha_teste = "senha_segura_123"
        self.usuario = User.objects.create_user(
            username="cidadao_teste",
            password=self.senha_teste,
            is_curator=False
        )

    def test_login_retorna_200(self):
        """A página de login deve carregar com sucesso."""
        resposta = self.client.get(reverse('login'))
        self.assertEqual(resposta.status_code, 200)

    def test_login_valido_autentica_usuario(self):
        """Usuário deve conseguir logar e iniciar uma sessão."""
        resposta = self.client.post(reverse('login'), {
            'username': 'cidadao_teste',
            'password': self.senha_teste
        })
        # Após logar com sucesso, o Django deve redirecionar (status 302)
        self.assertEqual(resposta.status_code, 302)
        # Verifica se a chave de sessão do usuário foi criada
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_logout_encerra_sessao(self):
        """Usuário logado deve conseguir encerrar a sessão."""
        # Força o login primeiro
        self.client.login(username='cidadao_teste', password=self.senha_teste)
        
        # Chama a rota de logout (recomendado via POST no Django 5+)
        resposta = self.client.post(reverse('logout'))
        
        # Verifica redirecionamento e se a sessão foi limpa
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_registrar_retorna_200(self):
        """A página de cadastro deve carregar com sucesso."""
        resposta = self.client.get(reverse('registrar'))
        self.assertEqual(resposta.status_code, 200)
