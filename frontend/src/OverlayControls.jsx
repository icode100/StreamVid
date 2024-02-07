import React from 'react';

const OverlayControl = ({ overlays, onOverlayChange }) => {
  return (
    <div className="overlay-controls">
      <h2>Overlays</h2>
      <ul>
        {overlays.map((overlay) => (
          <li key={overlay.id}>
            <span>{overlay.content}</span>
            <button onClick={() => onOverlayChange(overlay.id, 'DELETE')}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      <form onSubmit={(e) => {
        e.preventDefault();
        const content = e.target.content.value;
        onOverlayChange(null, 'ADD', { content });
      }}>
        <input type="text" name="content" placeholder="Enter overlay content" />
        <button type="submit">Add Overlay</button>
      </form>
    </div>
  );
};

export default OverlayControl;
