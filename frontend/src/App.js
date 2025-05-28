import React, { useState } from 'react';
import axios from 'axios';
import { 
  Send, 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle, 
  Loader2, 
  Gauge, 
  TrendingUp, 
  Scale, 
  BrainCircuit,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Wand2,
  ClipboardCheck,
  BarChart2,
  Info,
  Lightbulb,
  Rocket,
  CheckCircle2,
  AlertCircle,
  Zap,
  Code,
  BookOpen,
  ShieldCheck,
  LayoutDashboard,
  GitBranch,
  Cpu,
  FlaskConical
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'https://llm-qna-evaluator-v2-production.up.railway.app/api';

const formatAnswerText = (text) => {
  if (!text) return '';
  
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\* (.*$)/gim, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, (match) => {
      const items = match.split('</li>').filter(item => item.trim());
      return '<ul>' + items.map(item => item + '</li>').join('') + '</ul>';
    })
    .replace(/\n/g, '<br>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
};

function App() {
  const [question, setQuestion] = useState('');
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (id, section) => {
    setExpandedSections(prev => ({
      ...prev,
      [`${id}-${section}`]: !prev[`${id}-${section}`]
    }));
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: question.trim()
      });

      const newConversation = {
        id: Date.now(),
        question: question.trim(),
        answer: response.data.answer,
        evaluation: response.data.evaluation,
        timestamp: new Date().toLocaleString()
      };

      setConversations(prev => [newConversation, ...prev]);
      setQuestion('');
    } catch (err) {
      setError('Failed to get answer. Please try again later.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  const renderScoreBar = (score, max = 10) => {
    const percentage = (score / max) * 100;
    let colorClass = '';
    
    if (percentage >= 70) colorClass = 'excellent';
    else if (percentage >= 50) colorClass = 'good';
    else if (percentage >= 30) colorClass = 'average';
    else colorClass = 'poor';

    return (
      <div className="score-bar-container">
        <div className="score-bar-background">
          <div 
            className={`score-bar-fill ${colorClass}`} 
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <span className="score-value">{score}/{max}</span>
      </div>
    );
  };

  const renderMetricCircle = (value, label) => {
    const percentage = value * 100;
    let colorClass = '';
    
    if (percentage >= 70) colorClass = 'excellent';
    else if (percentage >= 50) colorClass = 'good';
    else if (percentage >= 30) colorClass = 'average';
    else colorClass = 'poor';

    return (
      <div className="metric-circle-container">
        <div className={`metric-circle ${colorClass}`}>
          <span>{percentage.toFixed(1)}%</span>
        </div>
        <span className="metric-label">{label}</span>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-container">
          <div className="logo">
            <div className="logo-icon">
              <BrainCircuit size={28} />
            </div>
            <div>
              <h1>AI Answer Evaluator</h1>
              <p>Advanced LLM-powered Q&A quality assessment</p>
            </div>
          </div>
          <div className="header-badge">
            <Cpu size={16} />
            <span>LLM-as-a-Judge v2.0</span>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="input-container">
          <div className="input-box glass">
            <div className="input-group">
              <textarea
                id="question-input"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask any question (e.g., 'Explain quantum computing in simple terms')..."
                rows="3"
                disabled={loading}
              />
              <div className="input-footer">
                <div className="input-hint">
                  <Info size={16} />
                  <span>Press Enter to submit, Shift+Enter for new line</span>
                </div>
                <button 
                  onClick={askQuestion} 
                  disabled={loading || !question.trim()}
                  className={loading ? 'loading' : ''}
                >
                  {loading ? (
                    <>
                      <Loader2 className="spinner" />
                      Evaluating...
                    </>
                  ) : (
                    <>
                      <Zap size={18} />
                      Evaluate Answer
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="results-container">
          {conversations.length === 0 ? (
            <div className="empty-state glass">
              <div className="empty-content">
                <Wand2 size={48} className="empty-icon" />
                <h3>No evaluations yet</h3>
                <p>Ask a question to see the AI evaluation in action</p>
                
                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon">
                      <LayoutDashboard size={24} />
                    </div>
                    <h4>Comprehensive Analysis</h4>
                    <p>Detailed breakdown of answer quality</p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">
                      <GitBranch size={24} />
                    </div>
                    <h4>Multi-Model</h4>
                    <p>Evaluates using multiple LLM approaches</p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">
                      <FlaskConical size={24} />
                    </div>
                    <h4>Scientific Metrics</h4>
                    <p>ROUGE, BLEU and semantic analysis</p>
                  </div>
                </div>

                <div className="examples">
                  <h4>
                    <Lightbulb size={20} />
                    Try these example questions:
                  </h4>
                  <ul>
                    <li>"How do I optimize React component performance?"</li>
                    <li>"Explain blockchain technology to a beginner"</li>
                    <li>"What are the latest advancements in AI?"</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            conversations.map(conv => (
              <div key={conv.id} className="evaluation-card glass">
                {/* Question Section */}
                <div className="question-section">
                  <div className="section-header">
                    <div className="section-icon">
                      <MessageSquare size={20} />
                    </div>
                    <div>
                      <h3>Question</h3>
                      <span className="timestamp">{conv.timestamp}</span>
                    </div>
                  </div>
                  <p className="question-text">{conv.question}</p>
                </div>

                {/* Answer Section */}
                <div className="answer-section">
                  <div className="section-header">
                    <div className="section-icon">
                      <BookOpen size={20} />
                    </div>
                    <h3>AI Answer</h3>
                  </div>
                  <div 
                    className="answer-text" 
                    dangerouslySetInnerHTML={{ __html: formatAnswerText(conv.answer) }}
                  />
                </div>

                {/* Evaluation Section */}
                {conv.evaluation && (
                  <div className={`evaluation-section ${conv.evaluation.quality ? conv.evaluation.quality.toLowerCase() : ''}`}>
                    <div className="evaluation-header">
                      <div className="verdict">
                        {conv.evaluation.quality === 'GOOD' ? (
                          <>
                            <div className="verdict-icon">
                              <ShieldCheck size={32} />
                            </div>
                            <div>
                              <h3>High Quality Answer</h3>
                              <p>This answer meets high standards for accuracy and usefulness</p>
                            </div>
                          </>
                        ) : conv.evaluation.quality === 'BAD' ? (
                          <>
                            <div className="verdict-icon">
                              <AlertTriangle size={32} />
                            </div>
                            <div>
                              <h3>Low Quality Answer</h3>
                              <p>This answer needs improvement in several areas</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="verdict-icon">
                              <AlertCircle size={32} />
                            </div>
                            <div>
                              <h3>Evaluation Error</h3>
                              <p>Could not complete the evaluation</p>
                            </div>
                          </>
                        )}
                      </div>
                      <div className="overall-score">
                        <div className="score-display">
                          <span>Overall Score</span>
                          <div className="score-value">
                            {conv.evaluation.score || 0}<span>/10</span>
                          </div>
                        </div>
                        {renderScoreBar(conv.evaluation.score || 0)}
                      </div>
                    </div>

                    {/* Collapsible Sections */}
                    <div className="collapsible-sections">
                      {/* LLM Judge Assessment */}
                      <div className="collapsible-section">
                        <button 
                          className="section-toggle"
                          onClick={() => toggleSection(conv.id, 'judge')}
                        >
                          <div className="toggle-header">
                            <div className="toggle-icon">
                              <BrainCircuit size={20} />
                            </div>
                            <h4>LLM Judge Assessment</h4>
                          </div>
                          {expandedSections[`${conv.id}-judge`] ? (
                            <ChevronUp size={20} className="chevron" />
                          ) : (
                            <ChevronDown size={20} className="chevron" />
                          )}
                        </button>
                        {expandedSections[`${conv.id}-judge`] && (
                          <div className="section-content">
                            <div className="judge-reasoning">
                              <h5>Evaluation Reasoning</h5>
                              <p>{conv.evaluation.reasoning || 'No reasoning provided'}</p>
                            </div>
                            
                            <div className="score-grid">
                              <div className="score-item">
                                <span>Content Depth</span>
                                {renderScoreBar(conv.evaluation.content_depth || 0)}
                              </div>
                              <div className="score-item">
                                <span>Clarity</span>
                                {renderScoreBar(conv.evaluation.clarity || 0)}
                              </div>
                              <div className="score-item">
                                <span>Actionability</span>
                                {renderScoreBar(conv.evaluation.actionability || 0)}
                              </div>
                              <div className="score-item">
                                <span>Comprehensiveness</span>
                                {renderScoreBar(conv.evaluation.comprehensiveness || 0)}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* NLP Metrics */}
                      {conv.evaluation.metrics_summary && (
                        <div className="collapsible-section">
                          <button 
                            className="section-toggle"
                            onClick={() => toggleSection(conv.id, 'metrics')}
                          >
                            <div className="toggle-header">
                              <div className="toggle-icon">
                                <BarChart2 size={20} />
                              </div>
                              <h4>Objective NLP Metrics</h4>
                            </div>
                            {expandedSections[`${conv.id}-metrics`] ? (
                              <ChevronUp size={20} className="chevron" />
                            ) : (
                              <ChevronDown size={20} className="chevron" />
                            )}
                          </button>
                          {expandedSections[`${conv.id}-metrics`] && (
                            <div className="section-content">
                              <div className="metrics-grid">
                                {renderMetricCircle(conv.evaluation.metrics_summary.rouge1_fmeasure || 0, "ROUGE-1")}
                                {renderMetricCircle(conv.evaluation.metrics_summary.rougeL_fmeasure || 0, "ROUGE-L")}
                                {renderMetricCircle(conv.evaluation.metrics_summary.bleu_score || 0, "BLEU")}
                                {renderMetricCircle(conv.evaluation.metrics_summary.overall_similarity || 0, "Similarity")}
                              </div>
                              <div className="metrics-interpretation">
                                <h5>Interpretation</h5>
                                <p>{conv.evaluation.metrics_summary.interpretation || 'No interpretation provided'}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Strengths & Improvements */}
                      <div className="collapsible-section">
                        <button 
                          className="section-toggle"
                          onClick={() => toggleSection(conv.id, 'analysis')}
                        >
                          <div className="toggle-header">
                            <div className="toggle-icon">
                              <Sparkles size={20} />
                            </div>
                            <h4>Strengths & Improvements</h4>
                          </div>
                          {expandedSections[`${conv.id}-analysis`] ? (
                            <ChevronUp size={20} className="chevron" />
                          ) : (
                            <ChevronDown size={20} className="chevron" />
                          )}
                        </button>
                        {expandedSections[`${conv.id}-analysis`] && (
                          <div className="section-content">
                            {conv.evaluation.strengths && conv.evaluation.strengths.length > 0 && (
                              <div className="strengths">
                                <h5>
                                  <CheckCircle2 size={18} className="strength-icon" />
                                  Identified Strengths
                                </h5>
                                <ul>
                                  {conv.evaluation.strengths.map((strength, index) => (
                                    <li key={index}>{strength}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {conv.evaluation.missing_elements && conv.evaluation.missing_elements.length > 0 && (
                              <div className="improvements">
                                <h5>
                                  <Rocket size={18} className="improvement-icon" />
                                  Suggested Improvements
                                </h5>
                                <ul>
                                  {conv.evaluation.missing_elements.map((element, index) => (
                                    <li key={index}>{element}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </main>

      <footer className="footer">
        <p>© {new Date().getFullYear()} AI Answer Evaluator • Powered by Advanced LLM Technology</p>
      </footer>
    </div>
  );
}

export default App;