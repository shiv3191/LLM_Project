import google.generativeai as genai
import json
from typing import Dict, Optional
import nltk
from rouge_score import rouge_scorer
from sacrebleu import BLEU
import os
import re
import textwrap  # Added missing import

class AdvancedQAEvaluator:
    """
    Advanced Q&A Evaluator using Gemini API with LLM-as-a-Judge approach.
    Combines NLP metrics (ROUGE, BLEU) with LLM-based qualitative evaluation.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the evaluator with API key and required models.
        
        Args:
            api_key: Gemini API key. If None, will try to get from GEMINI_API_KEY environment variable.
        """
        # Configure API key
        self._setup_api_key(api_key)
        
        # Initialize models and tools
        self._initialize_nltk()
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.bleu_scorer = BLEU()
        self.model = self._initialize_gemini_model()
    
    def _setup_api_key(self, api_key: Optional[str]) -> None:
        """Configure the Gemini API key."""
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please set GEMINI_API_KEY environment variable.")
        genai.configure(api_key=api_key)
    
    def _initialize_nltk(self) -> None:
        """Initialize NLTK with required resources."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def _initialize_gemini_model(self) -> genai.GenerativeModel:
        """Initialize the Gemini model with fallback options."""
        model_priority_list = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        
        for model_name in model_priority_list:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                model.generate_content("Test connection")
                print(f"✅ Successfully initialized model: {model_name}")
                return model
            except Exception as e:
                print(f"⚠️ Failed to initialize {model_name}: {str(e)}")
                continue
        
        raise RuntimeError("Could not initialize any Gemini model. Please check your API key and available models.")
    
    def get_answer(self, question: str) -> str:
        """
        Get an answer from the Gemini model.
        
        Args:
            question: The question to ask
            
        Returns:
            The generated answer or error message
        """
        try:
            response = self.model.generate_content(question)
            return response.text
        except Exception as e:
            return f"Error getting answer: {str(e)}"
    
    def generate_reference_answer(self, question: str) -> str:
        """
        Generate a high-quality reference answer using LLM-as-a-Judge approach.
        
        Args:
            question: The question to generate reference for
            
        Returns:
            The generated reference answer
        """
        prompt = f"""As an expert evaluator, generate the IDEAL reference answer for this question:
        
        Question: {question}
        
        Requirements:
        - Maximum comprehensiveness and detail
        - Perfect structure and clarity
        - Complete coverage of all aspects
        - Actionable and specific guidance
        - Include examples and best practices
        
        Provide the most comprehensive answer possible that covers:
        - Specific details and concrete examples
        - Step-by-step actionable guidance
        - Proper structure and organization
        - Relevant context and explanations
        - Potential pitfalls and solutions
        
        Reference Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating reference: {str(e)}"
    
    def _calculate_rouge(self, answer: str, reference: str) -> Dict:
        """Calculate ROUGE scores between answer and reference."""
        try:
            scores = self.rouge_scorer.score(reference, answer)
            return {
                'rouge1': scores['rouge1'].fmeasure,
                'rouge2': scores['rouge2'].fmeasure,
                'rougeL': scores['rougeL'].fmeasure
            }
        except Exception as e:
            print(f"ROUGE calculation error: {str(e)}")
            return {'rouge1': 0, 'rouge2': 0, 'rougeL': 0}
    
    def _calculate_bleu(self, answer: str, reference: str) -> float:
        """Calculate BLEU score between answer and reference."""
        try:
            # Simple tokenization with fallback
            try:
                answer_tokens = nltk.word_tokenize(answer.lower())
                reference_tokens = nltk.word_tokenize(reference.lower())
            except:
                answer_tokens = re.findall(r"\w+", answer.lower())
                reference_tokens = re.findall(r"\w+", reference.lower())
            
            score = self.bleu_scorer.sentence_score(
                ' '.join(answer_tokens),
                [' '.join(reference_tokens)]
            )
            return score.score / 100.0
        except Exception as e:
            print(f"BLEU calculation error: {str(e)}")
            return 0.0
    
    def evaluate_answer(self, question: str, answer: str) -> Dict:
        """
        Comprehensive evaluation of an answer using multiple metrics.
        
        Args:
            question: The original question
            answer: The answer to evaluate
            
        Returns:
            Dictionary with evaluation results
        """
        if answer.startswith("Error"):
            return self._error_response("Original answer generation failed")
        
        print("🔄 Generating reference answer...")
        reference = self.generate_reference_answer(question)
        
        print("📊 Calculating NLP metrics...")
        rouge_scores = self._calculate_rouge(answer, reference)
        bleu_score = self._calculate_bleu(answer, reference)
        
        print("⚖️ Running LLM-as-a-Judge evaluation...")
        llm_eval = self._llm_judge_evaluation(question, answer, rouge_scores, bleu_score)
        
        return {
            **llm_eval,
            'reference_answer': reference,
            'rouge_scores': rouge_scores,
            'bleu_score': bleu_score,
            'metrics_summary': self._create_metrics_summary(rouge_scores, bleu_score),
            'evaluation_method': 'LLM-as-a-Judge with ROUGE/BLEU'
        }
    
    def _llm_judge_evaluation(self, question: str, answer: str, rouge_scores: Dict, bleu_score: float) -> Dict:
        """
        Perform LLM-as-a-Judge evaluation with enhanced prompting.
        
        Args:
            question: Original question
            answer: Answer to evaluate
            rouge_scores: Dictionary of ROUGE scores
            bleu_score: BLEU score
            
        Returns:
            Dictionary with evaluation results
        """
        metrics_context = f"""
        Objective Metrics (for reference):
        - ROUGE-1: {rouge_scores.get('rouge1', 0):.3f}
        - ROUGE-2: {rouge_scores.get('rouge2', 0):.3f}
        - ROUGE-L: {rouge_scores.get('rougeL', 0):.3f}
        - BLEU: {bleu_score:.3f}
        """
        
        prompt = f"""
        [Expert Evaluation Task]
        Evaluate this Q&A pair based on:
        - Accuracy - Correctness of information
        - Completeness - Coverage of the topic
        - Clarity - Organization and readability
        - Depth - Level of detail provided
        - Usefulness - Practical value
        
        Question: {question}
        Answer: {answer}
        
        {metrics_context}
        
        Provide evaluation in this exact JSON format:
        {{
            "verdict": "EXCELLENT/GOOD/FAIR/POOR",
            "score": 1-10,
            "reasoning": "Detailed analysis",
            "strengths": ["list", "of", "strengths"],
            "improvements": ["suggested", "improvements"],
            "detail_score": 1-10,
            "clarity_score": 1-10,
            "accuracy_score": 1-10,
            "completeness_score": 1-10
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = self._clean_json_response(response.text)
            result = json.loads(response_text)
            
            # Standardize the output format
            return {
                'llm_judge_verdict': result.get('verdict', 'UNKNOWN'),
                'quality': self._verdict_to_quality(result.get('verdict')),
                'score': result.get('score', 0),
                'reasoning': result.get('reasoning', 'No reasoning provided'),
                'strengths': result.get('strengths', []),
                'missing_elements': result.get('improvements', []),
                'content_depth': result.get('detail_score', 0),
                'clarity': result.get('clarity_score', 0),
                'accuracy': result.get('accuracy_score', 0),
                'completeness': result.get('completeness_score', 0),
                'judge_confidence': min(10, max(1, result.get('score', 5)))  # Map score to confidence
            }
        except Exception as e:
            print(f"LLM Judge error: {str(e)}")
            return self._error_response(f"LLM Judge evaluation failed: {str(e)}")
    
    def _clean_json_response(self, text: str) -> str:
        """Clean JSON response from LLM."""
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        return text
    
    def _verdict_to_quality(self, verdict: str) -> str:
        """Convert verdict to simple quality label."""
        verdict = str(verdict).upper()
        if verdict in ['EXCELLENT', 'GOOD']:
            return 'GOOD'
        elif verdict in ['FAIR', 'POOR', 'BAD']:
            return 'BAD'
        return 'UNKNOWN'
    
    def _create_metrics_summary(self, rouge_scores: Dict, bleu_score: float) -> Dict:
        """Create summary of metrics with interpretation."""
        overall = (rouge_scores.get('rouge1', 0) * 0.4 + 
                  rouge_scores.get('rouge2', 0) * 0.3 + 
                  rouge_scores.get('rougeL', 0) * 0.2 + 
                  bleu_score * 0.1)
        
        if overall >= 0.75:
            interpretation = "Excellent match with reference"
        elif overall >= 0.5:
            interpretation = "Good match with some variations"
        elif overall >= 0.25:
            interpretation = "Partial match with significant differences"
        else:
            interpretation = "Low similarity to reference"
        
        return {
            'overall_score': overall,
            'interpretation': interpretation,
            **rouge_scores,
            'bleu_score': bleu_score
        }
    
    def _error_response(self, message: str) -> Dict:
        """Create standardized error response."""
        return {
            'llm_judge_verdict': 'ERROR',
            'quality': 'ERROR',
            'score': 0,
            'reasoning': message,
            'strengths': [],
            'missing_elements': [],
            'content_depth': 0,
            'clarity': 0,
            'accuracy': 0,
            'completeness': 0,
            'judge_confidence': 0
        }
    
    def display_results(self, evaluation: Dict) -> None:
        """Display evaluation results in a user-friendly format."""
        print("\n" + "=" * 80)
        print("📊 EVALUATION RESULTS".center(80))
        print("=" * 80)
        
        # Basic info
        verdict = evaluation.get('llm_judge_verdict', 'UNKNOWN')
        print(f"\n⚖️ Verdict: {verdict}")
        print(f"⭐ Overall Score: {evaluation.get('score', 0)}/10")
        print(f"🔍 Method: {evaluation.get('evaluation_method', 'Unknown')}")
        
        # Detailed scores
        print("\n📋 Detailed Scores:")
        print(f"  - Depth: {evaluation.get('content_depth', 0)}/10")
        print(f"  - Clarity: {evaluation.get('clarity', 0)}/10")
        print(f"  - Accuracy: {evaluation.get('accuracy', 0)}/10")
        print(f"  - Completeness: {evaluation.get('completeness', 0)}/10")
        
        # NLP metrics
        metrics = evaluation.get('metrics_summary', {})
        if metrics:
            print("\n📈 NLP Metrics:")
            print(f"  - ROUGE-1: {metrics.get('rouge1', 0):.3f}")
            print(f"  - ROUGE-2: {metrics.get('rouge2', 0):.3f}")
            print(f"  - ROUGE-L: {metrics.get('rougeL', 0):.3f}")
            print(f"  - BLEU: {metrics.get('bleu_score', 0):.3f}")
            print(f"  - Overall: {metrics.get('overall_score', 0):.3f} ({metrics.get('interpretation', '')})")
        
        # Reasoning
        print("\n🧠 Evaluation Reasoning:")
        print(textwrap.fill(evaluation.get('reasoning', 'No reasoning provided'), width=80))
        
        # Strengths
        if evaluation.get('strengths'):
            print("\n✨ Strengths:")
            for strength in evaluation['strengths']:
                print(f"  • {strength}")
        
        # Improvements
        if evaluation.get('missing_elements'):
            print("\n🔧 Suggested Improvements:")
            for item in evaluation['missing_elements']:
                print(f"  • {item}")
        
        print("=" * 80)

def main():
    """Main interactive loop."""
    print("🔍 Gemini Q&A Evaluator - LLM-as-a-Judge")
    print("Type 'quit' to exit\n")
    
    try:
        evaluator = AdvancedQAEvaluator()
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        return
    
    while True:
        question = input("\nEnter your question: ").strip()
        if question.lower() in ('quit', 'exit', 'q'):
            break
            
        if not question:
            continue
            
        print("\nGenerating answer...")
        answer = evaluator.get_answer(question)
        print("\nAnswer:")
        print("-" * 50)
        print(answer)
        print("-" * 50)
        
        if not answer.startswith("Error"):
            evaluation = evaluator.evaluate_answer(question, answer)
            evaluator.display_results(evaluation)
        
        if input("\nContinue? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()