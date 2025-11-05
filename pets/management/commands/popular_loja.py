from django.core.management.base import BaseCommand
from pets.models import Produto
import decimal

class Command(BaseCommand):
    help = 'Popula a loja com 15 produtos de exemplo.'

    def handle(self, *args, **options):
        # Limpa produtos antigos para evitar duplicatas
        self.stdout.write('Limpando produtos antigos...')
        Produto.objects.all().delete()

        produtos = [
            {'nome': 'Ração Premium Cães Adultos', 'emoji': '🐶', 'descricao': 'Pacote de 10kg, sabor carne e vegetais.', 'preco': decimal.Decimal('150.00'), 'estoque': 50},
            {'nome': 'Ração Premium Gatos Adultos', 'emoji': '🐱', 'descricao': 'Pacote de 5kg, sabor salmão.', 'preco': decimal.Decimal('120.00'), 'estoque': 40},
            {'nome': 'Coleira de Couro', 'emoji': '🏷️', 'descricao': 'Coleira de couro marrom, tamanho M.', 'preco': decimal.Decimal('45.50'), 'estoque': 30},
            {'nome': 'Arranhador Torre para Gatos', 'emoji': '🗼', 'descricao': 'Arranhador alto com 3 plataformas.', 'preco': decimal.Decimal('220.00'), 'estoque': 15},
            {'nome': 'Bolinha de Tênis (Pacote com 3)', 'emoji': '🎾', 'descricao': 'Bolinhas resistentes para cães.', 'preco': decimal.Decimal('25.00'), 'estoque': 100},
            {'nome': 'Cama Almofadada', 'emoji': '🛌', 'descricao': 'Cama super macia, lavável, tamanho G.', 'preco': decimal.Decimal('180.00'), 'estoque': 20},
            {'nome': 'Roda de Exercício para Hamster', 'emoji': '🐹', 'descricao': 'Roda silenciosa para gaiolas.', 'preco': decimal.Decimal('35.00'), 'estoque': 50},
            {'nome': 'Aquário 20 Litros', 'emoji': '🐠', 'descricao': 'Kit aquário completo com filtro e luz.', 'preco': decimal.Decimal('300.00'), 'estoque': 10},
            {'nome': 'Petisco Dental Care', 'emoji': '🦴', 'descricao': 'Pacote de petiscos para saúde bucal.', 'preco': decimal.Decimal('40.00'), 'estoque': 70},
            {'nome': 'Gaiola para Calopsita', 'emoji': '🦜', 'descricao': 'Gaiola espaçosa com poleiros e comedouros.', 'preco': decimal.Decimal('250.00'), 'estoque': 12},
            {'nome': 'Shampoo Hipoalergênico', 'emoji': '🧴', 'descricao': 'Shampoo suave para pets de pele sensível.', 'preco': decimal.Decimal('55.00'), 'estoque': 40},
            {'nome': 'Caixa de Transporte N°3', 'emoji': '✈️', 'descricao': 'Caixa padrão IATA para viagens aéreas.', 'preco': decimal.Decimal('190.00'), 'estoque': 8},
            {'nome': 'Fonte de Água para Gatos', 'emoji': '💧', 'descricao': 'Fonte bivolt que estimula o gato a beber água.', 'preco': decimal.Decimal('160.00'), 'estoque': 25},
            {'nome': 'Roupinha de Inverno (Moletom)', 'emoji': '🧥', 'descricao': 'Moletom cinza, tamanho P.', 'preco': decimal.Decimal('65.00'), 'estoque': 30},
            {'nome': 'Areia Higiênica Sílica', 'emoji': '🚽', 'descricao': 'Pacote de 1.8kg, alta absorção.', 'preco': decimal.Decimal('70.00'), 'estoque': 50},
        ]

        self.stdout.write(f'Criando {len(produtos)} produtos...')
        for item in produtos:
            Produto.objects.create(**item)

        self.stdout.write(self.style.SUCCESS(f'Loja populada com sucesso com {len(produtos)} produtos!'))