import React from 'react';

const DocumentPreviewModal = ({ isOpen, onClose, document }) => {
  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Document Preview</h2>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default DocumentPreviewModal;