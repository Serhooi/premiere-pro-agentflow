import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.video_project import db
from src.routes.user import user_bp
from src.routes.video import video_bp
from src.services.storage_service import init_storage_service
from src.services.queue_service import init_queue_manager

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# CORS для всех доменов (для разработки)
CORS(app, origins="*")

# Конфигурация
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Database configuration
# Для production используем PostgreSQL URL, для разработки - SQLite
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Исправляем URL для psycopg3
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    # PostgreSQL для production
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # SQLite для разработки
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация БД
db.init_app(app)

# Инициализация Supabase Storage
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    init_storage_service(supabase_url, supabase_key)
    print("✅ Supabase Storage initialized")
else:
    print("⚠️ Supabase credentials not found. Storage service disabled.")

# Инициализация Queue Manager
redis_url = os.getenv('REDIS_URL')
queue_manager = init_queue_manager(redis_url)

# Регистрация blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(video_bp, url_prefix='/api/video')

# Создание таблиц
with app.app_context():
    db.create_all()
    print("✅ Database tables created")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    queue_info = queue_manager.get_queue_info() if queue_manager else {'available': False}
    
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'agentflow-video-editor',
        'version': '1.0.0',
        'features': {
            'database': True,
            'storage': supabase_url is not None,
            'queue': queue_info.get('available', False),
            'cors': True
        },
        'queue_info': queue_info
    })

@app.route('/api/queue/status', methods=['GET'])
def queue_status():
    """Queue status endpoint"""
    if not queue_manager:
        return jsonify({
            'success': False,
            'error': 'Queue manager not initialized'
        }), 503
    
    return jsonify({
        'success': True,
        'queue_info': queue_manager.get_queue_info()
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files (React frontend)"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({
            'message': 'AgentFlow Video Editor Backend',
            'status': 'running',
            'api_docs': '/api/health'
        })

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'AgentFlow Video Editor Backend',
                'status': 'running',
                'api_docs': '/api/health'
            })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting AgentFlow Video Editor Backend on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🗄️ Database: {'PostgreSQL' if database_url else 'SQLite'}")
    print(f"📦 Storage: {'Supabase' if supabase_url else 'Disabled'}")
    print(f"🔄 Queue: {'Redis' if redis_url else 'Disabled'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

