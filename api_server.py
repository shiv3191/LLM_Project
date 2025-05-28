from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from ass import AdvancedQAEvaluator
from functools import wraps

# Configuration
app = Flask(__name__)
CORS(app)
ENV = os.environ.get('FLASK_ENV', 'development')

# Initialize evaluator once at startup
def init_evaluator():
    try:
        evaluator = AdvancedQAEvaluator()
        print("✅ Evaluator initialized successfully")
        return evaluator
    except Exception as e:
        print(f"❌ Evaluator initialization failed: {str(e)}")
        if ENV == 'development':
            print("ℹ️ Ensure GEMINI_API_KEY is set in your .env file")
        return None

evaluator = init_evaluator()

# Decorators
def require_evaluator(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not evaluator:
            return jsonify({"error": "Service unavailable - evaluator not initialized"}), 503
        return f(*args, **kwargs)
    return decorated

def validate_json(*required_fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.get_json()
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({
                    "error": "Missing required fields",
                    "missing": missing
                }), 400
            return f(*args, **kwargs)
        return decorated
    return decorator

# Routes
@app.route('/api/ask', methods=['POST'])
@require_evaluator
@validate_json('question')
def ask_question():
    """Endpoint to get answer and evaluation for a question"""
    data = request.get_json()
    question = data['question'].strip()
    
    try:
        answer = evaluator.get_answer(question)
        if answer.startswith("Error getting answer:"):
            return jsonify({
                "question": question,
                "answer": answer,
                "error": "Answer generation failed",
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        
        evaluation = evaluator.evaluate_answer_advanced(question, answer)
        return jsonify({
            "question": question,
            "answer": answer,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if ENV == 'development' else None
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with more detailed status"""
    status = {
        "status": "healthy" if evaluator else "degraded",
        "evaluator_ready": evaluator is not None,
        "environment": ENV,
        "timestamp": datetime.utcnow().isoformat()
    }
    return jsonify(status)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = ENV == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)