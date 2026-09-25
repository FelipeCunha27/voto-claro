from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestesDeAutenticacao(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_teste", 
            password="senha_segura123"
        )
        self.url_login = reverse('login')
        self.url_logout = reverse('logout')

    def test_login_retorna_200(self):
        """O GET na view de login deve retornar status 200."""
        resposta = self.client.get(self.url_login)
        self.assertEqual(resposta.status_code, 200)

    def test_login_sucesso_redireciona(self):
        """Um POST com credenciais válidas deve autenticar e redirecionar."""
        resposta = self.client.post(self.url_login, {
            'username': 'usuario_teste',
            'password': 'senha_segura123'
        })
        self.assertEqual(resposta.status_code, 302)

    def test_login_falha_retorna_erros(self):
        """Um POST com credenciais inválidas deve retornar erro no formulário."""
        resposta = self.client.post(self.url_login, {
            'username': 'usuario_teste',
            'password': 'senha_errada'
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context['form'].errors)

    def test_logout_redireciona(self):
        """O POST na view de logout deve deslogar o usuário e redirecionar."""
        self.client.login(username='usuario_teste', password='senha_segura123')
        # Django >= 5.0 requer POST para logout seguro
        resposta = self.client.post(self.url_logout)
        self.assertEqual(resposta.status_code, 302)

    def test_registrar_retorna_200(self):
        """O GET na view de registro deve retornar status 200."""
        url_registrar = reverse('registrar')
        resposta = self.client.get(url_registrar)
        self.assertEqual(resposta.status_code, 200)

    def test_registrar_sucesso_cria_usuario(self):
        """Um POST válido no registro deve criar o usuário e redirecionar."""
        url_registrar = reverse('registrar')
        resposta = self.client.post(url_registrar, {
            'username': 'novo_usuario',
            'email': 'novo@example.com',
            'password1': 'senha_nova123',
            'password2': 'senha_nova123',
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(User.objects.filter(username='novo_usuario').exists())

    def test_registrar_falha_senhas_diferentes(self):
        """Um POST com senhas divergentes não deve criar usuário."""
        url_registrar = reverse('registrar')
        resposta = self.client.post(url_registrar, {
            'username': 'novo_usuario2',
            'email': 'novo2@example.com',
            'password1': 'senha_nova123',
            'password2': 'outra_senha',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(User.objects.filter(username='novo_usuario2').exists())
        self.assertTrue(resposta.context['form'].errors)
