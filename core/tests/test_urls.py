from django.test import TestCase
from django.urls import resolve

class TestesDeRoteamentoBase(TestCase):
    def test_rotas_accounts_estao_configuradas(self):
        """A raiz do projeto deve incluir as rotas do app accounts."""
        resolvedor = resolve("/accounts/registrar/")
        self.assertEqual(resolvedor.view_name, "registrar")

    def test_rotas_panel_estao_configuradas(self):
        """A raiz do projeto deve incluir as rotas do app panel."""
        # panel.urls está incluído em path("") e mapeia "" para "panel_list"
        resolvedor = resolve("/")
        self.assertEqual(resolvedor.view_name, "panel_list")

    def test_rotas_bills_estao_configuradas(self):
        """A raiz do projeto deve incluir as rotas do app bills."""
        # bills.urls está incluído em path("") e mapeia "enviar/" para "enviar"
        resolvedor = resolve("/enviar/")
        self.assertEqual(resolvedor.view_name, "enviar")
