import React from 'react';

const QuestionnaireModal = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = React.useState({
    projectType: '',
    pages: '',
    references: '',
    description: '',
    researchQuestion: '',
    academicLevel: '',
    citationStyle: '',
    dataCollection: '',
    methodology: '',
    specificRequirements: '',
    keywords: ''
  });

  // Define your questions here - easy to update
  const questions = [
    {
      id: 'projectType',
      label: 'Project Type',
      type: 'select',
      required: true,
      options: [
        { value: '', label: 'Select project type' },
        { value: 'research', label: 'Research Paper' },
        { value: 'thesis', label: 'Thesis' },
        { value: 'dissertation', label: 'Dissertation' },
        { value: 'literature-review', label: 'Literature Review' },
        { value: 'case-study', label: 'Case Study' },
        { value: 'systematic-review', label: 'Systematic Review' },
        { value: 'other', label: 'Other' }
      ]
    },
    {
      id: 'academicLevel',
      label: 'Academic Level',
      type: 'select',
      required: true,
      options: [
        { value: '', label: 'Select academic level' },
        { value: 'undergraduate', label: 'Undergraduate' },
        { value: 'masters', label: 'Master\'s' },
        { value: 'phd', label: 'PhD/Doctoral' },
        { value: 'postdoc', label: 'Post-Doctoral' },
        { value: 'professional', label: 'Professional' }
      ]
    },
    {
      id: 'researchQuestion',
      label: 'Research Question/Objective',
      type: 'textarea',
      placeholder: 'What is the main research question or objective?',
      rows: 3,
      required: true
    },
    {
      id: 'description',
      label: 'Project Description',
      type: 'textarea',
      placeholder: 'Provide detailed description of your research topic, background, and scope...',
      rows: 5,
      required: true
    },
    {
      id: 'keywords',
      label: 'Keywords/Key Concepts',
      type: 'text',
      placeholder: 'e.g., climate change, machine learning, healthcare policy (comma-separated)',
      required: false
    },
    {
      id: 'methodology',
      label: 'Preferred Research Methodology',
      type: 'select',
      required: false,
      options: [
        { value: '', label: 'Select methodology (if applicable)' },
        { value: 'qualitative', label: 'Qualitative' },
        { value: 'quantitative', label: 'Quantitative' },
        { value: 'mixed', label: 'Mixed Methods' },
        { value: 'theoretical', label: 'Theoretical/Conceptual' },
        { value: 'experimental', label: 'Experimental' },
        { value: 'not-sure', label: 'Not Sure/Open to Suggestions' }
      ]
    },
    {
      id: 'dataCollection',
      label: 'Data Collection Preferences',
      type: 'select',
      required: false,
      options: [
        { value: '', label: 'Select data collection method (if applicable)' },
        { value: 'secondary', label: 'Secondary Data (existing sources)' },
        { value: 'primary', label: 'Primary Data (surveys, interviews, etc.)' },
        { value: 'both', label: 'Both Primary and Secondary' },
        { value: 'literature-only', label: 'Literature-Based Only' },
        { value: 'not-applicable', label: 'Not Applicable' }
      ]
    },
    {
      id: 'pages',
      label: 'Number of Pages',
      type: 'number',
      placeholder: 'Enter approximate number of pages',
      required: true
    },
    {
      id: 'references',
      label: 'Minimum Number of References',
      type: 'number',
      placeholder: 'Enter minimum number of references needed',
      required: false
    },
    {
      id: 'citationStyle',
      label: 'Citation Style',
      type: 'select',
      required: true,
      options: [
        { value: '', label: 'Select citation style' },
        { value: 'apa', label: 'APA (7th Edition)' },
        { value: 'mla', label: 'MLA' },
        { value: 'chicago', label: 'Chicago' },
        { value: 'harvard', label: 'Harvard' },
        { value: 'ieee', label: 'IEEE' },
        { value: 'vancouver', label: 'Vancouver' },
        { value: 'other', label: 'Other (specify in requirements)' }
      ]
    },
    {
      id: 'specificRequirements',
      label: 'Specific Requirements or Instructions',
      type: 'textarea',
      placeholder: 'Any specific formatting, structure, sources to include/exclude, or other special requirements...',
      rows: 4,
      required: false
    }
  ];

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      projectType: '',
      pages: '',
      references: '',
      description: '',
      researchQuestion: '',
      academicLevel: '',
      citationStyle: '',
      dataCollection: '',
      methodology: '',
      specificRequirements: '',
      keywords: ''
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content questionnaire-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Research Project Questionnaire</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          {questions.map((question) => (
            <div key={question.id} className="form-group">
              <label>
                {question.label}
                {question.required && <span className="required">*</span>}
              </label>
              
              {question.type === 'select' && (
                <select
                  name={question.id}
                  value={formData[question.id]}
                  onChange={handleInputChange}
                  required={question.required}
                >
                  {question.options.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}

              {question.type === 'textarea' && (
                <textarea
                  name={question.id}
                  placeholder={question.placeholder}
                  value={formData[question.id]}
                  onChange={handleInputChange}
                  rows={question.rows}
                  required={question.required}
                />
              )}

              {(question.type === 'text' || question.type === 'number' || question.type === 'date') && (
                <input
                  type={question.type}
                  name={question.id}
                  placeholder={question.placeholder}
                  value={formData[question.id]}
                  onChange={handleInputChange}
                  required={question.required}
                />
              )}
            </div>
          ))}

          <div className="modal-footer">
            <button type="button" className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="submit-button">
              Submit Research Request
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QuestionnaireModal;