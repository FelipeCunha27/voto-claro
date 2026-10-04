import uuid
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bills.models import Theme, Bill, Submission, AccessibleVersion

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula o banco de dados com Planos de Governo de demonstração para o portfólio'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando dados antigos...")
        AccessibleVersion.objects.all().delete()
        Submission.objects.all().delete()
        Bill.objects.all().delete()
        Theme.objects.all().delete()

        self.stdout.write("Iniciando setup de dados de demonstração (Planos de Governo)...")

        # 1. Criar Superusuário / Curador
        user, created = User.objects.get_or_create(username='admin')
        if created:
            user.set_password('admin123')
            user.is_staff = True
            user.is_superuser = True
            user.is_curator = True
            user.save()
            self.stdout.write(self.style.SUCCESS("✅ Usuário curador criado (admin / admin123)"))
        else:
            self.stdout.write("⚠️ Usuário admin já existe.")

        # 2. Criar Temas
        tema_educacao, _ = Theme.objects.get_or_create(name='Educação', slug='educacao')
        tema_cidade, _ = Theme.objects.get_or_create(name='Mobilidade Urbana', slug='mobilidade')
        
        # 3. Criar Plano de Governo Aprovado (Painel Público)
        bill_1, _ = Bill.objects.get_or_create(
            slug='plano-governo-educacao-2026',
            defaults={
                'title': 'Plano de Governo: Educação para o Futuro 2026 (Candidata A)',
                'theme': tema_educacao,
            }
        )
        
        sub_1, _ = Submission.objects.get_or_create(
            content_hash=hashlib.sha256(b"educacao_futuro").hexdigest(),
            defaults={
                'submitter': user,
                'title': 'Plano de Governo: Educação para o Futuro 2026',
                'source_text': 'O presente plano de governo visa estruturar a educação estadual com foco na erradicação do analfabetismo funcional...',
                'input_kind': Submission.InputKind.PASTED,
                'status': Submission.Status.PUBLISHED,
                'attempt_count': 1
            }
        )
        
        v_1, _ = AccessibleVersion.objects.get_or_create(
            submission=sub_1,
            defaults={
                'bill': bill_1,
                'version_number': 1,
                'summary': 'A proposta central da candidata foca em zerar a fila das creches e implementar ensino técnico em 100% das escolas estaduais.',
                'who_is_affected': 'Alunos da rede pública, professores estaduais e famílias buscando vagas em creches.',
                'practical_changes': '1. Construção de 150 novas creches públicas.\n2. Inclusão de disciplinas de programação no ensino médio.\n3. Bônus salarial anual para professores baseado no desempenho da escola.',
                'points_of_attention': 'O plano propõe distribuir tablets para todos os alunos, mas não explica detalhadamente de onde sairá o orçamento, o que pode aumentar a dívida do estado se não houver cortes em outras áreas.',
                'is_ai_generated': True,
                'review_state': AccessibleVersion.ReviewState.APPROVED
            }
        )
        
        bill_1.current_version = v_1
        bill_1.save()

        # 4. Criar Plano de Governo Pendente (Fila de Curadoria)
        bill_2, _ = Bill.objects.get_or_create(
            slug='plano-governo-sustentavel-2028',
            defaults={
                'title': 'Plano de Gestão Municipal: Nova Cidade Sustentável 2028 (Candidato B)',
                'theme': tema_cidade,
            }
        )
        
        sub_2, _ = Submission.objects.get_or_create(
            content_hash=hashlib.sha256(b"cidade_sustentavel").hexdigest(),
            defaults={
                'submitter': user,
                'title': 'Plano de Gestão Municipal: Nova Cidade Sustentável 2028',
                'source_text': 'Nossa gestão será pautada pela renovação da malha viária e transição energética da frota de transporte coletivo municipal...',
                'input_kind': Submission.InputKind.PASTED,
                'status': Submission.Status.GENERATED,
                'attempt_count': 1
            }
        )
        
        AccessibleVersion.objects.get_or_create(
            submission=sub_2,
            defaults={
                'bill': bill_2,
                'version_number': 1,
                'summary': 'Plano de prefeitura focado em mobilidade sustentável, prometendo ônibus elétricos e mudanças profundas na cobrança de tarifas no transporte.',
                'who_is_affected': 'Usuários de ônibus, motoristas de aplicativo e proprietários de imóveis nas regiões centrais.',
                'practical_changes': '1. Troca de 50% dos ônibus a diesel por veículos elétricos em 4 anos.\n2. Passe livre (tarifa zero) aos domingos para todos os cidadãos.\n3. Criação de 50km de novas ciclovias conectando o centro aos bairros periféricos.',
                'points_of_attention': 'Para financiar o passe livre aos domingos, o documento cita nas entrelinhas (página 42) a criação de uma taxa verde e o aumento do IPTU para imóveis de alto padrão na região central.',
                'is_ai_generated': True,
                'review_state': AccessibleVersion.ReviewState.PENDING
            }
        )

        self.stdout.write(self.style.SUCCESS("✅ Dados fictícios gerados com sucesso!"))
        self.stdout.write(self.style.SUCCESS("👉 Painel público tem 1 Plano de Governo aprovado."))
        self.stdout.write(self.style.SUCCESS("👉 Fila de curadoria tem 1 Plano de Governo pendente aguardando revisão."))
