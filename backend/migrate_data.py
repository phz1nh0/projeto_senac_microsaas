import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Cliente, ProdutoEstoque, OrdemServico, Usuario

# SQLite URI
sqlite_uri = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'app.db')}"

# MySQL URI
mysql_uri = "mysql+pymysql://root:123456@localhost/assistencia_tecnica"

def migrate_data():
    # Connect to SQLite
    sqlite_engine = create_engine(sqlite_uri)
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()

    # Connect to MySQL
    mysql_engine = create_engine(mysql_uri)
    MySQLSession = sessionmaker(bind=mysql_engine)
    mysql_session = MySQLSession()

    try:
        # Migrate Clientes
        clientes = sqlite_session.query(Cliente).all()
        for cliente in clientes:
            new_cliente = Cliente(
                nome=cliente.nome,
                cpf_cnpj=cliente.cpf_cnpj,
                tipo_pessoa=cliente.tipo_pessoa,
                endereco=cliente.endereco,
                email=cliente.email,
                telefone=cliente.telefone,
                observacoes=cliente.observacoes,
                status=cliente.status,
                criado_em=cliente.criado_em,
                atualizado_em=cliente.atualizado_em
            )
            mysql_session.add(new_cliente)
        mysql_session.commit()
        print(f"Migrated {len(clientes)} clientes")

        # Migrate ProdutoEstoque
        produtos = sqlite_session.query(ProdutoEstoque).all()
        for produto in produtos:
            new_produto = ProdutoEstoque(
                codigo=produto.codigo,
                nome=produto.nome,
                categoria=produto.categoria,
                descricao=produto.descricao,
                quantidade=produto.quantidade,
                estoque_minimo=produto.estoque_minimo,
                preco_custo=produto.preco_custo,
                preco_venda=produto.preco_venda,
                fornecedor=produto.fornecedor,
                localizacao=produto.localizacao,
                criado_em=produto.criado_em,
                atualizado_em=produto.atualizado_em
            )
            mysql_session.add(new_produto)
        mysql_session.commit()
        print(f"Migrated {len(produtos)} produtos")

        # Migrate Usuarios
        usuarios = sqlite_session.query(Usuario).all()
        for usuario in usuarios:
            new_usuario = Usuario(
                usuario=usuario.usuario,
                senha_hash=usuario.senha_hash,
                nome=usuario.nome,
                email=usuario.email,
                ativo=usuario.ativo,
                criado_em=usuario.criado_em,
                atualizado_em=usuario.atualizado_em
            )
            mysql_session.add(new_usuario)
        mysql_session.commit()
        print(f"Migrated {len(usuarios)} usuarios")

        # Migrate OrdemServico (after clientes)
        ordens = sqlite_session.query(OrdemServico).all()
        for ordem in ordens:
            new_ordem = OrdemServico(
                numero_os=ordem.numero_os,
                cliente_id=ordem.cliente_id,
                tipo_aparelho=ordem.tipo_aparelho,
                marca_modelo=ordem.marca_modelo,
                imei_serial=ordem.imei_serial,
                cor_aparelho=ordem.cor_aparelho,
                problema_relatado=ordem.problema_relatado,
                diagnostico_tecnico=ordem.diagnostico_tecnico,
                prazo_estimado=ordem.prazo_estimado,
                valor_orcamento=ordem.valor_orcamento,
                status=ordem.status,
                prioridade=ordem.prioridade,
                observacoes=ordem.observacoes,
                criado_em=ordem.criado_em,
                atualizado_em=ordem.atualizado_em
            )
            mysql_session.add(new_ordem)
        mysql_session.commit()
        print(f"Migrated {len(ordens)} ordens")

        print("Data migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        mysql_session.rollback()
    finally:
        sqlite_session.close()
        mysql_session.close()

if __name__ == "__main__":
    migrate_data()
