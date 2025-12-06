from flask import Flask, redirect, jsonify, request, send_file
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
import os

from config import get_config
from extensions import db, migrate


def create_app():
    """App factory principal."""
    app = Flask(__name__, static_folder='../', static_url_path='/')
    CORS(app)  # Enable CORS for all routes
    app.config.from_object(get_config())

    db.init_app(app)
    migrate.init_app(app, db)

    # Importa models para que o Migrate reconheça
    from models import Cliente, ProdutoEstoque, OrdemServico, Usuario  # noqa: F401

    # Cria todas as tabelas no banco de dados
    with app.app_context():
        db.create_all()

    # Blueprints
    from routes_clientes import bp as clientes_bp
    from routes_os import bp as os_bp
    from routes_estoque import bp as estoque_bp

    app.register_blueprint(clientes_bp, url_prefix="/api/clientes")
    app.register_blueprint(os_bp, url_prefix="/api/os")
    app.register_blueprint(estoque_bp, url_prefix="/api/estoque")

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.route('/')
    def index():
        return redirect('/login.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_file(os.path.join(app.static_folder, 'img', 'logo.png'), mimetype='image/vnd.microsoft.icon')

    # Error handlers globais para garantir retorno JSON nas rotas da API
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        """Trata erros de integridade do banco de dados."""
        db.session.rollback()
        # Se for uma rota da API, retorna JSON
        if request.path.startswith('/api/'):
            error_str = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
            if "unique constraint failed" in error_str:
                campo = "campo único"
                if "cpf_cnpj" in error_str:
                    campo = "CPF/CNPJ"
                elif "codigo" in error_str:
                    campo = "código"
                elif "numero_os" in error_str:
                    campo = "número da OS"
                return jsonify({
                    "erro": "Violação de constraint único",
                    "mensagem": f"Já existe um registro com este {campo}"
                }), 409
            return jsonify({
                "erro": "Erro de integridade no banco de dados",
                "mensagem": "Não foi possível realizar a operação devido a restrições do banco de dados"
            }), 409
        # Para outras rotas, deixa o Flask tratar normalmente
        raise

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Trata erros internos do servidor."""
        # Se for uma rota da API, retorna JSON
        if request.path.startswith('/api/'):
            return jsonify({
                "erro": "Erro interno do servidor",
                "mensagem": "Ocorreu um erro inesperado. Tente novamente mais tarde."
            }), 500
        # Para outras rotas, deixa o Flask tratar normalmente
        raise

    @app.errorhandler(404)
    def handle_not_found(e):
        """Trata erros 404."""
        # Se for uma rota da API, retorna JSON
        if request.path.startswith('/api/'):
            return jsonify({
                "erro": "Recurso não encontrado",
                "mensagem": "O recurso solicitado não foi encontrado"
            }), 404
        # Para outras rotas, deixa o Flask tratar normalmente
        raise

    @app.errorhandler(400)
    def handle_bad_request(e):
        """Trata erros 400."""
        # Se for uma rota da API, retorna JSON
        if request.path.startswith('/api/'):
            mensagem = str(e.description) if hasattr(e, 'description') else "Requisição inválida"
            return jsonify({
                "erro": "Requisição inválida",
                "mensagem": mensagem
            }), 400
        # Para outras rotas, deixa o Flask tratar normalmente
        raise

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
